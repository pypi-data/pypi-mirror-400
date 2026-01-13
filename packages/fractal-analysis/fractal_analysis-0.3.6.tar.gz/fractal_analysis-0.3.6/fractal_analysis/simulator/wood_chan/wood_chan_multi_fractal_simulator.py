from abc import ABC, abstractmethod
from typing import Union, List, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np

from fractal_analysis.simulator.wood_chan.wood_chan_fractal_simulator import WoodChanFbmSimulator


class KMeans:  # todo: find out if sklearn kmeans can produce same results
    """
     Implemented based on the MatLab library FracLab k_means.m
    """

    def __init__(self, n_clusters: int, x: Union[List, np.ndarray]):
        self.n_clusters = n_clusters
        self.x = x
        self.n = len(self.x)
        self.x_min = None
        self.x_max = None
        self.cluster_centers: Optional[np.ndarray] = None
        self.labels: Optional[np.ndarray] = None
        self.fit()

    def fit(self):
        x_sorted = np.sort(self.x)
        x_sorted_idx = np.argsort(self.x)
        self.x_min = x_sorted[0]
        self.x_max = x_sorted[-1]
        # initialization of average of n_clusters: linearly distributed between x_min and x_max
        new_avg = np.linspace(self.x_min, self.x_max, self.n_clusters)
        old_avg = np.zeros(self.n_clusters)
        sep = np.zeros(self.n_clusters - 1)
        while np.sum(np.abs(old_avg - new_avg)) != 0.0:
            # old average
            old_avg = new_avg
            # assignment of classes to kernels
            # x(i) belongs each k class , abs(x(i)-z(k)) = min(j, abs(x(i)-z(j)))
            # special case scalar and sorted values: separator = avgerage between 2 kernels
            sepx = np.array([0.5 * (new_avg[i] + new_avg[i + 1]) for i in range(self.n_clusters - 1)])
            # clear sep
            sep = np.zeros(self.n_clusters - 1)
            for i in range(self.n_clusters - 1):
                for j in range(self.n):
                    if x_sorted[j] <= sepx[i] <= x_sorted[j + 1]:
                        sep[i] = j
            sep = np.concatenate(([0], sep, [self.n - 1])).astype('int')

            # recalculate the average
            new_avg = np.array([np.mean(x_sorted[sep[i]:sep[i + 1] + 1]) for i in range(self.n_clusters)])
        self.cluster_centers = new_avg
        # create the vector resulting from the projection of the points on their corresponding kernel
        label_sorted = np.zeros(self.n).astype('int')
        for i in range(self.n_clusters):
            label_sorted[sep[i]: sep[i + 1] + 1] = i
        # reorder in the initial order
        label_zip = sorted(zip(x_sorted_idx, label_sorted), key=lambda x: x[0])
        self.labels = np.array([item[1] for item in label_zip])


