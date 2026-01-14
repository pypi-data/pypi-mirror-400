# -*- coding: utf-8 -*-
# Copyright (c) St. Anne's University Hospital in Brno. International Clinical
# Research Center, Biomedical Engineering;
# Institute of Scientific Instruments of the CAS, v. v. i., Medical signals -
# Computational neuroscience. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.


import numpy as np
import pandas as pd
from scipy.signal import find_peaks, spectrogram, detrend
from scipy import interpolate
# Local imports
from ...utils.method import Method


def __normalize_spec(f, t, Sxx, period, min_fs, max_fs, norm_max=None, norm_min=None):
    """
    Frequency-band crop and median-normalize a spectrogram in overlapping chunks.

    Parameters
    ----------
    f : np.ndarray
        Frequency vector returned by `scipy.signal.spectrogram`.
    t : np.ndarray
        Time vector returned by `scipy.signal.spectrogram`.
    Sxx : np.ndarray
        Spectrogram (freq x time) power matrix.
    period : float
        Window length [s] used to define chunk size along time for normalization.
    min_fs : float
        Lower frequency bound [Hz] for cropping. If <= 0, start from 0.
    max_fs : float
        Upper frequency bound [Hz] for cropping.
    norm_max : int or None, optional
        If provided, clip values above this ceiling after normalization.
    norm_min : int or None, optional
        If provided, clip values below this floor after normalization.

    Returns
    -------
    sxx_norm : np.ndarray
        Normalized spectrogram limited to the requested frequency range.
    t : np.ndarray
        Unchanged time vector (aligned with returned spectrogram).
    f : np.ndarray
        Cropped frequency vector.
    """
    if min_fs > 0:
        low_f_index = np.where(f < min_fs)[0][-1]
    else:
        low_f_index = 0

    high_f_index = np.where(f >= max_fs)[0][0]
    f = f[low_f_index:high_f_index]
    Sxx = Sxx[low_f_index:high_f_index, :]

    chunk = np.sum(t < period)
    overlap = chunk // 5

    sxx_norm = np.zeros(np.shape(Sxx))
    max_chunk = (len(t) // (chunk - overlap) - 1)
    for x in np.arange(max_chunk):
        sxx_norm[:, x * (chunk - overlap):x * (chunk - overlap) + chunk] = (
                Sxx[:, x * (chunk - overlap):x * (chunk - overlap) + chunk].T / np.median(
            Sxx[:, x * (chunk - overlap):x * (chunk - overlap) + chunk], axis=1)).T

    sxx_norm[:, (chunk - overlap) * max_chunk:-1] = (
            Sxx[:, (chunk - overlap) * max_chunk:-1].T / np.median(Sxx[:, (chunk - overlap) * max_chunk:-1],
                                                                   axis=1)).T

    if isinstance(norm_max, int):
        sxx_norm[sxx_norm > norm_max] = norm_max
    else:
        norm_max = 1e20

    if isinstance(norm_min, int):
        sxx_norm[sxx_norm < norm_min] = norm_min
    else:
        norm_min = 0

    sxx_norm = (sxx_norm - np.min(sxx_norm)) / np.max(sxx_norm)

    return sxx_norm, t, f


def __osc_shape(osc, fs):
    """
    Classify the shape of an oscillatory snippet as 'pistol' or 'blob'.

    The decision is based on local variance/transition ratios around the point
    of the steepest slope after detrending, using a short window derived from
    sampling frequency.

    Parameters
    ----------
    osc : np.ndarray
        1D array with samples of the candidate oscillation.
    fs : float
        Sampling frequency [Hz].

    Returns
    -------
    shape : str
        Either 'pistol' (sharp, high-contrast onset) or 'blob' (otherwise).
    """
    osc = detrend(osc)
    start = np.where(np.abs(np.diff(osc)) > (np.max(np.abs(np.diff(osc))) * 0.5))[0][0]

    sample_shift = int(fs/500)

    if (start > sample_shift) & (start < (len(osc)-sample_shift)):
        ratio1 = np.abs((np.mean(osc[start - sample_shift:start]) - np.mean(osc[start:start + sample_shift]))) / np.std(
            detrend(osc[start:start + sample_shift]))
        ratio = np.std(detrend(osc[start:start + sample_shift])) / np.std(
            detrend(osc[start - sample_shift:start]))  # (np.max(osc)-np.min(osc))/

        if (ratio > 4.5) & (ratio1 > 1):
            shape = 'pistol'
        elif (ratio > 10):
            shape = 'pistol'
        else:
            shape = 'blob'

    else:
        shape = 'blob'

    return shape

def __get_osc_amp(s, dmin=1, dmax=1, num_points=100):
    """
    Estimate oscillation amplitude via cubic-interpolated envelopes.

    Local extrema are detected, optionally reduced by taking extrema in
    `dmin`/`dmax`-sized chunks for robustness, and upper/lower envelopes are
    obtained with cubic interpolation. The amplitude is the max difference
    between upper and lower envelopes.

    Parameters
    ----------
    s : np.ndarray
        1D signal of the oscillation.
    dmin : int, optional
        Chunk size for reducing local minima candidates. Default is 1 (no
        reduction).
    dmax : int, optional
        Chunk size for reducing local maxima candidates. Default is 1 (no
        reduction).
    num_points : int, optional
        Number of points for the interpolated envelopes. Default is 100.

    Returns
    -------
    amp : float
        Estimated amplitude (max upper minus lower envelope). Returns 0 if not
        enough extrema are available to form envelopes.
    """
    # s = signal.detrend(s)
    # print(s)
    # locals min
    lmin = (np.diff(np.sign(np.diff(s))) > 0).nonzero()[0] + 1
    # locals max
    lmax = (np.diff(np.sign(np.diff(s))) < 0).nonzero()[0] + 1

    """
    # the following might help in some case by cutting the signal in "half"
    s_mid = np.mean(s) (0 if s centered or more generally mean of signal)
    # pre-sort of locals min based on sign 
    lmin = lmin[s[lmin]<s_mid]
    # pre-sort of local max based on sign 
    lmax = lmax[s[lmax]>s_mid]
    """

    # global max of dmax-chunks of locals max
    lmin = lmin[[i + np.argmin(s[lmin[i:i + dmin]]) for i in range(0, len(lmin), dmin)]]
    # global min of dmin-chunks of locals min
    lmax = lmax[[i + np.argmax(s[lmax[i:i + dmax]]) for i in range(0, len(lmax), dmax)]]

    # cannot interpolate less than 4 samples
    if (len(lmin) < 4) | (len(lmax) < 4):
        return 0
        #return (np.max(s) - np.min(s))

    higher = interpolate.griddata(lmax, s[lmax], xi=np.linspace(0, len(s), num_points), method='cubic')
    lower = interpolate.griddata(lmin, s[lmin], xi=np.linspace(0, len(s), num_points), method='cubic')
    sig_mean = (higher + lower) / 2

    # =============================================================================
    #     s_start = np.mean(s[:10])
    #     s_end = np.mean(s[10:])
    # =============================================================================
    interp = np.poly1d(np.polyfit(np.arange(len(s)), s, 3))

    return np.nanmax(higher - lower)


def detect_ufos(channel_data, fs, sensitivity=8, low_fc=1000, high_fc=8000):
    """
    Detect Ultra-Fast Oscillations (UFO) in a single-channel signal.

    The method computes a spectrogram, performs chunk-wise normalization,
    identifies salient broadband power increases above `low_fc`, and then
    extracts candidate events whose frequency profile shows sufficient
    peak-to-mean prominence. Each event is characterized by start/stop (in
    samples), dominant frequency, shape classification, and amplitude.

    Parameters
    ----------
    channel_data : np.ndarray
        1D raw signal.
    fs : float
        Sampling frequency [Hz].
    sensitivity : float, optional
        Minimum ratio of max-to-mean in the frequency profile to accept an
        event. Higher values are more conservative. Default is 8.
    low_fc : float, optional
        Lower cutoff frequency [Hz] from which the broadband power is summed.
        Default is 1000.
    high_fc : float, optional
        Upper bound [Hz] for analysis (also limited by fs/3). Default is 8000.

    Returns
    -------
    detections : list[tuple]
        List of tuples `(event_start, event_stop, frequency, shape, amplitude)`
        where `event_start` and `event_stop` are expressed in samples (floats
        based on `t * fs`), `frequency` is the dominant frequency [Hz], `shape`
        is 'pistol' or 'blob', and `amplitude` is a float derived from envelope
        difference. Returns an empty list if no events are detected.
    """
    show_plot = False
    connect_pieces = False
    window = 0.0157

    if fs < 2 * high_fc:
        return []

    # compute spectrogram
    # koeficients are based on nperseg 512 and noverlap 496 when fs is 32556

    f_orig, t_orig, Sxx = spectrogram(channel_data, fs, window='nuttall', nperseg=int(fs * window),
                                      noverlap=int(int(fs * window) * 0.96875), nfft=None, detrend='constant')
    # normalize spec
    max_fs = np.min([int(fs / 3), high_fc])

    min_fs = 0
    period = 1
    norm_max = 200
    norm_min = 5

    sxx_norm1, t1, f1 = __normalize_spec(f_orig, t_orig, Sxx, period, min_fs, max_fs)
    sxx_norm, t, f = __normalize_spec(f_orig, t_orig, Sxx, period, min_fs, max_fs, norm_max, norm_min)

    low_f_index = np.where(f <= low_fc)[0][-1]

    med_const = int(fs * 0.003)
    if np.mod(med_const, 2) == 0:
        med_const += 1

    det_sig = np.sum(sxx_norm[low_f_index:, :], axis=0)

    # determine threshold
    thresh = 5 * np.percentile(det_sig, 99)  # + 2*np.std(det_sig)
    # TODO fix more peaks within one
    peak_pos = find_peaks(det_sig, height=thresh)[0]
    peak_maxs = det_sig[peak_pos]

    th_indexes = (det_sig > thresh)
    th_sig = np.zeros(len(det_sig))
    th_sig[th_indexes] = 1

    th_starts = np.where(th_sig - np.append(th_sig[1:], th_sig[-1]) == -1)[0] + 1
    th_stops = np.where(th_sig - np.append(th_sig[1:], th_sig[-1]) == 1)[0]

    # condition to prevent error during multiprocessing
    if len(peak_pos) > 0:

        det_sig_d = np.diff(det_sig)
        inflex_d = np.where(np.diff(np.sign(np.diff(det_sig_d))))[0] + 1
        if inflex_d[0] >= peak_pos[0]:
            if len(peak_pos) > 1:
                peak_pos = peak_pos[1:]
                peak_maxs = peak_maxs[1:]
            else:
                return pd.DataFrame()

        if inflex_d[-1] <= peak_pos[-1]:
            if len(peak_pos) > 1:
                peak_pos = peak_pos[:-1]
                peak_maxs = peak_maxs[:-1]
            else:
                return []

        inflex_d = np.sort(np.append(peak_pos, inflex_d))

        peaks_in_inflex_pos_d = np.intersect1d(inflex_d, peak_pos, return_indices=True)[1]
        det_start = inflex_d[peaks_in_inflex_pos_d - 1] - 2
        det_end = inflex_d[peaks_in_inflex_pos_d + 1] + 4

        if connect_pieces:
            peak_num = []
            for i in np.arange(len(th_starts)):
                peak_app = np.sum((peak_pos > th_starts[i]) & (peak_pos < th_stops[i]))
                peak_num.append(peak_app)
            peak_num = np.array(peak_num) - 1

            del_idxes = np.where(np.array(peak_num) > 0)[0]
            del_count = peak_num[del_idxes]
            for i, x in enumerate(del_idxes):
                print(x)
                while del_count[i] > 0:
                    det_start = np.delete(det_start, x + 1)
                    det_end = np.delete(det_end, x)
                    del_count[i] = del_count[i] - 1

        len_ind = np.where((det_end - det_start) != 0)
        det_start = det_start[len_ind]
        det_end = det_end[len_ind]

        sums_axis = [np.sum(sxx_norm1[:, det_start[x]:det_end[x]], axis=1) for x in
                     np.arange(len(det_start))]


        # get frequencies
        frequencies = np.array([f1[np.argmax(x)] for x in sums_axis])

        # take only oscillations, whose frequency profile max peak is 10 times bigger than its mean
        max_to_mean = [np.max(x) / np.mean(x) > sensitivity for x in sums_axis]
        det_start = det_start[(max_to_mean) & (frequencies>low_fc)]
        det_end = det_end[max_to_mean & (frequencies>low_fc)]
        frequencies = frequencies[max_to_mean & (frequencies>low_fc)]

        if len(det_start) == 0:
            return []

        oscilations = [channel_data[int(t[det_start[x]] * fs): int(np.floor(t[det_end[x] - 1] * fs))] for x in
                       np.arange(len(det_start))]

        # classify shape and measure amplitude
        shapes = []
        amplitudes = []
        for oscilation in oscilations:
            shapes.append(__osc_shape(oscilation, fs))
            amplitudes.append(__get_osc_amp(oscilation))

        if det_end[-1] > len(t) - 1:
            det_start = det_start[:-1]
            det_end = det_end[:-1]
            frequencies = frequencies[:-1]
            shapes = shapes[:-1]
        if len(det_start) == 0:
            return []

        return list(zip(t[det_start] * fs, t[det_end] * fs, frequencies, shapes, amplitudes))

    else:

        return []

    return detectionsDF


class UfoDetector(Method):
    algorithm = 'UFO_DETECTOR'
    algorithm_type = 'event'
    version = '1.0.0'
    dtype = [('event_start', 'int32'),
             ('event_stop', 'int32'),
             ('frequency', 'int32'),
             ('shape', 'U10'),
             ('amplitude', 'float32'),]

    def __init__(self, **kwargs):
        """
        Ufo detection algorithm.

        Parameters
        ----------
        fs: int
            Sampling frequency
        threshold: float
            Number of standard deviations to use as a threshold

        References
        ----------
        [1] Ultra-fast oscillation detection in EEG signal from deep-brain microelectrodes
        V Travnicek, P Jurak, J Cimbalnik, P Klimes, P Daniel, M Brazdil - 2021 43rd annual international conference
        of the IEEE …, 2021
        """

        super().__init__(detect_ufos, **kwargs)
