from numpy import log2
from lazylinop.butterfly import ksm
from lazylinop.butterfly.ksm import _multiple_ksm
from lazylinop.basicops import bitrev
from lazylinop.butterfly.dft import _dft_square_dyadic_ks_values
from lazylinop.wip.butterfly.fuses import fuses
from array_api_compat import array_namespace


def dft_helper(N: int, n_factors: int, interval: tuple = (0, None),
               backend: str = 'numpy', strategy: str = 'memory',
               dtype: str = 'complex64', device='cpu'):
    r"""
    Return a :class:`LazyLinOp` `L` corresponding to
    the Discrete-Fourier-Transform (DFT).

    Shape of ``L`` is $\left(N,~N\right)$ where
    $N=2^n$ must be a power of two.

    Args:
        N: ``int``
            DFT of size $N$. $N$ must be a power of two.
        n_factors: ``int``
            Number of factors ``n_factors <= n``.
            If ``n_factors = n``, return the square-dyadic decomposition.
            The performance of the algorithm depends on
            the number of factors, the size of the DFT
            as-well-as the strategy.
            Our experimentation shows that square-dyadic decomposition
            is always the worse choice.
            The best choice is two, three or four factors.
       interval: ``tuple``, optional
            Compute DFT on the interval ``(start, end)``.
            Default value is ``(0, None)`` and corresponds
            to the full DFT.
        backend: ``str``, ``tuple`` or ``pycuda.driver.Device``, optional
            See :py:func:`ksm` for more details.
        strategy: ``str``, optional
            See :py:func:`lazylinop.wip.butterfly.fuses.fuses`
            for more details.
        dtype: ``str``, optional
            It could be either ``'complex64'`` (default) or ``'complex128'``.

    Benchmark of our DFT implementation is
    (we use default hyper-parameters here):

    .. image:: _static/default_dft_batch_size512_complex64.svg

    Returns:
        :class:`LazyLinOp` `L` corresponding to the DFT.

    Examples:
        >>> import numpy as np
        >>> from lazylinop.wip.butterfly.dft import dft_helper
        >>> from lazylinop.signal import dft
        >>> # Butterfly decomposition with five factors.
        >>> n = 5
        >>> N = 2 ** n
        >>> x = np.random.randn(N)
        >>> y = dft_helper(N, n) @ x
        >>> z = dft(N) @ x
        >>> np.allclose(y, z)
        True
        >>> # Compute only the first half.
        >>> interval = (0, N // 2)
        >>> y = dft_helper(N, n, interval=interval) @ x
        >>> z = (dft(N) @ x)[np.arange(*interval)]
        >>> np.allclose(y, z)
        True

    .. seealso::
        - :py:func:`lazylinop.butterfly.fuse`,
        - :py:func:`lazylinop.wip.butterfly.fuses.fuses`.
    """
    if not (((N & (N - 1)) == 0) and N > 0):
        raise ValueError("N must be a power of two.")
    p = int(log2(N))
    if n_factors > p or n_factors < 1:
        raise Exception("n_factors must be positive and less or"
                        + " equal to int(np.log2(N)).")
    if 'complex' not in str(dtype):
        raise Exception("dtype must be either complex.")

    # FIXME
    params = None
    # if n_factors == ...:
    #     params = None
    # elif n_factors == ...:
    #     params = None
    # else:
    #     params = None

    ks_values = _dft_square_dyadic_ks_values(
        N, dtype=dtype, device=device)
    ksv = fuses(ks_values, n_factors, strategy)

    if not isinstance(interval, tuple) or (
            isinstance(interval, tuple) and len(interval) != 2):
        raise Exception("interval must be a tuple of two" +
                        " integers (start, end) or (start, None).")
    start = interval[0]
    end = N if interval[1] is None else interval[1]
    if start >= end:
        raise Exception("interval must satisfy start < end.")

    if start > 0 or end < N:
        # Select a, b and d according to interval argument.
        # By construction a is always equal to 1.
        # a * c * d is the number of columns that is left
        # unchanged after the slicing along the rows.
        # Therefore only b changes.
        a, b, c, d = ksv[0].shape
        assert a == 1
        # Modify start and end to left d unchanged.
        # At the end we will need another slicing.
        _start = d * (start // d)
        _end = d * (end // d + int(end % d != 0))
        xp = array_namespace(ksv[0])
        rows = xp.arange(_start, _end)
        i_a = rows // (b * d)
        i_b = xp.unique((rows - i_a * b * d) // d)
        ksv[0] = ksv[0][:, i_b, :, :]
    else:
        _start, _end = start, end

    if backend in ('cupy', 'numpy', 'pytorch', 'scipy', 'xp'):
        L = ksm(ksv, backend=backend) @ bitrev(2 ** p)
    else:
        L = _multiple_ksm(ksv, backend=backend,
                          params=params, perm=True)
    L.ks_values = ksv
    if start == _start and end == _end:
        # No modifications of start and end.
        # Therefore, no need to slice again along the rows.
        return L
    else:
        return L[(start - _start):(end - _start), :]
