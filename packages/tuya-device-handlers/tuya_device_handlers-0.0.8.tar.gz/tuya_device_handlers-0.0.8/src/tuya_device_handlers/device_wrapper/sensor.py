"""Tuya device wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..raw_data_model import ElectricityData
from .base import DeviceWrapper
from .common import DPCodeEnumWrapper, DPCodeJsonWrapper, DPCodeRawWrapper

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


class WindDirectionEnumWrapper(DPCodeEnumWrapper, DeviceWrapper[str]):
    """Custom DPCode Wrapper for converting enum to wind direction."""

    _WIND_DIRECTIONS = {
        "north": 0.0,
        "north_north_east": 22.5,
        "north_east": 45.0,
        "east_north_east": 67.5,
        "east": 90.0,
        "east_south_east": 112.5,
        "south_east": 135.0,
        "south_south_east": 157.5,
        "south": 180.0,
        "south_south_west": 202.5,
        "south_west": 225.0,
        "west_south_west": 247.5,
        "west": 270.0,
        "west_north_west": 292.5,
        "north_west": 315.0,
        "north_north_west": 337.5,
    }

    def read_device_status(self, device: CustomerDevice) -> float | None:  # type: ignore[override]
        """Read the device value for the dpcode."""
        if (status := super().read_device_status(device)) is None:
            return None
        return self._WIND_DIRECTIONS.get(status)


class ElectricityCurrentJsonWrapper(DPCodeJsonWrapper, DeviceWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity current from JSON."""

    native_unit = "A"

    def read_device_status(self, device: CustomerDevice) -> float | None:  # type: ignore[override]
        """Read the device value for the dpcode."""
        if (status := super().read_device_status(device)) is None:
            return None
        return status.get("electricCurrent")


class ElectricityPowerJsonWrapper(DPCodeJsonWrapper, DeviceWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity power from JSON."""

    native_unit = "kW"

    def read_device_status(self, device: CustomerDevice) -> float | None:  # type: ignore[override]
        """Read the device value for the dpcode."""
        if (status := super().read_device_status(device)) is None:
            return None
        return status.get("power")


class ElectricityVoltageJsonWrapper(DPCodeJsonWrapper, DeviceWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity voltage from JSON."""

    native_unit = "V"

    def read_device_status(self, device: CustomerDevice) -> float | None:  # type: ignore[override]
        """Read the device value for the dpcode."""
        if (status := super().read_device_status(device)) is None:
            return None
        return status.get("voltage")


class ElectricityCurrentRawWrapper(DPCodeRawWrapper, DeviceWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity current from base64."""

    native_unit = "mA"
    suggested_unit = "A"

    def read_device_status(self, device: CustomerDevice) -> float | None:  # type: ignore[override]
        """Read the device value for the dpcode."""
        if (raw_value := super().read_device_status(device)) is None or (
            value := ElectricityData.from_bytes(raw_value)
        ) is None:
            return None
        return value.current


class ElectricityPowerRawWrapper(DPCodeRawWrapper, DeviceWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity power from base64."""

    native_unit = "W"
    suggested_unit = "kW"

    def read_device_status(self, device: CustomerDevice) -> float | None:  # type: ignore[override]
        """Read the device value for the dpcode."""
        if (raw_value := super().read_device_status(device)) is None or (
            value := ElectricityData.from_bytes(raw_value)
        ) is None:
            return None
        return value.power


class ElectricityVoltageRawWrapper(DPCodeRawWrapper, DeviceWrapper[float]):
    """Custom DPCode Wrapper for extracting electricity voltage from base64."""

    native_unit = "V"

    def read_device_status(self, device: CustomerDevice) -> float | None:  # type: ignore[override]
        """Read the device value for the dpcode."""
        if (raw_value := super().read_device_status(device)) is None or (
            value := ElectricityData.from_bytes(raw_value)
        ) is None:
            return None
        return value.voltage
