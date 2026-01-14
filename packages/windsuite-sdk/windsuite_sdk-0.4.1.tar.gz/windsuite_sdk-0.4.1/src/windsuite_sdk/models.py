"""Data models for the Windsuite SDK."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


@dataclass
class Vec3:
    """3D vector with x, y, z components."""

    x: float
    y: float
    z: float


@dataclass
class Quat:
    """Quaternion with w, x, y, z components."""

    w: float
    x: float
    y: float
    z: float


@dataclass
class WindProbeData:
    """
    Represents data from a wind probe.
    """

    timestamp_s: float
    wind_velocity_mps_probe_ref: Vec3  # Raw data
    wind_velocity_mps_windshaper_ref: Vec3
    wind_velocity_mps_windshaper_ref_corrected: Vec3  # Corrected for probe movement

    temperature_celcius: float
    atmospheric_pressure_hpascal: float
    static_pressure_pascal: float

    conversion_status: int
    data_is_valid: bool


@dataclass
class TrackedWindProbeData:
    """
    Represents windprobe data associated with the current position of the probe.
    """

    probe_tracking_data: TrackingData
    windprobe_data: WindProbeData
    curated_tracked_probe_data: BestTrackedWindProbeData | None = None


@dataclass
class BestWindProbeData:
    """
    Represents curated data from a wind probe.
    The velocity is the most accurate depending on the tracking.
    """

    timestamp_s: float
    best_wind_velocity_mps: Vec3
    temperature_celcius: float
    atmospheric_pressure_hpascal: float
    static_pressure_pascal: float
    conversion_status: int


@dataclass
class BestTrackedWindProbeData:
    """
    Represents curated windprobe data associated with the current position of the probe.
    """

    probe_position_mm_windshaper_ref: Vec3
    best_windprobe_data: BestWindProbeData


@dataclass
class TrackingData:
    """
    Represents tracking data for a single object.

    - Position in meters in the world reference frame,
    - Orientation as a quaternion in the world reference frame,

    ! Special case for the windshaper itself that will have the same as it's his reference frame
    - Position in meters in the windshaper reference frame,
    - Orientation as a quaternion in the windshaper reference frame,

    - Velocity in meters per second,
    - Angular velocity in degrees per second.
    """

    timestamp: float

    position_meters_world_ref: Vec3
    rotation_world_ref: Quat

    position_meters_windshaper_ref: Vec3
    rotation_windshaper_ref: Quat

    velocity_mps_world_ref: Vec3
    angular_velocity_degps_world_ref: Vec3

    velocity_mps_windshaper_ref: Vec3
    angular_velocity_degps_windshaper_ref: Vec3

    is_tracked: bool = False


class ModuleType(str, Enum):
    """
    Enum representing the type of a Windshaper Module.
    """

    MODULE_0812 = "0812"
    MODULE_0816 = "0816"
    MODULE_2420 = "2420"


@dataclass
class ModuleInfo:
    """
    Represents the current state of a Windshaper Module.

    Notes:
    It's possible to receive rpms and pwms in different formats depending on the Module type.

    For simplicity of use, the following conventions are used:
        Every received information is a list of lists, where each inner list represents a layer and each of these list contains the values for each fan in that layer.

        e.g.
            ! Module type 2420
            pwms = [[25.0]] -> Module with 1 layer and 1 fan with 25% pwm
            rpms = [[3445]] -> Module with 1 layer and 1 fan with 3445 rpm

            ! Module type 0816 / 0812
            pwms = [
                        [10, 10, 20, 20, 10, 10, 20, 20, 30], # ! UPSTREAM LAYER
                        [40, 40, 50, 50, 40, 40, 50, 50, 30], # ! DOWNSTREAM LAYER
                    ] -> Module with 2 layers and 9 fans per layer
            rpms = [
                        [1200, 1250, 1300, 1280, 1190, 1230, 1310, 1290, 1150], # ! UPSTREAM LAYER
                        [2200, 2250, 2300, 2280, 2190, 2230, 2310, 2290, 2150], # ! DOWNSTREAM LAYER
                    ] -> Module with 2 layers and 9 fans per layer

    """

    INDEX_DOWNSTREAM: ClassVar[int] = 0
    INDEX_UPSTREAM: ClassVar[int] = 1

    row: int
    col: int
    mac: str
    ip: str
    type: str

    lifepoints: int

    target_pwm: list[list[float]]
    current_pwm: list[list[float]]

    current_rpm: list[list[float]]

    target_psu_state: bool
    current_psu_state: bool

    is_connected: bool = False
