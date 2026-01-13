"""Shared discovery infrastructure for CLI commands.

Provides common functionality for mDNS device discovery used by
`hl datasource discover` subcommands.
"""

from __future__ import annotations

from typing import List, Sequence

import click

from highlighter.network.mdns import (
    DEFAULT_DEVICE_KEYWORDS,
    DEFAULT_SERVICE_TYPES,
    DiscoveredDevice,
    DiscoveryConfig,
    discover_devices,
)

DEFAULT_TIMEOUT = 5
DEFAULT_MAX_MAC_WORKERS = 8


def build_discovery_config(
    *,
    timeout: int,
    service_types: Sequence[str],
    keywords: Sequence[str],
    max_mac_workers: int,
) -> DiscoveryConfig:
    """Build DiscoveryConfig from CLI options.

    Args:
        timeout: Discovery timeout in seconds
        service_types: mDNS service types (empty = use defaults)
        keywords: Filter keywords (empty = use defaults)
        max_mac_workers: Max concurrent MAC resolution workers

    Returns:
        Configured DiscoveryConfig instance
    """
    return DiscoveryConfig(
        timeout_seconds=timeout,
        service_types=list(service_types) or list(DEFAULT_SERVICE_TYPES),
        device_keywords=list(keywords) or list(DEFAULT_DEVICE_KEYWORDS),
        max_mac_workers=max_mac_workers,
    )


def run_discovery(
    *,
    timeout: int,
    service_types: Sequence[str],
    keywords: Sequence[str],
    max_mac_workers: int,
    resolve_macs: bool,
) -> List[DiscoveredDevice]:
    """Run mDNS discovery with given options.

    Args:
        timeout: Discovery timeout in seconds
        service_types: mDNS service types to query
        keywords: Keywords to filter services
        max_mac_workers: Max concurrent MAC resolution workers
        resolve_macs: Whether to resolve MAC addresses via ARP

    Returns:
        List of discovered devices
    """
    config = build_discovery_config(
        timeout=timeout,
        service_types=service_types,
        keywords=keywords,
        max_mac_workers=max_mac_workers,
    )
    return discover_devices(config=config, resolve_macs=resolve_macs)


def common_discovery_options(func):
    """Decorator adding common discovery CLI options.

    Adds: --service-type, --keyword, --max-mac-workers, --timeout/-t

    Usage:
        @discover_group.command("list")
        @common_discovery_options
        def list_devices(timeout, service_types, keywords, max_mac_workers):
            ...
    """
    func = click.option(
        "-t",
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        show_default=True,
        help="Timeout in seconds for mDNS discovery",
    )(func)
    func = click.option(
        "--max-mac-workers",
        type=int,
        default=DEFAULT_MAX_MAC_WORKERS,
        show_default=True,
        help="Maximum concurrent MAC resolution tasks",
    )(func)
    func = click.option(
        "--keyword",
        "keywords",
        multiple=True,
        help="Filter services by keyword (repeatable, default targets common camera vendors)",
    )(func)
    func = click.option(
        "--service-type",
        "service_types",
        multiple=True,
        help="mDNS service type to query (repeatable, default: _http._tcp, _psia._tcp, _CGI._tcp)",
    )(func)
    return func
