# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import List, Union, Callable, Optional

__all__ = [
    "Hit",
    "FlashCamTrigger",
    "MultiPMTTrigger",
    "HitFeatures",
    "RunInfo",
    "HitMaker",
    "FeatureExtractor",
    "ChargeReconstruction",
]


__doc__ = """
Python bindings for the SWGO Charge Reconstruction Library (swgo-charli).
"""


class Hit:
    """
    Class representing a hit with time and charge including their uncertainties.

    The update methods only modify the values if the new uncertainty is smaller than the current one.

    Attributes
    ----------
    channel : int
        The channel number.
    id : int
        The unique identifier for the hit.
    time : float
        The time in seconds.
    charge : float
        The charge in PE.
    time_uncertainty : float
        The uncertainty of the time in seconds.
    charge_uncertainty : float
        The uncertainty of the charge in PE.
    """

    def __init__(self, channel: int = -1, id: int = 0, time: float = 0.0, charge: float = 0.0,
                 time_uncertainty: float = float('inf'), charge_uncertainty: float = float('inf')) -> None: ...

    def is_valid(self) -> bool: ...

    @property
    def channel(self) -> int: ...

    @property
    def id(self) -> int: ...

    @property
    def time(self) -> float: ...

    @property
    def charge(self) -> float: ...

    @property
    def time_uncertainty(self) -> float: ...

    @property
    def charge_uncertainty(self) -> float: ...

    def update_time(self, new_time: float, new_time_uncertainty: float) -> bool:
        """
        Update the time and its uncertainty if the new uncertainty is smaller.

        Parameters
        ----------
        new_time : float
            The new time in seconds.
        new_time_uncertainty : float
            The new time uncertainty in seconds.

        Returns
        -------
        bool
            True if the time was updated, False otherwise.
        """

    def update_charge(self, new_charge: float, new_charge_uncertainty: float) -> bool:
        """
        Update the charge and its uncertainty if the new uncertainty is smaller.

        Parameters
        ----------
        new_charge : float
            The new charge in PE.
        new_charge_uncertainty : float
            The new charge uncertainty in PE.

        Returns
        -------
        bool
            True if the charge was updated, False otherwise.
        """

    def set_channel(self, channel: int) -> None:
        """
        Set the channel number.

        Parameters
        ----------
        channel : int
            The channel number.
        """


class FlashCamTrigger:
    """
    FlashCam trigger data structure.

    Contains the trigger time, channel number and waveform samples.

    Attributes
    ----------
    channel : int
        The channel number.
    trigger_time_s : int
        Seconds since run start.
    trigger_time_ticks : int
        Ticks since last full second (tick = 4ns).
    baseline : float
        Baseline in LSB.
    intsum : float
        Waveform sum in LSB.
    waveform : List[int]
        The waveform samples in LSB as a list of unsigned 16-bit integers.
    """

    channel: int
    trigger_time_s: int
    trigger_time_ticks: int
    baseline: float
    intsum: float
    waveform: List[int]

    def __init__(self) -> None: ...


class MultiPMTTrigger:
    """
    MultiPMT trigger data structure.

    Attributes
    ----------
    time : float
        Trigger time in seconds.
    channel : int
        Channel number.
    time_over_threshold : float
        Time over threshold in seconds.
    adc_sample : int
        ADC sample in LSB as an unsigned 16-bit integer.
    """

    time: float
    channel: int
    time_over_threshold: float
    adc_sample: int

    def __init__(self) -> None: ...


class HitFeatures:
    """
    Class to hold features of a hit used for charge and time reconstruction.

    All features are gated by "has" flags to indicate whether they are available.
    Getters raise RuntimeError if the feature is not set.

    Attributes
    ----------
    channel : int
        The channel number.
    id : int
        The hit ID.
    pmt_type : int
        The PMT type.
    waveform_integral : float
        The integral of the waveform in LSB.
    time_over_threshold : float
        The time over threshold in s.
    trigger_time : float
        The trigger time in s.
    adc_sample : float
        The ADC sample in LSB.
    """

    def __init__(self) -> None: ...
    # Feature properties. Getters will raise RuntimeError if the feature is not set.
    channel: int
    waveform_integral: float
    time_over_threshold: float
    trigger_time: float
    pmt_type: int
    adc_sample: float
    id: int

    def has_channel(self) -> bool: ...
    def has_waveform_integral(self) -> bool: ...
    def has_time_over_threshold(self) -> bool: ...
    def has_trigger_time(self) -> bool: ...
    def has_pmt_type(self) -> bool: ...
    def has_adc_sample(self) -> bool: ...
    def has_id(self) -> bool: ...


class RunInfo:
    """
    Run information data structure.

    Attributes
    ----------
    run_number : int
        The run number.
    time_offset_s : int
        Time offset in seconds since run start.
    time_offset_ns : int
        Time offset in nanoseconds within the last full second.
    run_start_time_ns : int
        Run start time as nanoseconds since epoch.
    """

    run_number: int
    time_offset_s: int
    time_offset_ns: int
    run_start_time_ns: int

    def __init__(self) -> None: ...

    @staticmethod
    def simulation_run() -> "RunInfo": ...

    @staticmethod
    def run_number_from_id(id: int) -> int: ...

    @staticmethod
    def trigger_index_from_id(id: int) -> int: ...

    # constants
    RUN_ID_SHIFT: int
    TRIGGER_INDEX_SHIFT: int


