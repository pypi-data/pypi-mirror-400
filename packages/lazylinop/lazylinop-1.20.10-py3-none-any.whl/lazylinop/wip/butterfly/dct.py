from numpy import log2
from lazylinop.signal.dct import _dct_helper
from lazylinop.wip.butterfly.dft import dft_helper


def dct_helper(N: int, n_factors: int, type: int = 2,
               backend: str = 'xp', strategy: str = 'memory',
               dtype: str = 'complex128', device='cpu'):
    r"""
    Returns a :class:`.LazyLinOp` ```L`` for the Direct Cosine Transform (DCT).

    Shape of ``L`` is $\left(N,~N\right)$ where
    $N=2^n$ must be a power of two except for DCT I (see below).

    ``L`` is orthonormal, and the :class:`.LazyLinOp`
    for the inverse DCT is ``L.T``.

    Args:
        N: ``int``
            Size of the input (N > 0).
            $N$ must be:

            - a power of two for DCT II, III and IV.
            - a power of two plus one for DCT I.
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
            See `SciPy DCT <https://docs.scipy.org/doc/scipy/
            reference/generated/
            scipy.fft.dct.html#scipy-fft-dct>`_ and
            `CuPy DCT <https://docs.cupy.dev/en/latest/reference/
            generated/cupyx.scipy.fft.dct.html>`_ for more details.
        backend: ``str``, ``tuple`` or ``pycuda.driver.Device``, optional
            See :py:func:`ksm` for more details.
        strategy: ``str``, optional
            See :py:func:`lazylinop.wip.butterfly.fuses.fuses`
            for more details.
        dtype: ``str``, optional
            dtype of the underlying DFT ``ks_values``.
            It could be either ``'complex64'`` (default) or ``'complex128'``.

    Returns:
        :class:`.LazyLinOp`

    Example:
        >>> from lazylinop.wip.butterfly.dct import dct_helper
        >>> from scipy.fft import dct as sp_dct
        >>> import numpy as np
        >>> N = 32
        >>> x = np.random.randn(N)
        >>> F = dct_helper(N, 2)
               ['0', '1', '2', '3', '4', '5', '6']
        step=0 ['01', '2', '3', '4', '5', '6']
        step=1 ['01', '2', '3', '4', '56']
        step=2 ['01', '23', '4', '56']
        step=3 ['01', '23', '456']
        step=4 ['0123', '456']
        >>> y = F @ x
        >>> np.allclose(y, sp_dct(x, norm='ortho'))
        True
        >>> # compute the inverse DCT
        >>> x_ = F.T @ y
        >>> np.allclose(x_, x)
        True
        >>> # To mimick SciPy DCT II norm='ortho' and orthogonalize=False
        >>> from lazylinop.basicops import diag
        >>> v = np.full(N, 1.0)
        >>> v[0] = np.sqrt(2.0)
        >>> y = diag(v) @ F @ x
        >>> z = sp_dct(x, 2, N, 0, 'ortho', False, 1, orthogonalize=False)
        >>> np.allclose(y, z)
        True

    References:
        [1] A Fast Cosine Transform in One and Two Dimensions,
            by J. Makhoul, `IEEE Transactions on acoustics,
            speech and signal processing` vol. 28(1), pp. 27-34,
            :doi:`10.1109/TASSP.1980.1163351` (1980).

    .. seealso::
        - `DCT (Wikipedia) <https://en.wikipedia.org/
          wiki/Discrete_cosine_transform>`_,
        - `SciPy DCT <https://docs.scipy.org/doc/scipy/
          reference/generated/ scipy.fft.dct.html#scipy-fft-dct>`_,
        - `SciPy inverse DCT <https://docs.scipy.org/doc/scipy/
          reference/generated/ scipy.fft.idct.html#scipy-fft-idct>`_,
        - `CuPy DCT <https://docs.cupy.dev/en/latest/reference/
          generated/cupyx.scipy.fft.dct.html>`_,
        - :py:func:`lazylinop.signal.dct`.
        - :py:func:`lazylinop.signal.dst`,
        - :py:func:`lazylinop.wip.butterfly.dst`.
    """

    if type == 1:
        if N < 2:
            raise Exception("DCT I: size of the input must be >= 2.")
        p, _N = 0, N - 1
        while _N >> 1 != 0:
            p += 1
            _N >>= 1
        if (N - 1) != 2 ** p:
            raise Exception("DCT I: size of the input minus one" +
                            " must be a power of two.")

    def fft_fn(N):
        return dft_helper(N, n_factors, backend=backend,
                          strategy=strategy, dtype=dtype, device=device)

    return _dct_helper(N, type, None, 'ortho', None, True, None, fft_fn)
