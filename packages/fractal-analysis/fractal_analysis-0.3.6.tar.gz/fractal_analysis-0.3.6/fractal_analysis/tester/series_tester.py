from typing import Union, List

import numpy as np
import pandas as pd

from fractal_analysis.tester.critical_surface import CriticalSurfaceBrownianMotion, CriticalSurfaceFBM, \
    CriticalSurfaceMFBM
from fractal_analysis.tester.estimate_sigma import EstimateSigma


class SeriesTester:
    def __init__(self,
                 critical_surface: CriticalSurfaceBrownianMotion,
                 is_cache_stat=False,
                 is_cache_quantile=False):
        """
        is_cache_stat: allow cache variable stat, set to True if x is unchanged
        is_cache_quantile: allow cache variable quantile, set to True if sig2 and h are unchanged
        """
        self.critical_surface = critical_surface
        self.is_cache_stat = is_cache_stat
        self.is_cache_quantile = is_cache_quantile
        self._old_series = None
        self._old_h = None
        self._old_sig2 = None
        self._stat = None
        self._quantile = None

    def test(self, x: Union[List, np.ndarray, pd.Series], h: Union[float, List, np.ndarray, pd.Series],
             add_on_sig2: float = 0, sig2: float = None):
        """
            x: series to test
            h: holder exponent, same length as x if test MBM, float in (0,1) if test FBM
            sig2: sigma square, if None, use auto-estimated sigma
            add_on_sig2: add on noise
        """
        if self.critical_surface.is_increment_series:
            series = np.diff(x, prepend=0)
        else:
            series = np.array(x)
        if isinstance(self.critical_surface, CriticalSurfaceFBM):
            if not isinstance(h, (float, int)):
                raise ValueError("h must be float for FBM tester.")
            else:
                h_series = np.ones(len(series)) * h
        elif isinstance(self.critical_surface, CriticalSurfaceMFBM):
            if isinstance(h, float):
                raise ValueError("h must be array-like for MBM tester.")
            elif isinstance(h, (List, np.ndarray, pd.Series)):
                h_series = np.array(h)
                if len(h_series) != len(series):
                    raise ValueError('h and x should have the same length for MBM tester.')
            else:
                raise ValueError("h must be List or np.ndarray or pd.Series for MBM tester.")
        else:
            raise ValueError("Critical surface type is not found.")
        if self.is_cache_stat and np.array_equal(series, self._old_series):
            stat = self._stat
        else:
            stat = np.dot(series.T.dot(self.critical_surface.matrix_A_k), series)
            if self.is_cache_stat:
                self._old_series = series
                self._stat = stat
        if sig2 is None:
            sig2 = EstimateSigma(series=series, h_series=h_series).theta_hat_square
        if self.is_cache_quantile and np.array_equal(sig2, self._old_sig2) and np.array_equal(h, self._old_h):
            quantile = self._quantile
        else:
            if isinstance(h, pd.Series):
                h = np.array(h)
            quantile = self.critical_surface.quantile(sig2=sig2, H=h, add_on_sig2=add_on_sig2)
            if self.is_cache_quantile:
                self._old_h = h
                self._old_sig2 = sig2
                self._quantile = quantile
        low = quantile[0]
        up = quantile[1]
        if low <= stat <= up:
            ret = True
        else:
            ret = False
        return ret, sig2


class MBMSeriesTester(SeriesTester):
    """
        Source paper: Balcerek, Michał, and Krzysztof Burnecki. (2020) Testing of Multifractional Brownian Motion.
                      Entropy 22, no. 12: 1403.
                      https://doi.org/10.3390/e22121403
    """

    def __init__(self, critical_surface: CriticalSurfaceMFBM, is_cache_stat=False, is_cache_quantile=False):
        super().__init__(critical_surface=critical_surface,
                         is_cache_stat=is_cache_stat,
                         is_cache_quantile=is_cache_quantile)


class FBMSeriesTester(SeriesTester):
    """
        Source paper: Michał Balcerek, Krzysztof Burnecki. (2020)
                      Testing of fractional Brownian motion in a noisy environment.
                      Chaos, Solitons & Fractals, Volume 140, 110097.
                      https://doi.org/10.1016/j.chaos.2020.110097
        Note: this class implements Algorithm 1 of the paper.
              can use an auto-estimated sigma.
    """

    def __init__(self, critical_surface: CriticalSurfaceFBM, is_cache_stat=False, is_cache_quantile=False):
        super().__init__(critical_surface=critical_surface,
                         is_cache_stat=is_cache_stat,
                         is_cache_quantile=is_cache_quantile)
