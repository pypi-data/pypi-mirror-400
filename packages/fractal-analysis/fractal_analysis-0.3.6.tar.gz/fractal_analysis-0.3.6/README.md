# Fractal Analysis
Fractal and multifractal methods, including 

- testers:
  - fractional Brownian motion (FBM) tester
  - multifractional Brownian motion (MBM) tester
- estimators:
  - IR hurst exponents estimator of multifractional Brownian motion (MBM)
  - QV hurst exponents estimator of multifractional Brownian motion (MBM)
- simulators:
  - Wood and Chan methods:
    - Wood and Chan fractional Brownian motion (FBM) simulator
    - Wood and Chan multifractional Brownian motion (MBM) simulator
  - DPW methods:
    - DPW fractional Brownian motion (FBM) simulator
    - DPW sub-fractional Brownian motion (sub-FBM) simulator
    - DPW bi-fractional Brownian motion (bi-FBM) simulator
    - DPW tri-fractional Brownian motion (tri-FBM) simulator
    - DPW general fractional self similar process simulator
    - DPW multifractional Brownian motion (MBM) simulator

## FBM / MBM tester
Test if a series is FBM (MBM) given the hurst parameter (hurst exponents series).
The implementation is based on the following papers:

>Michał Balcerek, Krzysztof Burnecki. (2020)  
Testing of fractional Brownian motion in a noisy environment.  
Chaos, Solitons & Fractals, Volume 140, 110097.  
https://doi.org/10.1016/j.chaos.2020.110097

>Balcerek, Michał, and Krzysztof Burnecki. (2020)  
Testing of Multifractional Brownian Motion. Entropy 22, no. 12: 1403.  
https://doi.org/10.3390/e22121403 

We added the following improvements to the FBM and/or MBM tester:
- option for automatically estimating sigma 
  - based on Theorem 2.3 of the following paper:
    >Ayache A., Peng Q. (2012)  
     Stochastic Volatility and Multifractional Brownian Motion.  
     In: Zili M., Filatova D. (eds) Stochastic Differential Equations and Processes. 
     Springer Proceedings in Mathematics, vol 7. Springer, Berlin, Heidelberg.  
     https://doi.org/10.1007/978-3-642-22368-6_6

