# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from .charli import *

def _hit_list_to_numpy_ref(hits):
    """
    Convert a list of Hit objects to a structured numpy array.

    Parameters
    ----------
    hits : List[Hit]
        List of Hit objects to convert.

    Returns
    -------
    numpy.ndarray
        Structured numpy array with fields: channel, time, charge, time_uncertainty, charge_uncertainty.
    """
    import numpy as np

    dtype = np.dtype([
        ('channel', np.int32),
        ('id', np.int64),
        ('time', np.float64),
        ('charge', np.float64),
        ('time_uncertainty', np.float64),
        ('charge_uncertainty', np.float64),
    ])

    data = np.empty(len(hits), dtype=dtype)

    for i, hit in enumerate(hits):
        data[i]['channel'] = hit.channel
        data[i]['id'] = hit.id
        data[i]['time'] = hit.time
        data[i]['charge'] = hit.charge
        data[i]['time_uncertainty'] = hit.time_uncertainty
        data[i]['charge_uncertainty'] = hit.charge_uncertainty

    return data


def _numpy_to_hit_list_ref(np_array):
    """
    Convert a structured numpy array to a list of Hit objects.

    Parameters
    ----------
    np_array : numpy.ndarray
        Structured numpy array with fields: channel, time, charge, time_uncertainty, charge_uncertainty.

    Returns
    -------
    List[Hit]
        List of Hit objects.
    """
    hits = []
    for row in np_array:
        hit = Hit(
            channel=int(row['channel']),
            id=int(row['id']),
            time=float(row['time']),
            charge=float(row['charge']),
            time_uncertainty=float(row['time_uncertainty']),
            charge_uncertainty=float(row['charge_uncertainty'])
        )
        hits.append(hit)
    return hits


def _hit_features_list_to_numpy_ref(features):
    """
    Convert a list of HitFeatures objects to a structured numpy array.
    Unset fields are represented with -1 for integers and NaN for floats.

    Parameters
    ----------
    features : List[HitFeatures]
        List of HitFeatures objects to convert.

    Returns
    -------
    numpy.ndarray
        Structured numpy array with fields:  channel, pmt_type, trigger_time, waveform_integral, time_over_threshold, adc_sample.
    """
    import numpy as np

    dtype = np.dtype([
        ('channel', np.int32),
        ('pmt_type', np.int32),
        ('id', np.int64),
        ('trigger_time', np.float64),
        ('waveform_integral', np.float64),
        ('time_over_threshold', np.float64),
        ('adc_sample', np.float64),
    ])

    data = np.empty(len(features), dtype=dtype)

    for i, feature in enumerate(features):
        data[i]['channel'] = feature.channel if feature.has_channel() else -1
        data[i]['pmt_type'] = feature.pmt_type if feature.has_pmt_type() else -1
        data[i]['id'] = feature.id if feature.has_id() else -1
        data[i]['trigger_time'] = feature.trigger_time if feature.has_trigger_time() else np.nan
        data[i]['waveform_integral'] = feature.waveform_integral if feature.has_waveform_integral() else np.nan
        data[i]['time_over_threshold'] = feature.time_over_threshold if feature.has_time_over_threshold() else np.nan
        data[i]['adc_sample'] = feature.adc_sample if feature.has_adc_sample() else np.nan

    return data


def _numpy_to_hit_features_list_ref(np_array):
    """
    Convert a structured numpy array to a list of HitFeatures objects.
    Fields with -1 for integers and NaN for floats are considered unset.

    Parameters
    ----------
    np_array : numpy.ndarray
        Structured numpy array with fields: channel, pmt_type, trigger_time, waveform_integral, time_over_threshold, adc_sample.

    Returns
    -------
    List[HitFeatures]
        List of HitFeatures objects.
    """
    import numpy as np

    features = []
    for row in np_array:
        feature = HitFeatures()
        if row['channel'] != -1:
            feature.channel = int(row['channel'])
        if row['pmt_type'] != -1:
            feature.pmt_type = int(row['pmt_type'])
        if row['id'] != -1:
            feature.id = int(row['id'])
        if not np.isnan(row['trigger_time']):
            feature.trigger_time = float(row['trigger_time'])
        if not np.isnan(row['waveform_integral']):
            feature.waveform_integral = float(row['waveform_integral'])
        if not np.isnan(row['time_over_threshold']):
            feature.time_over_threshold = float(row['time_over_threshold'])
        if not np.isnan(row['adc_sample']):
            feature.adc_sample = float(row['adc_sample'])
        features.append(feature)

    return features
