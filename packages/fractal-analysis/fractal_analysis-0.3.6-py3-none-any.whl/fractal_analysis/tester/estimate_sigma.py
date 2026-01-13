import cmath
import math
from typing import Union, List

import numpy as np
from scipy import integrate


class EstimateSigma:
    """
        Source paper: Ayache A., Peng Q. (2012) Stochastic Volatility and Multifractional Brownian Motion.
                      In: Zili M., Filatova D. (eds) Stochastic Differential Equations and Processes.
                      Springer Proceedings in Mathematics, vol 7. Springer, Berlin, Heidelberg.
                      https://doi.org/10.1007/978-3-642-22368-6_6
        Note: this class implements the estimator of sigma in Theorem 2.3 of the paper.
    """

    def __init__(self,
                 series: Union[List, np.ndarray],
                 h_series: Union[List, np.ndarray]):
        self.Y = [item ** 2 for item in series]  # Y is series square, p4 eq10
        self.n = len(series) - 1  # N=n  p5 line1
        self.h_series = h_series
        if len(self.h_series) != len(series):
            raise ValueError('h series and series should have the same length.')

    def C_integrant(self, eta: float, s: int):
        exp_ = cmath.exp(complex(imag=eta)) - 1
        exp_norm_sqr = exp_.real ** 2 + exp_.imag ** 2
        integrant = exp_norm_sqr ** 2 / abs(eta) ** (2 * self.h_series[s] + 3)
        return integrant

    def C(self, s: int, tol=1e-3):  # p7 eq22
        limit = 50
        max_ = 5
        text = None
        for i in range(max_):
            ret = integrate.quad(self.C_integrant, -np.inf, 0, args=(s,), limit=limit, full_output=1)
            ret = ret + integrate.quad(self.C_integrant, 0, np.inf, args=(s,), limit=limit, full_output=1)
            if ret[1] <= tol:
                return ret[0], text
            limit += 50
        text = f'Bad auto sigma square calculated with error {ret[1]}. Suggest to give sigma square and rerun.'
        return ret[0], text

    @property
    def V_bar(self):
        """
        p6 thm2.1 eq20
        h==1
        """
        text = None
        sum_ = 0
        for i in range(self.n - 1):
            C, text = self.C(s=i)
            sum_ += (self.Y[i + 1] - self.Y[i]) ** 2 / C / self.n ** (
                    -2 * self.h_series[i])
        if text:
            print(text)
        return sum_ / self.n

    @property
    def theta_hat_square(self):
        return self.V_bar * self.n / 2 / math.sqrt(math.log(self.n)) / sum(self.Y)
