from typing import Union, List

import numpy as np
import pandas as pd
import math


class IrHurstEstimator:
    """
        Source paper: Bardet, Jean-Marc & Surgailis, Donatas, 2013.
                      "Nonparametric estimation of the local Hurst function of multifractional Gaussian processes,"
                      Stochastic Processes and their Applications, Elsevier, vol. 123(3), pages 1004-1045.
        Original Matlab code source: http://samm.univ-paris1.fr/Sofwares-Logiciels
                                     Software for estimating the Hurst function H of a Multifractional Brownian Motion:
                                     Quadratic Variation estimator and IR estimator
    """

    def __init__(self, mbm_series: Union[List, np.ndarray, pd.Series], alpha: float):
        """
            mbm_series: multifractional Brownian motion series
            alpha: decide how many observations on mbm_series is used to estimate a point of the holder exponent;
                   small alpha means more observations are used for a single point and therefore the variance is small.
        """
        self.mbm_series = np.array(mbm_series)
        self.alpha = alpha
        if not (0 < self.alpha < 1):
            raise ValueError(f'Alpha must be in range (0, 1).')
        self.n = len(self.mbm_series)

    @staticmethod
    def _ismember(a, b):
        bind = {}
        for i, elt in enumerate(b):
            if elt not in bind:
                bind[elt] = i
        return [bind.get(itm, None) for itm in a]  # None can be replaced by any other "not in b" value

    def _neighborhood(self, t: int, step: int = 1):
        """
            The function $\mathcal{V}_{n,\alpha}(t)$ in Sec 2.1 of the source paper:
                      Bardet, Jean-Marc & Surgailis, Donatas, 2013.
                      "Nonparametric estimation of the local Hurst function of multifractional Gaussian processes,"
                      Stochastic Processes and their Applications, Elsevier, vol. 123(3), pages 1004-1045.
        """
        n_to_1_minus_alpha = self.n ** (1 - self.alpha)
        k_min = max(0.0, math.ceil(t - n_to_1_minus_alpha))  # the pdep in matlab code
        k_max = min(float(self.n - 3 - 2), math.floor(t + n_to_1_minus_alpha))  # the pfin in matlab code
        return np.arange(start=k_min, stop=k_max + 1, step=step, dtype=int)

    @staticmethod
    def _hest_ir(R, p: int):
        """
            Equivalent to matlab function HestIR(R,p) in the source code:
                        http://samm.univ-paris1.fr/Sofwares-Logiciels
                        Software for estimating the Hurst function H of a Multifractional Brownian Motion:
                        Quadratic Variation estimator and IR estimator
            This is $\Lambda_2^{-1}(H)$ (inverse function of eq. 2.5) in the paper:
                        Bardet, Jean-Marc & Surgailis, Donatas, 2013.
                        "Nonparametric estimation of the local Hurst function of multifractional Gaussian processes,"
                        Stochastic Processes and their Applications, Elsevier, vol. 123(3), pages 1004-1045.
        """
        start = 0.0001
        stop = 0.9999
        step = 0.0001
        H = np.arange(start, stop + step, step)
        if p == 1:
            r = 2 ** (2 * H - 1) - 1
        elif p == 2:
            r = (-3 ** (2 * H) + 2 ** (2 * H + 2) - 7) / (8 - 2 ** (2 * H + 1))
        else:
            raise ValueError('p is the order of the IR statistic; only takes 1 or 2.')
        lam = 1 / np.pi * np.arccos(-r) + np.sqrt(1 - r ** 2) / (np.pi * (1 - r)) * np.log(2 / (r + 1))
        return sum(R > i for i in lam) / 10000

    @property
    def holder_exponents(self):
        mgn_series = self.mbm_series[1:] - self.mbm_series[:-1]
        ir_estimates = []
        for t in range(self.n):
            k = self._neighborhood(t=t)
            R2 = np.mean(np.abs(mgn_series[3 + k] - mgn_series[1 + k]) / (
                    np.abs(mgn_series[3 + k] - mgn_series[2 + k]) + np.abs(mgn_series[2 + k] - mgn_series[1 + k])))
            ir_estimates.append(self._hest_ir(R=R2, p=2))
        return np.array(ir_estimates)


class QvHurstEstimator(IrHurstEstimator):
    """
        Source paper: Bardet, Jean-Marc & Surgailis, Donatas, 2013.
                      "Nonparametric estimation of the local Hurst function of multifractional Gaussian processes,"
                      Stochastic Processes and their Applications, Elsevier, vol. 123(3), pages 1004-1045.
        Original Matlab code source: http://samm.univ-paris1.fr/Sofwares-Logiciels
                                     Software for estimating the Hurst function H of a Multifractional Brownian Motion:
                                     Quadratic Variation estimator and IR estimator
    """

    def __init__(self, mbm_series: Union[List, np.ndarray, pd.Series], alpha: float, p: int = 5):
        """
            mbm_series: multifractional Brownian motion series
            alpha: decide how many observations on mbm_series is used to estimate a point of the holder exponent;
                   small alpha means more observations are used for a single point and therefore the variance is small.
            p: the number of dilatations of QV estimates and it is 5 according to the paper.
        """
        super().__init__(mbm_series=mbm_series, alpha=alpha)
        self.p = p

    def _neighborhood(self, t: int, step: int = 1):
        """
            Modified (for QV) function $\mathcal{V}_{n,\alpha}(t)$ in Sec 2.1 of the source paper:
                      Bardet, Jean-Marc & Surgailis, Donatas, 2013.
                      "Nonparametric estimation of the local Hurst function of multifractional Gaussian processes,"
                      Stochastic Processes and their Applications, Elsevier, vol. 123(3), pages 1004-1045.
        """
        n_to_1_minus_alpha = self.n ** (1 - self.alpha)
        k_min = max(0.0, math.ceil(t - n_to_1_minus_alpha))  # the pdep in matlab code
        k_max = min(float(self.n - 11), math.floor(t + n_to_1_minus_alpha))  # the pfin in matlab code
        return np.arange(start=k_min, stop=k_max + 1, step=step, dtype=int)

    def _get_S(self, t):
        """
            Eq (2.7): i=1,...self.p
        """
        k = self._neighborhood(t=t, step=1)  # the matlab code uses a neighborhood of every i steps, here we use step=1
        S_lst = []
        for i in range(1, self.p + 1):
            S_lst.append(np.mean((self.mbm_series[2 * i + k] - 2 * self.mbm_series[i + k] + self.mbm_series[k]) ** 2))
        return np.array(S_lst)

    @staticmethod
    def _get_A(p: int = 5):
        log_lst = np.log(range(1, p + 1))
        mean_log_lst = np.mean(log_lst)
        return log_lst - mean_log_lst

    @property
    def holder_exponents(self):
        A_lst = self._get_A()
        AAT = np.dot(A_lst, A_lst.T)
        A_over_AAT_over2 = A_lst / 2 / AAT
        qv_estimates = []
        for t in range(self.n):
            log_S_lst = np.log(self._get_S(t=t))
            qv_estimates.append(np.dot(A_over_AAT_over2, log_S_lst))
        return np.array(qv_estimates)
