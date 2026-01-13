"""Tuya device wrapper."""

# Dictionary to track logged warnings to avoid spamming logs
# Keyed by device ID
DEVICE_WARNINGS: dict[str, set[str]] = {}