[//]: # (  - a detailed introduction can be found in the section 5 of the following paper:)

[//]: # (    > todo: add paper name)
- option for testing if the series itself is a FBM (MBM)
- option for testing if the increment of the series is the increment of a FBM (MBM)
- option for testing if the series is a FBM (MBM) with an add-on noise
- option for testing if the increment of the series is the increment of a FBM (MBM) with an add-on noise

## IR / QV hurst estimator of MBM
Estimate the hurst parameter (hurst exponent series) of a MBM.
The implementation is based on the following paper:

>Bardet, Jean-Marc & Surgailis, Donatas, 2013.  
Nonparametric estimation of the local Hurst function of multifractional Gaussian processes.  
Stochastic Processes and their Applications, Elsevier, vol. 123(3), pages 1004-1045.


Bardet, the author in the above paper, provides a Matlab code that can be found at: 
>http://samm.univ-paris1.fr/Sofwares-Logiciels  
Software for estimating the Hurst function H of a Multifractional Brownian Motion:
 Quadratic Variation estimator and IR estimator

## Wood and Chan FBM simulator
Generate a Fractional Brownian Motion (FBM) using Wood and Chan circulant matrix. The implementation is based on the following paper:
>A.T.A. Wood, G. Chan, Simulation of stationary Gaussian process in [0,1]d.
Journal of Computational and Graphical Statistics, Vol. 3 (1994) 409-432.

and based on a Matlab library ```Fraclab``` and its function ```fbmwoodchan.m``` that can be found at:

>https://project.inria.fr/fraclab

## Wood and Chan MBM simulator
Generate a Multi-fractional Brownian Motion (mBm) using Wood&Chan circulant matrix, some krigging and a prequantification.
The implementation is based on the following paper:
>O. Barrie,"Synthe et estimation de mouvements Browniens multifractionnaires et autres processus rularit prescrite. 
Dinition du processus autorul multifractionnaire et applications", PhD Thesis (2007)

and based on a Matlab library ```Fraclab``` and its function ```mBmQuantifKrigeage.m``` that can be found at:

>https://project.inria.fr/fraclab

## DPW FBM / sub-FBM / bi-FBM / tri-FBM / self similar fractal simulator
Generate a fractional self similar processes. 

The main idea is:  use Lamperti transform to transfer a self-similar process to a stationary process, and
                   simulate the stationary process using circulant embedding approach (Wood, A.T.A., Chan, G., 1994.
                   Simulation of stationary Gaussian processes in [0, 1]^d. Journal of computational and graphical
                   statistics 3, 409–432). Then a subsequence of the simulated stationary process is convert back to
                   the series. 

The implementation is based on our paper:
>Y. Ding, Q. Peng, W. Wu "A General Method for Simulating H-self-similar Processes." 

[//]: # (> #todo: add paper link )


## DPW MBM simulator
Generates a Multi-fractional Brownian Motion (mBm) using DPW Lamperti Transformation, some krigging and a prequantification.

The implementation is based on our paper:
>Y. Ding, Q. Peng, W. Wu "A General Method for Simulating H-self-similar Processes." 

[//]: # (> #todo: add paper link )


## To install
To get started, simply do:
```
pip install fractal-analysis
```
or check out the code from out GitHub repository.

You can now use the series tester module in Python with:
```
from fractal_analysis import tester
```
or use the hurst estimators with
```
from fractal_analysis import estimator
```
or use the simulators with
```
from fractal_analysis import simulator
```

## Examples
### FBM / MBM tester
Import:
```
from fractal_analysis.tester.series_tester import MBMSeriesTester, FBMSeriesTester
from fractal_analysis.tester.critical_surface import CriticalSurfaceFBM, CriticalSurfaceMFBM
```
To test if a series ```series``` is FBM, use ```CriticalSurfaceFBM``` with length of the series ```N```,
the significance level ```alpha``` (look at quantiles of order ```alpha/2``` and ```1 − alpha/2```), and  choose to test
on the series itself or its increment series using ```is_increment_series``` (default is ```False```, meaning to test on
the series itself),
```
fbm_tester = FBMSeriesTester(critical_surface=CriticalSurfaceFBM(N=N, alpha=0.05, is_increment_series=False))
```

To test if the series is FBM with hurst parameter 0.3 and use auto estimated sigma square (set ```sig2=None```):

```
is_fbm, sig2 = fbm_tester.test(h=0.3, x=series, sig2=None, add_on_sig2=0)
```
If the output contains, for example:
> Bad auto sigma square calculated with error 6.239236333681868. Suggest to give sigma square and rerun.

The auto sigma square estimated is not accurate. You may want to manually choose a sigma square and rerun. For example:
```
is_fbm, sig2 = fbm_tester.test(h=0.3, x=series, sig2=1, add_on_sig2=0)
```
If you want to test with an add-on noise, change the value of ```add_on_sig2```.




To test if the series is MBM,  use ```CriticalSurfaceMFBM``` with length of the series ```N```
and the significance level ```alpha``` (look at quantiles of order ```alpha/2``` and ```1 − alpha/2```) 
```
mbm_tester = MBMSeriesTester(critical_surface=CriticalSurfaceMFBM(N=N, alpha=0.05, is_increment_series=False))
```
To test if the series is MBM with a given holder exponent series ```h_mbm_series``` and use auto estimated sigma square:
```
is_mbm, sig2 = mbm_tester.test(h=h_mbm_series, x=series, sig2=None, add_on_sig2=0)
```
Be aware that ```MBMSeriesTester``` requires ```len(h_mbm_series)==len(series)```.

#### Use of cache
Use caching to speed up the testing process. If the series ```x``` for testing is unchanged and multiple ```h``` 
and/or ```sig2``` are used, you may want to set 
```is_cache_stat=True``` to allow cache variable ```stat```. If ```h``` and ```sig2``` are unchanged and multiple ```x```
are used, you may want to set ```is_cache_quantile=True``` to allow cache variable ```quantile```. For example:
```
mbm_tester = MBMSeriesTester(critical_surface=CriticalSurfaceMFBM(N=N, alpha=0.05), is_cache_stat=True, is_cache_quantile=False)
```

### IR / QV hurst estimator of MBM
Import:
```
from fractal_analysis.estimator.hurst_estimator import IrHurstEstimator, QvHurstEstimator
import numpy as np
import math
```
Generate a standard brownian motion
```
N = 100
series = np.random.randn(N) * 0.5 * math.sqrt(1 / N)
series = np.cumsum(series)
```
To estimate the hurst exponents series of the above series with ```alpha=0.2``` using IR estimator,
```
estimator = IrHurstEstimator(mbm_series=series, alpha=0.2)
print(estimator.holder_exponents)
```
To estimate the hurst exponents series of the above series with ```alpha=0.2``` using QV estimator,
```
estimator = QvHurstEstimator(mbm_series=series, alpha=0.2)
print(estimator.holder_exponents)
```
Here the value of ```alpha``` decides how many observations on the ```mbm_series``` is used to estimate a point of the
holder exponent; small alpha means more observations are used for a single point and therefore the variance is small.
   
### Simulators

#### Wood and Chan FBM simulator
Import:
```
from fractal_analysis.simulator.wood_chan.wood_chan_fractal_simulator import WoodChanFbmSimulator
```
To simulate a FBM series with ```1000``` samples and ```0.8``` hurst parameter,
```
woodchan_fbm = WoodChanFbmSimulator(sample_size=1000, hurst_parameter=0.8).get_fbm()
```


#### Wood and Chan MBM simulator
Import:
```
from fractal_analysis.simulator.wood_chan.wood_chan_multi_fractal_simulator import WoodChanMbmSimulator
```
To simulate a MBM series with ```1000``` samples and a sin shape holder function,
```
sample_size=1000
t = np.linspace(0, 1, sample_size)
holder_exponents = 0.5 + 0.3 * np.sin(4 * np.pi * t)
woodchan_mbm = WoodChanMbmSimulator(sample_size=sample_size,holder_exponents=holder_exponents).get_mbm()
```

#### DPW FBM simulator
Import:
```
from fractal_analysis.simulator.dpw.dpw_fractal_simulator import DpwFbmSimulator
```
To simulate a FBM series with ```1000``` samples and ```0.8``` hurst parameter,
```
dpw_fbm = DpwFbmSimulator(sample_size=1000, hurst_parameter=0.8).get_fbm()
```

#### DPW sub-FBM simulator
Import:
```
from fractal_analysis.simulator.dpw.dpw_fractal_simulator import DpwSubFbmSimulator
```
To simulate a sub-FBM series with ```1000``` samples and ```0.8``` hurst parameter,
```
dpw_sub_fbm = DpwSubFbmSimulator(sample_size=1000, hurst_parameter=0.8).get_sub_fbm()
```
#### DPW bi-FBM simulator
Import:
```
from fractal_analysis.simulator.dpw.dpw_fractal_simulator import DpwBiFbmSimulator
```
To simulate a bi-FBM series with ```1000``` samples, ```0.8``` hurst parameter, and ```0.2``` bi factor,
```
dpw_bi_fbm = DpwBiFbmSimulator(sample_size=1000, hurst_parameter=0.8, bi_factor=0.2).get_bi_fbm()
```
When ```bi_factor=1```, bi-FBM becomes FBM

#### DPW tri-FBM simulator
Import:
```
from fractal_analysis.simulator.dpw.dpw_fractal_simulator import DpwTriFbmSimulator
```
To simulate a tri-FBM series with ```1000``` samples, ```0.8``` hurst parameter, and ```0.2``` tri factor,
```
dpw_tri_fbm = DpwTriFbmSimulator(sample_size=1000, hurst_parameter=0.8, tri_factor=0.2).get_tri_fbm()
```
When ```tri_factor=1```, tri-FBM becomes FBM with multiplier 2.

#### DPW self similar fractal simulator
Import:
```
from fractal_analysis.simulator.dpw.dpw_fractal_simulator import DpwSelfSimilarFractalSimulator
```
To simulate a customized self similar fractal series, you need to input ```covariance_func```. For example,
```
dpw_self_similar_fractal = DpwSelfSimilarFractalSimulator(sample_size, hurst_parameter, covariance_func).get_self_similar_process()
```

#### DPW MBM simulator
Import:
```
from fractal_analysis.simulator.dpw.dpw_multi_fractal_simulator import DpwMbmSimulator
```
To simulate a MBM series with ```1000``` samples and a sin shape holder function,
```
sample_size = 1000
t = np.linspace(0, 1, sample_size)
holder_exponents = 0.5 + 0.3 * np.sin(4 * np.pi * t)
dpw_mbm = DpwMbmSimulator(sample_size=sample_size, holder_exponents=holder_exponents).get_mbm()
```

#### Plot or seed a simulated series

In all simulators, you can use ```is_plot``` (default is ```False```) to show or not show the plot of the series. 
Set ```is_plot=True``` and ```plot_path="path_to_save/plot_name.png"``` (default is ```None```) to save the plot. 
Use ```seed```  (default is ```None```) to fix the random state. Use ```y_limits``` to fix y-axis range. 
In the mbm simulators, use ```hurst_name``` to name the holder exponent function in plot tile.  
For example,
```
dpw_fbm = DpwFbmSimulator(sample_size=1000, hurst_parameter=0.8).get_fbm(is_plot=True, seed=1, plot_path="path_to_save/plot_name.png")
```

#### To use ```lamperti_multiplier``` in DPW simulators
```lamperti_multiplier``` is a positive integer used for Lamperti transform. 
Bigger value (usually <=10) provides more accuracy; default value is 5. For example,
```
dpw_fbm = DpwFbmSimulator(sample_size=1000, hurst_parameter=0.8, lamperti_multiplier=10).get_fbm()
```