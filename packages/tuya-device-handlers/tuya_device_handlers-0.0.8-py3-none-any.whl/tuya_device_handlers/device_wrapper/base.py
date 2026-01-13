"""Tuya device wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tuya_sharing import CustomerDevice  # type: ignore[import-untyped]


class DeviceWrapper[T]:
    """Base device wrapper."""

    native_unit: str | None = None
    suggested_unit: str | None = None

    max_value: float
    min_value: float
    value_step: float

    options: list[str]

    def read_device_status(self, device: CustomerDevice) -> T | None:
        """Read device status and convert to a Home Assistant value."""
        raise NotImplementedError

    def get_update_commands(
        self, device: CustomerDevice, value: T
    ) -> list[dict[str, Any]]:
        """Generate update commands for a Home Assistant action."""
        raise NotImplementedError
