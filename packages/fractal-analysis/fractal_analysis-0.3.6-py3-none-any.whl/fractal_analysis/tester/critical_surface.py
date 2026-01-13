import functools
import math
from abc import ABC, abstractmethod
from typing import Union, List

import numpy as np
from numpy import linalg
from scipy.linalg import sqrtm


class CriticalSurfaceBrownianMotion(ABC):
    """
        alpha: significance level (look at quantiles of order alpha/2 and 1 − alpha/2)
    """

    def __init__(self,
                 N: int,
                 alpha: float = 0.05,
                 k: int = 1,
                 chi2_trials: int = 100000,
                 is_increment_series: bool = False):
        self.N = N
        self.alpha = alpha
        self.k = k
        np.random.seed(6)
        self.chi2 = np.random.chisquare(df=1, size=(self.N, chi2_trials))
        np.random.seed()
        self.is_increment_series = is_increment_series

    @functools.cached_property
    def matrix_A_k(self):
        if self.k == 0:
            A_k = np.diag(np.ones(4) / self.N)
        else:
            A_k = np.zeros((self.N, self.N))
            for i in range(self.N):
                for j in range(self.N):
                    if abs(i - j) == self.k:
                        A_k[i, j] = 0.5 / (self.N - self.k)
        return A_k

    def _add_on_sig2_matrix(self, add_on_sig2: float):
        add_on_sig2_matrix = np.zeros((self.N, self.N))
        for i in range(self.N):
            for j in range(i, self.N):
                k = j - i
                if k == 0:
                    add_on_sig2_matrix[i, j] = 2 * add_on_sig2
                    add_on_sig2_matrix[j, i] = 2 * add_on_sig2
                if k == 1:
                    add_on_sig2_matrix[i, j] = - add_on_sig2
                    add_on_sig2_matrix[j, i] = - add_on_sig2
        return add_on_sig2_matrix

    @abstractmethod
    def _autocovariance_matrix_increment(self, sig2: float, H: Union[List[float], np.ndarray, float],
                                         add_on_sig2: float):
        pass

    @abstractmethod
    def _autocovariance_matrix(self, sig2: float, H: Union[List[float], np.ndarray, float], add_on_sig2: float):
        pass

    def _eigenvalues(self, sig2: float, H: Union[List[float], np.ndarray, float], add_on_sig2: float):
        if self.is_increment_series:
            Sigma: np.ndarray = self._autocovariance_matrix_increment(sig2=sig2, H=H, add_on_sig2=add_on_sig2)
        else:
            Sigma: np.ndarray = self._autocovariance_matrix(sig2=sig2, H=H, add_on_sig2=add_on_sig2)
        square_root_Sigma = sqrtm(Sigma)
        square_root_Sigma = np.real(square_root_Sigma)
        A_k = self.matrix_A_k
        mat = square_root_Sigma.dot(A_k)
        mat = mat.dot(square_root_Sigma)
        eigenvalues, _ = linalg.eig(mat)
        eigenvalues = np.real(eigenvalues)
        return eigenvalues

    def _generalized_chi2(self, sig2, H: Union[List[float], np.ndarray, float], add_on_sig2: float):
        eigenvalues = self._eigenvalues(sig2=sig2, H=H, add_on_sig2=add_on_sig2)
        stat = np.array(eigenvalues.dot(self.chi2))
        return stat

    def quantile(self, sig2, H: Union[List[float], np.ndarray, float], add_on_sig2: float = 0):
        dist = self._generalized_chi2(sig2=sig2, H=H, add_on_sig2=add_on_sig2)
        quantile = [0, 0]
        quantile[0] = np.quantile(a=dist, q=self.alpha / 2)
        quantile[1] = np.quantile(a=dist, q=1 - self.alpha / 2)
        return quantile