class FeatureExtractor:
    """
    Extractor for hit features from different trigger types.

    There is an extractor available for each supported trigger type. The extractors are
    automatically selected based on the type of the trigger data.
    """

    def __init__(self, settings: str) -> None:
        """
        Constructs a FeatureExtractor.

        Parameters
        ----------
        settings : str
            Path to the settings file.
        """

    def extract_features(self, trigger_data: List[Union[FlashCamTrigger, MultiPMTTrigger]], run_info: Optional["RunInfo"] = None) -> List[HitFeatures]:
        """
        Extracts hit features from a list of trigger data.

        Parameters
        ----------
        trigger_data : list
            The list of trigger data (FlashCamTrigger or MultiPMTTrigger).

        run_info : RunInfo, optional
            Run information (default is a simulation run).

        Returns
        -------
        list
            A list of extracted HitFeatures. Note that there is no one-to-one mapping between
            triggers and hit features: a single trigger may produce multiple hits or no hits.
        """


class HitMaker:
    """
    Class to create Hit objects from HitFeatures.

    HitMaker serves as a container for Reconstructors which represent different
    charge and time reconstruction algorithms.
    """

    def __init__(self, settings: str | None = None) -> None:
        """
        Construct an empty HitMaker or initialize from settings file.

        Parameters
        ----------
        settings : str, optional
            Path to the settings file. If omitted, an empty HitMaker is constructed.
        """

    def make_hits(self, features: List[HitFeatures], no_discard: bool = False) -> List[Hit]:
        """
        Creates Hit objects from the given HitFeatures.

        Parameters
        ----------
        features : list
            The hit features.
        no_discard : bool, optional
            If True, invalid hits will not be discarded. Default is False.

        Returns
        -------
        list
            A list of created Hit objects.
        """
    
    def add_reconstructor_from_callable(self, callable: Callable[[HitFeatures, Hit], Hit]) -> None:
        """
        Add a reconstructor backed by a Python callable.

        Parameters
        ----------
        callable : Callable[[HitFeatures, Hit], Hit]
            A callable that accepts (HitFeatures, Hit) and returns an updated Hit.
        """


class ChargeReconstruction:
    """
    The main interface of the charge reconstruction library.

    The reconstruct method converts trigger data (detector output) into hits (reconstruction output).
    The charge and time reconstruction can be configured via a settings file passed to the constructor.
    """

    def __init__(self, settings: str) -> None:
        """
        Create a ChargeReconstruction instance from the given settings file path.

        Parameters
        ----------
        settings : str
            Path to the settings file used to configure feature extractor and reconstructor.

        Raises
        ------
        Exception
            Propagates exceptions from feature extractor and reconstructor creation if settings are invalid.
        """

    def reconstruct(self, trigger_data: List[Union[FlashCamTrigger, MultiPMTTrigger]], run_info: Optional["RunInfo"] = None) -> List[Hit]:
        """
        Reconstruct hits from the given trigger data.

        Parameters
        ----------
        trigger_data : list
            A list of trigger objects (FlashCamTrigger or MultiPMTTrigger).

        run_info : RunInfo, optional
            Run information (default is a simulation run).

        Returns
        -------
        list
            A list of Hit objects resulting from the reconstruction.

        Notes
        -----
        A single trigger may produce multiple hits or no hits at all.
        """


# Functions from __init__.py

def hit_list_to_numpy(hits: List[Hit]) -> "numpy.ndarray":
    """
    Converts a list of Hit objects to a structured numpy array.

    Parameters
    ----------
    hits : List[Hit]
        List of Hit objects to convert.

    Returns
    -------
    numpy.ndarray
        Structured numpy array with fields: channel, id, time, charge, time_uncertainty, charge_uncertainty.
    """

def numpy_to_hit_list(np_array: "numpy.ndarray") -> List[Hit]:
    """
    Converts a structured numpy array to a vector of Hit objects.

    Parameters
    ----------
    np_array : numpy.ndarray
        Structured numpy array with fields: channel, id, time, charge, time_uncertainty, charge_uncertainty.

    Returns
    -------
    vector[Hit]
        Vector of Hit objects.
    """

def hit_features_list_to_numpy(features: List[HitFeatures]) -> "numpy.ndarray":
    """
    Converts a list of HitFeatures objects to a structured numpy array.
    Unset fields are represented with -1 for integers and NaN for floats.

    Parameters
    ----------
    features : List[HitFeatures]
        List of HitFeatures objects to convert.

    Returns
    -------
    numpy.ndarray
        Structured numpy array with fields: channel, pmt_type, id, trigger_time, waveform_integral, time_over_threshold, adc_sample.
    """

def numpy_to_hit_features_list(np_array: "numpy.ndarray") -> List[HitFeatures]:
    """
    Converts a structured numpy array to a vector of HitFeatures objects.
    Fields with -1 for integers and NaN for floats are considered unset.

    Parameters
    ----------
    np_array : numpy.ndarray
        Structured numpy array with fields: channel, pmt_type, id, trigger_time, waveform_integral, time_over_threshold, adc_sample.

    Returns
    -------
    vector[HitFeatures]
        Vector of HitFeatures objects.
    """