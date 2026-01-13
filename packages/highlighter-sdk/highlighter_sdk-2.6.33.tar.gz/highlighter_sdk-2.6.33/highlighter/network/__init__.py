"""Networking utilities for Highlighter SDK."""

from .mdns import (
    DEFAULT_DEVICE_KEYWORDS,
    DEFAULT_SERVICE_TYPES,
    DEFAULT_TIMEOUT_SECONDS,
    DiscoveredDevice,
    DiscoveryConfig,
    DiscoveryError,
    MacResolver,
    discover_devices,
    normalize_mac,
)

__all__ = [
    "DEFAULT_DEVICE_KEYWORDS",
    "DEFAULT_SERVICE_TYPES",
    "DEFAULT_TIMEOUT_SECONDS",
    "DiscoveryConfig",
    "DiscoveredDevice",
    "DiscoveryError",
    "MacResolver",
    "normalize_mac",
    "discover_devices",
]
