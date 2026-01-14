from lazylinop.signal.dst import _dst_helper
from lazylinop.wip.butterfly.dft import dft_helper


def dst_helper(N: int, n_factors: int, type: int = 2,
               backend: str = 'xp', strategy: str = 'memory',
               dtype: str = 'complex128', device='cpu'):
    r"""
    Returns a :class:`.LazyLinOp` ```L`` for the Direct Sine Transform (DST).

    Shape of ``L`` is $\left(N,~N\right)$ where
    $N=2^n$ must be a power of two except for DST I (see below).

    ``L`` is orthonormal, and the :class:`.LazyLinOp`
    for the inverse DST is ``L.T``.

    Args:
        N: ``int``
            Size of the input (N > 0).

            $N$ must be:

            - a power of two for DCT II, III and IV.
            - a power of two minus one for DCT I.
        n_factors: ``int``
            Number of factors ``n_factors <= n``.
            If ``n_factors = n``, return the square-dyadic decomposition.
            The performance of the algorithm depends on
            the number of factors, the size of the underlying DFT
            as-well-as the strategy.
            Our experimentation shows that square-dyadic decomposition
            is always the worse choice.
            The best choice is two, three or four factors.
        type: ``int``, optional
            1, 2, 3, 4 (I, II, III, IV).
            Defaut is 2.
            See `SciPy DST <https://docs.scipy.org/doc/scipy/
            reference/generated/
            scipy.fft.dst.html#scipy-fft-dst>`_ and
            `CuPy DST <https://docs.cupy.dev/en/latest/reference/
            generated/cupyx.scipy.fft.dst.html>`_ for more details.
        backend: ``str``, ``tuple`` or ``pycuda.driver.Device``, optional
            See :py:func:`ksm` for more details.
        strategy: ``str``, optional
            See :py:func:`lazylinop.wip.butterfly.fuses.fuses`
            for more details.
        dtype: ``str``, optional
            dtype of the underlying DFT ``ks_values``.
            It could be either ``'complex64'`` or ``'complex128'`` (default).

    Returns:
        :class:`.LazyLinOp`

    Example:
        >>> from lazylinop.wip.butterfly.dst import dst_helper
        >>> from scipy.fft import dst as sp_dst
        >>> import numpy as np
        >>> N = 32
        >>> x = np.random.randn(N)
        >>> F = dst_helper(N, 2)
               ['0', '1', '2', '3', '4', '5', '6']
        step=0 ['01', '2', '3', '4', '5', '6']
        step=1 ['01', '2', '3', '4', '56']
        step=2 ['01', '23', '4', '56']
        step=3 ['01', '23', '456']
        step=4 ['0123', '456']
        >>> y = F @ x
        >>> np.allclose(y, sp_dst(x, norm='ortho'))
        True
        >>> # compute the inverse DST
        >>> x_ = F.T @ y
        >>> np.allclose(x_, x)
        True

    .. seealso::
        - `DST (Wikipedia) <https://en.wikipedia.org/
          wiki/Discrete_sine_transform>`_,
        - `SciPy DST <https://docs.scipy.org/doc/scipy/
          reference/generated/ scipy.fft.dst.html>`_,
        - `SciPy inverse DST <https://docs.scipy.org/doc/scipy/
          reference/generated/scipy.fft.idst.html>`_,
        - `CuPy DST <https://docs.cupy.dev/en/latest/reference/
          generated/cupyx.scipy.fft.dst.html>`_,
        - :py:func:`lazylinop.signal.dct`.
        - :py:func:`lazylinop.signal.dst`,
        - :py:func:`lazylinop.wip.butterfly.dct`.
    """

    if type == 1:
        if N <= 1:
            raise Exception("DST I: N must be > 1.")
        p, _N = 0, N + 1
        while _N >> 1 != 0:
            p += 1
            _N >>= 1
        if (N + 1) != 2 ** p:
            raise Exception("DST I: size of the input plus one" +
                            "  must be a power of two.")

    def fft_fn(N):
        return dft_helper(N, n_factors, backend=backend,
                          strategy=strategy, dtype=dtype, device=device)

    return _dst_helper(N, type, None, 'ortho', None, True, None, fft_fn)
