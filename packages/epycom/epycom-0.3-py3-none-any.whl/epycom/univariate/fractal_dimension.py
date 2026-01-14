# -*- coding: utf-8 -*-
# Copyright (c) St. Anne's University Hospital in Brno. International Clinical
# Research Center, Biomedical Engineering;
# Institute of Scientific Instruments of the CAS, v. v. i., Medical signals -
# Computational neuroscience. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

# Std imports

# Third pary imports
import numpy as np

# Local imports
from ..utils.method import Method


def compute_fractal_dimension(sig, Kmax=9):
    """
    Computes the fractal dimension (FD) of a signal using the Higuchi method.
    The FD is a measure of how "complicated" a signal is.
    Some papers refer this feature to have big correlation with the standatd
    deviation of the signal.

    Higher values of FD indicate more oscilations in the signal.

    To have comparable results between different signals, it is important to 
    pre-process the signal in the same way. Most importantly, the sampling 
    frequency should be the same and time length of the signal should be same. 
    
    To calcate FD by this method, important step is to choose 
    the parameter k carefully. For sampling frequency 1000 samples of signal, 
    k=10 is recommended by published papers.
    
    FD varies between 1 and 2, where 1 means a straight line.

    Parameters
    ----------
    sig: np.array
        2D numpy array of shape (signals, samples), time series (int, float)
    k: int
        parameter, number of different time intervals,
        for good results choose k carefully, for sampling frequency fs=800-1000,
        k=10 is recommended

    Returns
    -------
    FD: float
        FD of the signal, value in range 1<FD<2

    Example
    -------
    FD = compute_fractal_dimension(sig)
    """

    N = sig.size
    Kmax +=1
    L = np.zeros((Kmax, Kmax))
    for k in range (1, Kmax):
        for m in range (1, k+1):
            for i in range (1, (N-m)//k):
                L[k,m] += np.abs(sig[m+i*k]-sig[m+(i-1)*k]) #calculating length of the subrow in the signal
            L[k,m] *= (N-1)/(((N-m)//k)*k**2) #this term serves as a normalization factor for the curve length of y_k,m
    meanL = np.ones(Kmax-1)
    for k in range (1, Kmax):
        for m in range (1, k+1):
            meanL[k-1] += L[k,m]
        meanL[k-1] /= k
    meanL = np.log(meanL)
    k = np.linspace(1,Kmax-1, num=Kmax-1)
    k = np.log(k)
    line = np.polyfit(k, meanL, 1)
    FD = -line[0]
    return FD


class FractalDimension(Method):

    algorithm = 'FRACTAL_DIMENSION'
    algorithm_type = 'univareiate'
    version = '1.1.0'
    dtype = [('fractal_dimesion', 'float32')]


    def __init__(self, **kwargs):
        """
    Computes the FD of a signal using the Higuchi method.
    The FD is a measure of how "complicated" a signal is.
    Some papers refer this feature to have big correlation with the standatd
    deviation of the signal.

    Higher values of FD indicate more oscilations in the signal.

    To have comparable results between different signals, it is important to 
    pre-process the signal in the same way. Most importantly, the sampling 
    frequency should be the same and time length of the signal should be same. 
    
    To calcate FD by this method, important step is to choose 
    the parameter k carefully. For sampling frequency 1000 samples of signal, 
    k=10 is recommended by published papers.


        Parameters
        ----------
        sig: np.array
            2D numpy array of shape (signals, samples), 
            time series (int, float)
        Kmax: int
            parameter, number of different time intervals,
        """

        super().__init__(compute_fractal_dimension, **kwargs)
