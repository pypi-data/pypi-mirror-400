"""mDNS/Zeroconf discovery helpers shared by the CLI and SDK."""

from __future__ import annotations

import ipaddress
import logging
import platform
import re
import subprocess  # nosec B404 - Required for ARP/ping commands with validated inputs
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf

LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 5  # balances discovery completeness with CLI responsiveness
DEFAULT_SERVICE_TYPES = ["_http._tcp.local.", "_psia._tcp.local.", "_CGI._tcp.local."]
DEFAULT_DEVICE_KEYWORDS = ["HIKVISION", "CAMERA", "AXIS", "DAHUA", "IP CAM", "IPCAM"]


class DiscoveryError(Exception):
    """Raised when the Zeroconf discovery process fails."""


@dataclass
class DiscoveredDevice:
    """Representation of a discovered device."""

    service_name: str
    hostname: str
    ip: str
    port: str
    serial: str
    mac: Optional[str] = None


class DeviceServiceListener:
    """Listener for mDNS service discovery events."""

    def __init__(self, zeroconf: Zeroconf) -> None:
        self.zeroconf = zeroconf
        self.services: Dict[str, ServiceInfo] = {}
        self.lock = threading.Lock()

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        try:
            info = zc.get_service_info(type_, name)
            if info:
                with self.lock:
                    self.services[name] = info
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.debug("Failed to add service %s of type %s: %s", name, type_, exc)

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        self.add_service(zc, type_, name)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        with self.lock:
            removed = self.services.pop(name, None)
            if removed is None:
                LOGGER.debug("Attempted to remove unknown service %s", name)

    def get_services(self) -> List[ServiceInfo]:
        with self.lock:
            return list(self.services.values())


def normalize_mac(mac: str) -> Optional[str]:
    """Normalize MAC address format."""

    hex_digits = re.sub(r"[^0-9A-Fa-f]", "", mac)
    if len(hex_digits) != 12:
        return None

    pairs = [hex_digits[i : i + 2].upper() for i in range(0, 12, 2)]
    return ":".join(pairs)


class MacResolver:
    """Resolve MAC addresses for IPs across Linux, macOS, and Windows."""

    def __init__(self, platform_name: Optional[str] = None) -> None:
        self.platform_name = platform_name or platform.system()

    def resolve(self, ip: str) -> Optional[str]:
        if not _is_valid_ip(ip):
            LOGGER.debug("Skipping MAC resolution for invalid IP %s", ip)
            return None
        mac = self._query_arp_tables(ip)
        if mac:
            return mac

        self._ping_ip(ip)
        return self._query_arp_tables(ip)

    def _query_arp_tables(self, ip: str) -> Optional[str]:
        for command in self._commands_for_platform(ip):
            mac = self._run_and_extract(command)
            if mac:
                return mac
        return None

    def _run_and_extract(self, command: List[str]) -> Optional[str]:
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, timeout=5
            )  # nosec B603 - Command uses validated IP address with hardcoded system commands
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            LOGGER.debug("Command %s failed during MAC resolution: %s", command, exc)
            return None

        if result.returncode != 0:
            LOGGER.debug("Command %s exited with %s", command, result.returncode)
            return None

        mac = self._extract_mac(result.stdout)
        if mac:
            return normalize_mac(mac)
        return None

    def _commands_for_platform(self, ip: str) -> Iterable[List[str]]:
        system = self.platform_name
        if system == "Linux":
            yield ["ip", "neighbor", "show", ip]
            yield ["arp", "-n", ip]
        elif system == "Darwin":
            yield ["arp", "-n", ip]
            yield ["arp", ip]
        elif system == "Windows":
            yield ["arp", "-a", ip]
        else:
            yield ["arp", "-n", ip]

    def _ping_ip(self, ip: str) -> None:
        command: List[str]
        system = self.platform_name
        if system == "Linux":
            command = ["ping", "-c", "1", "-W", "1", ip]
        elif system == "Darwin":
            command = ["ping", "-c", "1", ip]
        elif system == "Windows":
            command = ["ping", "-n", "1", "-w", "1000", ip]
        else:
            command = ["ping", "-c", "1", ip]

        try:
            subprocess.run(
                command, capture_output=True, timeout=3
            )  # nosec B603 - Command uses validated IP address with hardcoded ping command
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return

    @staticmethod
    def _extract_mac(output: str) -> Optional[str]:
        pattern = re.compile(r"([0-9A-Fa-f]{2}(?:[:-][0-9A-Fa-f]{2}){5})")
        match = pattern.search(output)
        if match:
            return match.group(1)

        compact = re.compile(r"([0-9A-Fa-f]{12})")
        match = compact.search(output)
        if match:
            return match.group(1)
        return None