class CriticalSurfaceFBM(CriticalSurfaceBrownianMotion):
    """
        Source paper: Michał Balcerek, Krzysztof Burnecki. (2020)
                      Testing of fractional Brownian motion in a noisy environment.
                      Chaos, Solitons & Fractals, Volume 140, 110097.
                      https://doi.org/10.1016/j.chaos.2020.110097
    """

    def _autocovariance_matrix(self, sig2: float, H: float, add_on_sig2: float):
        # raise ValueError("No non increment version exists, use is_increment_series=True for FBM testing.")
        if not isinstance(H, (float, int)) or H > 1 or H < 0:
            raise ValueError(f'H is {H}, but it needs to be a float in [0,1].')
        Sigma = np.zeros((self.N, self.N))
        twoH = 2 * H
        for i in range(self.N):
            for j in range(i, self.N):
                t = (i + 1) / self.N
                s = (j + 1) / self.N
                sigma = 0.5 * (t ** twoH + s ** twoH - abs(t - s) ** twoH)  # todo: /self.N
                Sigma[i, j] = sigma
                if i != j:
                    Sigma[j, i] = sigma
        return sig2 * Sigma + self._add_on_sig2_matrix(add_on_sig2=add_on_sig2)

    def _autocovariance_matrix_increment(self, sig2: float, add_on_sig2: float, H: float):
        if not isinstance(H, (float, int)) or H > 1 or H < 0:
            raise ValueError(f'H is {H}, but it needs to be a float in [0,1].')
        Sigma = np.zeros((self.N, self.N))
        twoH = 2 * H
        for i in range(self.N):
            for j in range(i, self.N):
                k = abs(i - j)
                t_k_plus_one = (k + 1) / self.N
                t_k_minus_one = (k - 1) / self.N
                t_k = k / self.N
                sigma = 0.5 * (t_k_plus_one ** twoH + abs(t_k_minus_one) ** twoH - 2 * t_k ** twoH)  # todo: /self.N
                Sigma[i, j] = sigma
                if i != j:
                    Sigma[j, i] = sigma
        return sig2 * Sigma + self._add_on_sig2_matrix(add_on_sig2=add_on_sig2)


class CriticalSurfaceMFBM(CriticalSurfaceBrownianMotion):
    """
        Source paper: Balcerek, Michał, and Krzysztof Burnecki. (2020) Testing of Multifractional Brownian Motion.
                          Entropy 22, no. 12: 1403.
                          https://doi.org/10.3390/e22121403
    """

    @functools.lru_cache(maxsize=128)
    def _D(self, x: float, y: float):
        gam_xy = math.gamma(x + y + 1)
        gam_x = math.gamma(2 * x + 1)
        gam_y = math.gamma(2 * y + 1)
        sin_xy = math.sin(math.pi * (x + y) / 2)
        sin_x = math.sin(math.pi * x)
        sin_y = math.sin(math.pi * y)
        return math.sqrt(gam_x * gam_y * sin_x * sin_y) / 2 / gam_xy / sin_xy

    def _autocovariance_matrix(self, sig2: float, H: Union[List, np.ndarray], add_on_sig2: float, delta_i: int = 0,
                               delta_j: int = 0):
        Sigma = np.zeros((self.N, self.N))
        for i in range(self.N):
            for j in range(i, self.N):
                ht_idx = min(self.N - 1, i + delta_i)
                hs_idx = min(self.N - 1, j + delta_j)
                ht = H[ht_idx]
                hs = H[hs_idx]
                hths = ht + hs
                D = self._D(x=ht, y=hs)
                # sigma = D * ((i + delta_t + 1) ** h + (j + delta_s + 1) ** h - abs(i + delta_t - j - delta_s) ** h)
                t = (i + delta_i + 1) / self.N
                s = (j + delta_j + 1) / self.N
                sigma = D * (t ** hths + s ** hths - abs(t - s) ** hths)  # todo: /self.N
                Sigma[i, j] = sigma
                if i != j:
                    Sigma[j, i] = sigma
        return sig2 * Sigma + self._add_on_sig2_matrix(add_on_sig2=add_on_sig2)

    def _autocovariance_matrix_increment(self, sig2: float, H: Union[List, np.ndarray], add_on_sig2: float):
        if isinstance(H, (float, int)):
            raise ValueError('H needs to be a list for MBM.')
        cov_t1_s1 = self._autocovariance_matrix(delta_i=1, delta_j=1, H=H, sig2=1, add_on_sig2=0)
        cov_t1_s0 = self._autocovariance_matrix(delta_i=1, delta_j=0, H=H, sig2=1, add_on_sig2=0)
        cov_t0_s1 = self._autocovariance_matrix(delta_i=0, delta_j=1, H=H, sig2=1, add_on_sig2=0)
        cov_t0_s0 = self._autocovariance_matrix(delta_i=0, delta_j=0, H=H, sig2=1, add_on_sig2=0)
        cov_inc = cov_t1_s1 - cov_t1_s0 - cov_t0_s1 + cov_t0_s0
        return sig2 * cov_inc + self._add_on_sig2_matrix(add_on_sig2=add_on_sig2)
