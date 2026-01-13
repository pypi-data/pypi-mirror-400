import numpy as np
import scipy

from fractal_analysis.simulator.dpw.dpw_fractal_simulator import DpwNegFbmSimulator
from fractal_analysis.simulator.wood_chan.wood_chan_multi_fractal_simulator import MultiFractalBaseSimulator


class DpwMbmSimulator(MultiFractalBaseSimulator):
    """
        Main idea: generates a Multi-fractional Brownian Motion (mBm) using DPW
                   Lamperti Transformation, some krigging and a prequantification.
        Reference: Y. Ding, Q. Peng, W. Wu "A General Method for Simulating H-self-similar Processes.". # todo: add source link
    """

    def __init__(self, sample_size: int, holder_exponents: np.ndarray, pre_quant_level: int = 10,
                 lamperti_multiplier: int = 5, tmax: float = 1, std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            holder_exponents: is a list of real value in (0:1); it allows to model a process the pointwise regularity of which varies in time.
            pre_quant_level: levels for the pre-quantification.
            lamperti_multiplier: an integer used for Lamperti transform; bigger value (usually <=10) provides more accuracy; default value is 5
            tmax: generates series using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates series using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """
        super().__init__(sample_size=sample_size, holder_exponents=holder_exponents, pre_quant_level=pre_quant_level,
                         tmax=tmax, std_const=std_const)
        if not isinstance(lamperti_multiplier, int) and lamperti_multiplier <= 0:
            raise ValueError(f'lamperti_multiplier must be a positive integer.')
        self.lamperti_multiplier = lamperti_multiplier

    def get_fractal_base_func(self, mean: float, seed: int):
        neg_fbm_simulator = DpwNegFbmSimulator(sample_size=self.sample_size, hurst_parameter=mean, tmax=self.tmax,
                                                std_const=self.std_const, lamperti_multiplier=self.lamperti_multiplier)
        return neg_fbm_simulator.get_neg_fbm(seed=seed)

    @staticmethod
    def neg_fbm_covariance_func(t, s, h1, h2):
        # todo: combine with dpw_fractal_simulator.DpwNegFbmSimulator.neg_fbm_covariance_func
        """
            Covariance function of two paths using DPW Lamperti transformation
            on the negative part of mBm simulation. Corresponding matlab func: covm.m
            t : time index of path 1
            s : time index of path 2, assume t>s
            h1 : H function corresponding to time index of path 1
            h2 : H function corresponding to time index of path 2
        """
        if t != s:
            numerator = scipy.special.gamma(h1 + 0.5) * scipy.special.gamma(h2 + 0.5) * (
                    abs(t) ** (h1 + h2) + abs(s) ** (h1 + h2) - abs(t - s) ** (h1 + h2))
            denominator = 2 * scipy.special.gamma(h1 + h2 + 1) * np.sin((h1 + h2) * np.pi / 2)
            term = -s * (t ** (h1 - 1 / 2)) * (s ** (h2 - 1 / 2)) / (h2 + 1 / 2)
            summ = scipy.special.hyp2f1(0.5 - h1, 1, h2 + 3 / 2, s / t)
            cov = numerator / denominator + term * summ
        else:
            num = (scipy.special.gamma(h1 + 1 / 2) ** 2) * abs(t) ** (2 * h1)
            de = scipy.special.gamma(2 * h1 + 1) * np.sin(h1 * np.pi)
            cov = num / de - (t ** (2 * h1)) / (2 * h1)
        return cov

    def fractal_cov_matrix(self, i, hu_, hu1_, holder_exponent, means, f_lst=None, q_lst=None):
        """
            Covariance matrix of neg fbm under Lamperti transformation
        """
        t = (i + 1) / self.sample_size
        tau = 1 / self.sample_size
        num1 = means[hu_]
        num2 = means[hu1_]
        b1 = [self.neg_fbm_covariance_func(t, t - tau, holder_exponent, num1),
              self.neg_fbm_covariance_func(t, t, holder_exponent, num1),
              self.neg_fbm_covariance_func(t + tau, t, num1, holder_exponent)]
        b2 = [self.neg_fbm_covariance_func(t, t - tau, holder_exponent, num2),
              self.neg_fbm_covariance_func(t, t, holder_exponent, num2),
              self.neg_fbm_covariance_func(t + tau, t, num2, holder_exponent)]
        b = np.concatenate([b1, b2])

        def helper_func(x1, x2):
            ret = [[self.neg_fbm_covariance_func(t - tau, t - tau, x1, x2),
                    self.neg_fbm_covariance_func(t, t - tau, x1, x2),
                    self.neg_fbm_covariance_func(t + tau, t - tau, x1, x2)],
                   [0, self.neg_fbm_covariance_func(t, t, x1, x2),
                    self.neg_fbm_covariance_func(t + tau, t, x1, x2)],
                   [0, 0, self.neg_fbm_covariance_func(t + tau, t + tau, x1, x2)]]
            for i in range(len(ret)):
                for j in range(i + 1, len(ret)):
                    ret[j][i] = ret[i][j]
            return ret

        A = helper_func(x1=num1, x2=num1)
        B = helper_func(x1=num2, x2=num2)
        C = [[self.neg_fbm_covariance_func(t - tau, t - tau, num1, num2),
              self.neg_fbm_covariance_func(t, t - tau, num2, num1),
              self.neg_fbm_covariance_func(t + tau, t - tau, num2, num1)],
             [0, self.neg_fbm_covariance_func(t, t, num1, num2), self.neg_fbm_covariance_func(t + tau, t, num2, num1)],
             [0, 0, self.neg_fbm_covariance_func(t + tau, t + tau, num1, num2)]]
        for i in range(len(C)):
            for j in range(i + 1, len(C)):
                C[j][i] = C[i][j]
        D = np.vstack((np.hstack((A, C)), np.hstack((C, B))))
        covmm = np.linalg.inv(D)
        v = np.dot(covmm, b)
        return v

    @property
    def riemann_louville_mbm(self):
        """
            Riemann-Louville Multifractional Brownian Motion or Positive FBM.
            sample_size: Length of the discretized sample path.
            holder_exponents: Hurst function where 0<H(i)<1.
        """
        dt = 1 / (self.sample_size - 1)
        r = np.random.normal(0, 1, self.sample_size)
        t = np.arange(1, self.sample_size + 1) * dt
        M = np.zeros((self.sample_size, self.sample_size))
        for j in range(self.sample_size):
            w = ((t ** (2 * self.holder_exponents[j]) - (t - dt) ** (2 * self.holder_exponents[j])) / (
                    2 * self.holder_exponents[j])) ** 0.5
            for i in range(j + 1):
                M[j, i] = r[i] * w[j - i]
        pos = np.sum(M, axis=1)
        return pos

    def get_mbm(self, is_plot: bool = False, seed: int = None, hurst_name: str = '', plot_path: str = None,
                y_limits: list = None):
        means, labels = self.get_kmeans()
        # precalculation of 1D fBm in the length of k with random inputs.
        base_fbm = self.get_fractal_bases(means=means, seed=seed)
        # neighborhood search in holder exponents
        hu, hu1 = self.get_holder_neighborhood(means=means, labels=labels)
        # Krigeage: calculate some common coefficients for covariance matrices

        neg_mbm = self.get_series_by_krigeage(hu=hu, hu1=hu1, means=means, base_fbm=base_fbm)
        pos_mbm = self.riemann_louville_mbm
        mbm = ((scipy.special.gamma(2 * self.holder_exponents + 1) * np.sin(self.holder_exponents * np.pi)) ** (
                1 / 2) / scipy.special.gamma(self.holder_exponents + 1 / 2)) * (neg_mbm + pos_mbm)
        mbm[-1] = mbm[-2]
        if is_plot:
            self.plot(series=mbm, method_name='DPW', series_name='MBM', hurst_name=hurst_name, save_path=plot_path,
                      y_limits=y_limits)
        return mbm