class MultiFractalBaseSimulator(ABC):
    def __init__(self, sample_size: int, holder_exponents: np.ndarray, pre_quant_level: int = 10, tmax: float = 1,
                 std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            holder_exponents: is a list of real value in (0:1); it allows to model a process the pointwise regularity of which varies in time.
            pre_quant_level: levels for the pre-quantification.
            tmax: generates series using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates series using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """
        self.sample_size = sample_size
        if self.sample_size <= 0:
            raise ValueError(f'sample_size must be a positive integer.')
        if not isinstance(holder_exponents, np.ndarray):
            raise ValueError(f'holder_exponents must be in type numpy array.')
        if not all((holder_exponents > 0) & (holder_exponents < 1)):
            raise ValueError(f'elements in holder_exponents must be in range (0, 1).')
        self.pre_quant_level = pre_quant_level
        self.tmax = tmax
        if not self.tmax > 0:
            raise ValueError(f'tmax must be positive.')
        self.std_const = std_const
        if not self.std_const > 0:
            raise ValueError(f'std_const must be positive.')

        self.eps = 10 ** (-3)
        self.holder_exponents = np.maximum(self.eps, np.minimum(1 - self.eps, holder_exponents))

    def get_kmeans(self) -> Tuple[np.array, np.array]:
        kmeans = KMeans(n_clusters=self.pre_quant_level, x=self.holder_exponents)
        # To avoid the case of "3 neighbours", we add the min and max values to the k - avgs with a "safety" margin
        mean_min = kmeans.cluster_centers[0]
        mean_max = kmeans.cluster_centers[-1]

        if 2 * kmeans.x_min - mean_min < 0:
            mean_inf = max(self.eps, kmeans.x_min - 10 * self.eps)
        else:
            mean_inf = 2 * kmeans.x_min - mean_min

        if 2 * kmeans.x_max - mean_max > 1:
            mean_sup = min(1 - self.eps, kmeans.x_max + 10 * self.eps)
        else:
            mean_sup = 2 * kmeans.x_max - mean_max

        means = np.concatenate(([mean_inf], kmeans.cluster_centers, [mean_sup]))
        return means, kmeans.labels

    @abstractmethod
    def get_fractal_base_func(self, mean: float, seed: int):
        pass

    def get_fractal_bases(self, means: np.array, seed: int) -> np.ndarray:
        """simulate multiple series"""
        base_fbm = np.zeros((self.sample_size, self.pre_quant_level + 2))
        for i in range(self.pre_quant_level + 2):
            base_fbm[:, i] = self.get_fractal_base_func(mean=means[i], seed=seed)
        return base_fbm

    def get_holder_neighborhood(self, means: np.ndarray, labels: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        hu = np.zeros(self.sample_size)
        for i in range(self.sample_size):
            ind = labels[i]
            if self.holder_exponents[i] < means[ind + 1]:
                hu[i] = ind
            else:
                hu[i] = ind + 1
        hu1 = hu + 1
        return hu, hu1

    @abstractmethod
    def fractal_cov_matrix(self, i, hu_, hu1_, holder_exponent, means, f_lst=None, q_lst=None):
        pass

    def get_series_by_krigeage(self, hu: np.ndarray, hu1: np.ndarray, means: np.ndarray, base_fbm: np.ndarray,
                               f_lst: np.ndarray = None, q_lst: np.ndarray = None):
        series = np.zeros(self.sample_size)

        for i in range(1, self.sample_size - 1):
            hu_ = int(hu[i])
            hu1_ = int(hu1[i])
            if abs(self.holder_exponents[i] - means[hu_]) < self.eps:
                series[i] = base_fbm[i, hu_]
            elif abs(self.holder_exponents[i] - means[hu1_]) < self.eps:
                series[i] = base_fbm[i, hu1_]
            else:
                v = self.fractal_cov_matrix(i=i, hu_=hu_, hu1_=hu1_, f_lst=f_lst, q_lst=q_lst,
                                            holder_exponent=self.holder_exponents[i],
                                            means=means)
                u = np.array([base_fbm[i - 1, hu_], base_fbm[i, hu_], base_fbm[i + 1, hu_],
                              base_fbm[i - 1, hu1_], base_fbm[i, hu1_], base_fbm[i + 1, hu1_]])
                series[i] = np.dot(u, v)
        return series

    def plot(self, series: np.ndarray, method_name: str, series_name: str, hurst_name: str = '', save_path: str = None,
             y_limits: list = None):
        plt.plot(np.arange(0, self.tmax, self.tmax / self.sample_size), series)
        plt.title(
            f'{method_name} {series_name} simulation with {self.sample_size} samples and {hurst_name} hurst')
        plt.xlabel('Time')
        if y_limits is not None:
            plt.ylim(y_limits)
        if save_path is not None:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


class WoodChanMbmSimulator(MultiFractalBaseSimulator):
    """
        Main idea: generates a Multi-fractional Brownian Motion (mBm) using Wood&Chan circulant matrix, some krigging
                   and a prequantification.
        Reference: O. Barrie,"Synthe et estimation de mouvements Browniens multifractionnaires et autres processus
                   rularit prescrite. Dinition du processus autorul multifractionnaire et applications",
                   PhD Thesis (2007).
        Corresponding Matlab code: FracLab (https://project.inria.fr/fraclab/)
                                   mBmQuantifKrigeage.m
    """

    def __init__(self, sample_size: int, holder_exponents: np.ndarray, pre_quant_level: int = 10, tmax: float = 1,
                 std_const: float = 1):
        """
            sample_size: is the length of samples generated; it is a positive integer.
            holder_exponents: is a list of real value in (0:1); it allows to model a process the pointwise regularity of which varies in time.
            pre_quant_level: levels for the pre-quantification.
            tmax: generates series using a specific size of time support, i.e. the time runs in [0,tmax]; if tmax is not specified, the default value is tmax = 1.
            std_const: generates series using a specific standard deviation at instant t = 1; if std_const is not specified, the default value is std_const = 1.
        """
        super().__init__(sample_size=sample_size, holder_exponents=holder_exponents, pre_quant_level=pre_quant_level,
                         tmax=tmax, std_const=std_const)

    def get_fractal_base_func(self, mean: float, seed: int):
        fbm_simulator = WoodChanFbmSimulator(sample_size=self.sample_size, hurst_parameter=mean, tmax=self.tmax,
                                             std_const=self.std_const)
        return fbm_simulator.get_fbm(seed=seed)

    @staticmethod
    def new_gamma(z):  # todo: find out if scipy gamma can produce same results
        """
            Idea: function gamma(z) adjusted to the scalar z 0<z<1
            Ref: Abramowitz & Stegun, Handbook of Mathemtical Functions, sec. 6.1.

                 "An Overview of Software Development for Special
                 Functions", W. J. Cody, Lecture Notes in Mathematics,
                 506, Numerical Analysis Dundee, 1975, G. A. Watson
                 (ed.), Springer Verlag, Berlin, 1976.

                 Computer Approximations, Hart, Et. Al., Wiley and sons, New York, 1968.
        """
        ppp = np.array([-1.71618513886549492533811e+0, 2.47656508055759199108314e+1,
                        -3.79804256470945635097577e+2, 6.29331155312818442661052e+2,
                        8.66966202790413211295064e+2, -3.14512729688483675254357e+4,
                        -3.61444134186911729807069e+4, 6.64561438202405440627855e+4])
        qqq = np.array([-3.08402300119738975254353e+1, 3.15350626979604161529144e+2,
                        -1.01515636749021914166146e+3, -3.10777167157231109440444e+3,
                        2.25381184209801510330112e+4, 4.75584627752788110767815e+3,
                        -1.34659959864969306392456e+5, -1.15132259675553483497211e+5])
        xnum = 0
        xden = 1
        for i in range(8):
            xnum = (xnum + ppp[i]) * z
            xden = xden * z + qqq[i]
        res = (xnum + xden) / (xden * z)
        return res

    @staticmethod
    def ii_func(h):  # todo: find out if scipy.stats.hypergeom can do the same thing
        if h == 0:
            ii = np.inf
        elif h < 0.5:
            q = 1 / h
            ii = WoodChanMbmSimulator.new_gamma(1 - 2 * h) * q * np.sin(np.pi * (0.5 - h))
        elif h == 0.5:
            ii = np.pi
        else:
            qq = 1 / (h * (2 * h - 1))
            ii = WoodChanMbmSimulator.new_gamma(2 - 2 * h) * qq * np.sin(np.pi * (h - 0.5))
        return ii

    @staticmethod
    def fbm_cov_matrix(index, hu_, hu1_, h1, h2, f, h, n, means):
        """
            calculates the covariance matrix of basic FBMs and coefficients for the calculating of MBM in the case of
            6 grid neighbour of (t,H(t))
        """
        t = (index + 1) / n
        tau = 1 / n
        num1 = means[hu_]
        num2 = means[hu1_]
        hh = WoodChanMbmSimulator.ii_func(h)
        f1 = 0.5 * WoodChanMbmSimulator.ii_func((num1 + h) / 2) * (1 / np.sqrt(h1 * hh))
        f2 = 0.5 * WoodChanMbmSimulator.ii_func((num2 + h) / 2) * (1 / np.sqrt(h2 * hh))
        b1 = f1 * np.array([t ** (num1 + h) + (t - tau) ** (num1 + h) - tau ** (num1 + h), 2 * t ** (num1 + h),
                            t ** (num1 + h) + (t + tau) ** (num1 + h) - tau ** (num1 + h)])
        b2 = f2 * np.array([t ** (num2 + h) + (t - tau) ** (num2 + h) - tau ** (num2 + h), 2 * t ** (num2 + h),
                            t ** (num2 + h) + (t + tau) ** (num2 + h) - tau ** (num2 + h)])
        b = np.concatenate([b1, b2])
        A = 0.5 * np.array(
            [[2 * (t - tau) ** (2 * num1), (t - tau) ** (2 * num1) + t ** (2 * num1) - tau ** (2 * num1),
              (t - tau) ** (2 * num1) + (t + tau) ** (2 * num1) - (2 * tau) ** (2 * num1)],
             [0, 2 * t ** (2 * num1), t ** (2 * num1) + (t + tau) ** (2 * num1) - tau ** (2 * num1)],
             [0, 0, 2 * (t + tau) ** (2 * num1)]])
        A = A + np.triu(A, 1).T
        B = 0.5 * np.array([[2 * (t - tau) ** (2 * num2), (t - tau) ** (2 * num2) + t ** (2 * num2) - tau ** (2 * num2),
                             (t - tau) ** (2 * num2) + (t + tau) ** (2 * num2) - (2 * tau) ** (2 * num2)],
                            [0, 2 * t ** (2 * num2), t ** (2 * num2) + (t + tau) ** (2 * num2) - tau ** (2 * num2)],
                            [0, 0, 2 * (t + tau) ** (2 * num2)]])
        B = B + np.triu(B, 1).T
        C = f * np.array([[2 * (t - tau) ** (num1 + num2),
                           (t - tau) ** (num1 + num2) + t ** (num1 + num2) - tau ** (num1 + num2),
                           (t - tau) ** (num1 + num2) + (t + tau) ** (num1 + num2) - (2 * tau) ** (num1 + num2)],
                          [0, 2 * t ** (num1 + num2),
                           t ** (num1 + num2) + (t + tau) ** (num1 + num2) - tau ** (num1 + num2)],
                          [0, 0, 2 * (t + tau) ** (num1 + num2)]])
        C = C + np.triu(C, 1).T
        D = np.concatenate((np.concatenate((A, C), axis=1), np.concatenate((C, B), axis=1)))
        covm = np.linalg.inv(D)
        v = covm.dot(b)
        err = np.abs(t ** (2 * h) - np.dot(b.T, v))
        return v, err

    def get_q_lst(self, means):
        q = np.zeros(self.pre_quant_level + 2)
        for i in range(1, self.pre_quant_level + 3):
            q[i - 1] = WoodChanMbmSimulator.ii_func(means[i - 1])
        return q

    def get_f_lst(self, means, q):
        f = np.zeros(self.pre_quant_level + 2)
        for i in range(1, self.pre_quant_level + 2):
            f[i] = 0.5 * WoodChanMbmSimulator.ii_func((means[i] + means[i - 1]) / 2) * (1 / np.sqrt(q[i] * q[i - 1]))
        return f

    def fractal_cov_matrix(self, i, hu_, hu1_, holder_exponent, means, f_lst=None, q_lst=None):

        v, _ = WoodChanMbmSimulator.fbm_cov_matrix(index=i, hu_=hu_, hu1_=hu1_, h1=q_lst[hu_], h2=q_lst[hu1_],
                                                   f=f_lst[hu1_],
                                                   h=holder_exponent, n=self.sample_size, means=means)
        return v

    def get_mbm(self, is_plot: bool = False, seed: int = None, hurst_name: str = '', plot_path: str = None,
                y_limits: list = None):
        """simulate a mbm series"""
        means, labels = self.get_kmeans()
        # precalculation of 1D fBm in the length of k with random inputs.
        base_fbm = self.get_fractal_bases(means=means, seed=seed)
        # neighborhood search in holder exponents
        hu, hu1 = self.get_holder_neighborhood(means=means, labels=labels)
        # Krigeage: calculate some common coefficients for covariance matrices
        q_lst = self.get_q_lst(means=means)
        f_lst = self.get_f_lst(means=means, q=q_lst)
        mbm = self.get_series_by_krigeage(hu=hu, hu1=hu1, means=means, base_fbm=base_fbm, f_lst=f_lst, q_lst=q_lst)
        mbm[-1] = mbm[-2]
        if is_plot:
            self.plot(series=mbm, method_name='Wood and Chan', series_name='MBM', hurst_name=hurst_name,
                      save_path=plot_path, y_limits=y_limits)
        return mbm