def extract_serial_from_name(name: str) -> Optional[str]:
    """Best-effort serial extractor tuned for vendor naming schemes."""

    candidates = re.findall(r"[A-Z0-9]{8,}", name.upper())
    for candidate in candidates:
        letters = sum(ch.isalpha() for ch in candidate)
        digits = sum(ch.isdigit() for ch in candidate)
        if letters >= 2 and digits >= 2 and len(candidate) <= 20:
            return candidate
    return None


@dataclass
class DiscoveryConfig:
    """Configuration knobs for device discovery."""

    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    service_types: List[str] = field(default_factory=lambda: list(DEFAULT_SERVICE_TYPES))
    device_keywords: List[str] = field(default_factory=lambda: list(DEFAULT_DEVICE_KEYWORDS))
    max_mac_workers: int = 8


def discover_devices(
    *,
    config: Optional[DiscoveryConfig] = None,
    resolve_macs: bool = True,
    mac_resolver: Optional[MacResolver] = None,
) -> List[DiscoveredDevice]:
    """Discover devices on the network using mDNS/Zeroconf."""

    cfg = config or DiscoveryConfig()

    zeroconf: Optional[Zeroconf] = None
    try:
        zeroconf = Zeroconf()
        listener = DeviceServiceListener(zeroconf)
        for service_type in cfg.service_types:
            ServiceBrowser(zeroconf, service_type, listener)

        time.sleep(cfg.timeout_seconds)

        raw_services = listener.get_services()
        filtered = _filter_device_services(raw_services, cfg.device_keywords)
        devices = _build_devices(filtered)
        deduped = _deduplicate_by_ip(devices)

        if resolve_macs:
            resolver = mac_resolver or MacResolver()
            _resolve_macs(deduped, resolver, cfg)

        return deduped
    except Exception as exc:  # pragma: no cover - exceptional path
        raise DiscoveryError(f"Error during mDNS discovery: {exc}") from exc
    finally:
        if zeroconf is not None:
            zeroconf.close()


def _filter_device_services(services: List[ServiceInfo], keywords: List[str]) -> List[ServiceInfo]:
    keyword_set = {kw.upper() for kw in keywords}
    filtered: List[ServiceInfo] = []
    for info in services:
        service_name = info.name.upper()
        if any(keyword in service_name for keyword in keyword_set):
            filtered.append(info)
    return filtered


def _build_devices(services: List[ServiceInfo]) -> List[DiscoveredDevice]:
    devices: List[DiscoveredDevice] = []
    for info in services:
        addresses = info.parsed_addresses()
        if not addresses:
            continue

        ipv4_addresses = [addr for addr in addresses if ":" not in addr]
        ip = ipv4_addresses[0] if ipv4_addresses else addresses[0]

        if not _is_valid_ip(ip):
            LOGGER.debug("Skipping invalid IP from service %s: %s", info.name, ip)
            continue

        hostname = (info.server or "").rstrip(".")
        port = str(info.port or "80")
        serial = _extract_serial(info.name, hostname)

        devices.append(
            DiscoveredDevice(
                service_name=info.name,
                hostname=hostname,
                ip=ip,
                port=port,
                serial=serial or "",
            )
        )
    return devices


def _deduplicate_by_ip(devices: List[DiscoveredDevice]) -> List[DiscoveredDevice]:
    deduped: Dict[str, DiscoveredDevice] = {}
    for device in devices:
        existing = deduped.get(device.ip)
        if existing:
            if device.serial and not existing.serial:
                existing.serial = device.serial
        else:
            deduped[device.ip] = device
    return list(deduped.values())


def _resolve_macs(devices: List[DiscoveredDevice], resolver: MacResolver, cfg: DiscoveryConfig) -> None:
    with ThreadPoolExecutor(max_workers=cfg.max_mac_workers) as executor:
        futures = [executor.submit(_resolve_single_mac, resolver, device) for device in devices]
        wait(futures)


def _resolve_single_mac(resolver: MacResolver, device: DiscoveredDevice) -> None:
    try:
        device.mac = resolver.resolve(device.ip)
    except Exception as exc:  # pragma: no cover - defensive
        LOGGER.debug("Failed to resolve MAC for %s: %s", device.ip, exc)
        device.mac = None


def _extract_serial(service_name: str, hostname: str) -> Optional[str]:
    for candidate in (service_name, hostname):
        serial = extract_serial_from_name(candidate)
        if serial:
            return serial
    return None


def _is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
