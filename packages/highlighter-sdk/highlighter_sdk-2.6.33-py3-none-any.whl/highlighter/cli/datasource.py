"""CLI commands for data source management."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import List, Optional
from uuid import UUID

import click

from highlighter.cli.discovery_cli import (
    common_discovery_options,
    run_discovery,
)
from highlighter.datasource.models import LocalDataSourceEntry, LocalDataSourceFile
from highlighter.datasource.service import DataSourceService
from highlighter.network.mdns import (
    DiscoveredDevice,
    DiscoveryError,
    normalize_mac,
)

DEFAULT_URI_PATTERN = "rtsp://{ip}:554/stream"
DEFAULT_NAME_PATTERN = "{service_name}"


@click.group("datasource")
@click.pass_context
def datasource_group(ctx):
    """Manage data sources for Highlighter."""
    pass


@datasource_group.group("discover")
@click.pass_context
def discover_group(ctx):
    """Commands for network device discovery and data source export."""
    pass


@discover_group.command("list")
@click.option(
    "--show-mac/--no-show-mac",
    default=True,
    help="Show MAC addresses (requires ARP access)",
)
@common_discovery_options
def list_devices(timeout, service_types, keywords, max_mac_workers, show_mac):
    """List all discovered devices on the network."""
    click.echo("Discovering devices on the network...")
    try:
        devices = run_discovery(
            timeout=timeout,
            resolve_macs=show_mac,
            service_types=service_types,
            keywords=keywords,
            max_mac_workers=max_mac_workers,
        )
    except DiscoveryError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    if not devices:
        click.echo("No devices found.")
        return

    click.echo(f"\nFound {len(devices)} device(s):\n")

    for i, device in enumerate(devices, 1):
        click.echo(f"{i}. {device.service_name}")
        click.echo(f"   IP:       {device.ip}:{device.port}")
        click.echo(f"   Hostname: {device.hostname}")
        if device.serial:
            click.echo(f"   Serial:   {device.serial}")
        if show_mac:
            mac = device.mac or "Unknown"
            click.echo(f"   MAC:      {mac}")
        click.echo()


@discover_group.command("find")
@click.option(
    "-m", "--mac", type=str, help="MAC address to search for (format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX)"
)
@click.option("-s", "--serial", type=str, help="Serial number to search for")
@common_discovery_options
def find_device(
    mac: Optional[str], serial: Optional[str], timeout: int, service_types, keywords, max_mac_workers
) -> None:
    """Find a device by MAC address or serial number."""
    if not mac and not serial:
        click.echo("Error: Must provide either --mac or --serial", err=True)
        sys.exit(1)

    normalized_mac = None
    if mac:
        normalized_mac = normalize_mac(mac)
        if not normalized_mac:
            click.echo(f"Error: Invalid MAC address format: {mac}", err=True)
            click.echo("Expected format: XX:XX:XX:XX:XX:XX", err=True)
            sys.exit(1)

    click.echo("Discovering devices on the network...")
    try:
        devices = run_discovery(
            timeout=timeout,
            resolve_macs=True,
            service_types=service_types,
            keywords=keywords,
            max_mac_workers=max_mac_workers,
        )
    except DiscoveryError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    if not devices:
        click.echo("No devices found.")
        sys.exit(1)

    matches: List[DiscoveredDevice] = []
    for device in devices:
        if normalized_mac and (device.mac or "").upper() == normalized_mac:
            matches.append(device)
        elif serial and device.serial and serial.upper() in device.serial.upper():
            matches.append(device)

    if not matches:
        if normalized_mac:
            click.echo(f"No device found with MAC address: {normalized_mac}", err=True)
        if serial:
            click.echo(f"No device found with serial number: {serial}", err=True)
        sys.exit(1)

    if len(matches) > 1:
        click.echo("Warning: Multiple devices match the criteria:", err=True)
        for device in matches:
            click.echo(
                f"  - {device.ip} (Serial: {device.serial or 'Unknown'}, MAC: {device.mac or 'Unknown'})",
                err=True,
            )
        click.echo()

    device = matches[0]
    click.echo("Found device:")
    click.echo(f"  Service:  {device.service_name}")
    click.echo(f"  IP:       {device.ip}")
    click.echo(f"  Port:     {device.port}")
    click.echo(f"  Hostname: {device.hostname}")
    if device.serial:
        click.echo(f"  Serial:   {device.serial}")
    click.echo(f"  MAC:      {device.mac or 'Unknown'}")

    click.echo(f"\nIP Address: {device.ip}")


@discover_group.command("batch")
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True, readable=True),
    help="File containing MAC addresses (one per line)",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    help="Write lookup results to a file",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["csv", "datasource"]),
    default="csv",
    show_default=True,
    help="Output as CSV or datasource JSON (for cloud import)",
)
@click.option(
    "-T",
    "--template",
    type=str,
    help="Template name for datasource export (format=datasource)",
)
@click.option(
    "--uri-pattern",
    type=str,
    default=DEFAULT_URI_PATTERN,
    show_default=True,
    help="URI pattern for datasource export (format=datasource)",
)
@click.option(
    "--name-pattern",
    type=str,
    default=DEFAULT_NAME_PATTERN,
    show_default=True,
    help="Name pattern for datasource export (format=datasource)",
)
@click.option("--csv/--no-csv", default=True, help="Include CSV header (default: True)")
@click.option("--quiet/--no-quiet", default=False, help="Suppress discovery messages, only show results")
@click.option(
    "--show-hostname/--no-show-hostname", default=True, help="Include hostname in output (default: True)"
)
@click.argument("macs", nargs=-1)
@common_discovery_options
@click.pass_context
def batch_find(
    ctx,
    file,
    output,
    output_format,
    template,
    uri_pattern,
    name_pattern,
    timeout,
    csv,
    quiet,
    macs,
    service_types,
    keywords,
    max_mac_workers,
    show_hostname,
):
    """Find multiple devices by MAC addresses and emit results."""

    class MacRequest:
        def __init__(self, mac: str, name: Optional[str] = None) -> None:
            self.mac = mac
            self.name = name

    mac_list: List[str] = []

    if macs:
        mac_list.extend(macs)

    if file:
        with open(file, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line and not line.startswith("#"):
                    mac_list.append(line)

    if not sys.stdin.isatty() and not file and not macs:
        for line in sys.stdin:
            line = line.strip()
            if line and not line.startswith("#"):
                mac_list.append(line)

    if not mac_list:
        click.echo("Error: No MAC addresses provided for batch lookup", err=True)
        click.echo("Use --file, provide MACs as arguments, or pipe to stdin", err=True)
        sys.exit(1)

    mac_requests: List[MacRequest] = []
    for mac in mac_list:
        requested_name = None
        mac_value = mac
        if "=" in mac:
            parts = mac.split("=", 1)
            requested_name = parts[0].strip() or None
            mac_value = parts[1].strip()

        norm = normalize_mac(mac_value)
        if norm:
            mac_requests.append(MacRequest(norm, requested_name))
        else:
            if not quiet:
                click.echo(f"Warning: Invalid MAC address format: {mac}", err=True)

    if not mac_requests:
        click.echo("Error: No valid MAC addresses found", err=True)
        sys.exit(1)

    patterns_provided = uri_pattern != DEFAULT_URI_PATTERN or name_pattern != DEFAULT_NAME_PATTERN
    if output_format == "csv" and (template or patterns_provided):
        click.echo(
            "Error: --template/--uri-pattern/--name-pattern are only valid when --format=datasource",
            err=True,
        )
        sys.exit(1)

    if not quiet:
        click.echo(
            f"Discovering devices on the network (searching for {len(mac_requests)} MAC addresses)...",
            err=True,
        )

    try:
        devices = run_discovery(
            timeout=timeout,
            resolve_macs=True,
            service_types=service_types,
            keywords=keywords,
            max_mac_workers=max_mac_workers,
        )
    except DiscoveryError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    mac_to_device = {device.mac: device for device in devices if device.mac}

    found_count = 0
    if output_format == "datasource":
        # Validate template/pattern usage
        if template and patterns_provided:
            click.echo(
                "Error: Cannot specify both --template and custom patterns (--uri-pattern/--name-pattern)",
                err=True,
            )
            sys.exit(1)

        service = DataSourceService(ctx.obj["client"])
        loaded_template = None
        if template:
            loaded_template = service.load_template(template)
            if not loaded_template:
                click.echo(f"Error: Template '{template}' not found", err=True)
                available = service.list_templates()
                if available:
                    click.echo(f"Available templates: {', '.join(available)}", err=True)
                else:
                    click.echo("No templates available", err=True)
                sys.exit(1)

        entries = []
        seen_source_uris = set()
        for request in mac_requests:
            norm_mac = request.mac
            device = mac_to_device.get(norm_mac)
            if not device:
                continue
            if loaded_template:
                entry = service.apply_template(loaded_template, device, requested_name=request.name)
            else:
                placeholders = {
                    "ip": device.ip or "",
                    "hostname": device.hostname or "",
                    "port": device.port or "",
                    "serial": device.serial or "",
                    "mac": device.mac or "",
                    "service_name": device.service_name or "",
                }
                source_uri = uri_pattern.format(**placeholders)
                name = name_pattern.format(**placeholders)
                entry = LocalDataSourceEntry(
                    name=request.name or name,
                    source_uri=source_uri,
                    mac=device.mac,
                    serial=device.serial,
                    hostname=device.hostname,
                    ip=device.ip,
                    port=device.port,
                    template=None,
                )
            source_uri = entry.source_uri or ""
            if source_uri and source_uri in seen_source_uris:
                continue
            if source_uri:
                seen_source_uris.add(source_uri)
            entries.append(entry)
            found_count += 1

        data_source_file = LocalDataSourceFile(
            data_sources=entries,
            template=template if template else None,
        )

        if output:
            output_path = Path(output)
            service.save_file(output_path, data_source_file)
            if not quiet:
                click.echo(f"Saved data sources to {output_path}", err=True)
        else:
            click.echo(
                json.dumps(
                    data_source_file.model_dump(mode="json", exclude_none=False), indent=2, default=str
                )
            )

    else:
        output_lines: List[str] = []
        if csv:
            header = "MAC,IP,Hostname" if show_hostname else "MAC,IP"
            output_lines.append(header)

        for request in mac_requests:
            norm_mac = request.mac
            device = mac_to_device.get(norm_mac)
            ip = device.ip if device else "not_found"
            hostname = device.hostname if device else ""
            if device:
                found_count += 1

            if show_hostname:
                output_lines.append(f"{norm_mac},{ip},{hostname}")
            else:
                output_lines.append(f"{norm_mac},{ip}")

        if output:
            output_path = Path(output)
            output_path.write_text("\n".join(output_lines) + ("\n" if output_lines else ""), encoding="utf-8")
            if not quiet:
                click.echo(f"Wrote results to {output_path}", err=True)

        for line in output_lines:
            click.echo(line)

    if not quiet:
        click.echo(f"\nFound {found_count}/{len(mac_requests)} devices", err=True)


@datasource_group.command("list")
@click.option(
    "--file", "-f", type=click.Path(exists=True), help="Local file path (if not specified, queries cloud)"
)
@click.option(
    "--format",
    type=click.Choice(["table", "json", "csv", "stream"]),
    default="table",
    show_default=True,
    help="Output format",
)
@click.option(
    "--stream-template",
    type=click.Path(exists=True),
    help="Template JSON for stream definitions (used with --format=stream)",
)
@click.pass_context
def list_datasources(ctx, file: Optional[str], format: str, stream_template: Optional[str]):
    """List data sources from cloud or local file."""
    client = ctx.obj["client"]
    service = DataSourceService(client)

    if file:
        # Load from local file
        data_source_file = service.load_file(Path(file))
        sources = data_source_file.data_sources
        if format != "stream":
            click.echo(f"Data sources from {file}:")
    else:
        # Fetch from cloud
        cloud_sources = service.fetch_from_cloud()
        if format != "stream":
            click.echo(f"Data sources from cloud ({len(cloud_sources)} total):")

        if format == "json":
            output = [{"id": s.id, "uuid": str(s.uuid), "name": s.name} for s in cloud_sources]
            click.echo(json.dumps(output, indent=2))
            return
        elif format == "csv":
            click.echo("id,uuid,name")
            for s in cloud_sources:
                click.echo(f"{s.id},{s.uuid},{s.name}")
            return
        elif format == "stream":
            sources = cloud_sources
            # fall through to stream formatting
        else:
            # Table format
            if not cloud_sources:
                click.echo("No data sources found.")
                return

            click.echo()
            for i, s in enumerate(cloud_sources, 1):
                click.echo(f"{i}. {s.name}")
                click.echo(f"   ID:   {s.id}")
                click.echo(f"   UUID: {s.uuid}")
                click.echo()
            return

    # Local file formatting
    if format == "json":
        click.echo(json.dumps([s.model_dump(mode="json") for s in sources], indent=2, default=str))
    elif format == "csv":
        click.echo("id,uuid,name,source_uri,mac,serial")
        for s in sources:
            click.echo(
                f"{s.id or ''},{s.uuid or ''},{s.name},{s.source_uri or ''},{s.mac or ''},{s.serial or ''}"
            )
    elif format == "stream":
        # Build stream definitions from a template
        def _format_value(value, placeholders):
            if isinstance(value, str):
                return value.format(**placeholders)
            if isinstance(value, dict):
                return {k: _format_value(v, placeholders) for k, v in value.items()}
            if isinstance(value, list):
                return [_format_value(v, placeholders) for v in value]
            return value

        if stream_template:
            with open(stream_template, "r", encoding="utf-8") as f:
                template_obj = json.load(f)
        else:
            template_obj = {"data_sources": "({source_uri})", "subgraph_name": "{name}"}

        stream_defs = []
        for s in sources:
            placeholders = {
                "id": s.id or "",
                "uuid": str(s.uuid) if s.uuid else "",
                "name": s.name,
                "source_uri": getattr(s, "source_uri", None) or "",
                "mac": getattr(s, "mac", None) or "",
                "serial": getattr(s, "serial", None) or "",
                "hostname": getattr(s, "hostname", None) or "",
                "ip": getattr(s, "ip", None) or "",
                "port": getattr(s, "port", None) or "",
            }
            try:
                formatted = _format_value(copy.deepcopy(template_obj), placeholders)
            except KeyError as exc:
                click.echo(f"Error: Unknown placeholder in stream template: {exc}", err=True)
                sys.exit(1)
            stream_defs.append(formatted)

        click.echo(json.dumps(stream_defs, indent=2))
    else:
        # Table format
        if not sources:
            click.echo("No data sources found.")
            return

        click.echo()
        for i, s in enumerate(sources, 1):
            click.echo(f"{i}. {s.name}")
            if s.id:
                click.echo(f"   ID:         {s.id}")
            if s.uuid:
                click.echo(f"   UUID:       {s.uuid}")
            if s.source_uri:
                click.echo(f"   Source URI: {s.source_uri}")
            if s.mac:
                click.echo(f"   MAC:        {s.mac}")
            if s.serial:
                click.echo(f"   Serial:     {s.serial}")
            click.echo()


@datasource_group.command("view")
@click.option("--id", type=int, help="Data source ID")
@click.option("--uuid", type=str, help="Data source UUID")
@click.option("--name", "-n", type=str, help="Data source name")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    show_default=True,
    help="Output format",
)
@click.pass_context
def view_datasource(ctx, id: Optional[int], uuid: Optional[str], name: Optional[str], format: str):
    """View details of a single data source."""
    client = ctx.obj["client"]
    service = DataSourceService(client)

    # Validate that exactly one identifier is provided
    identifiers = [id, uuid, name]
    if sum(x is not None for x in identifiers) != 1:
        click.echo("Error: Must provide exactly one of --id, --uuid, or --name", err=True)
        sys.exit(1)

    # Fetch the data source
    try:
        if id:
            source = service.get_by_id(id)
        elif uuid:
            source = service.get_by_uuid(UUID(uuid))
        elif name:
            source = service.get_by_name(name)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if not source:
        click.echo("Error: Data source not found", err=True)
        sys.exit(1)

    # Output
    if format == "json":
        output = {"id": source.id, "uuid": str(source.uuid), "name": source.name}
        click.echo(json.dumps(output, indent=2))
    else:
        # Table format
        click.echo(f"Data Source: {source.name}")
        click.echo(f"ID:   {source.id}")
        click.echo(f"UUID: {source.uuid}")


@datasource_group.command("create")
@click.option("--name", "-n", type=str, required=True, help="Data source name")
@click.option("--source-uri", "-u", type=str, help="Source URI (e.g., rtsp://hostname:554/stream)")
@click.option(
    "--format",
    type=click.Choice(["table", "json"]),
    default="table",
    show_default=True,
    help="Output format",
)
@click.pass_context
def create_datasource(ctx, name: str, source_uri: Optional[str], format: str):
    """Create a single data source in the cloud."""
    client = ctx.obj["client"]
    service = DataSourceService(client)

    try:
        created = service.create(name=name, source_uri=source_uri)
        click.echo(f"Created data source: {created.name}")

        if format == "json":
            output = {"id": created.id, "uuid": str(created.uuid), "name": created.name}
            click.echo(json.dumps(output, indent=2))
        else:
            click.echo(f"ID:   {created.id}")
            click.echo(f"UUID: {created.uuid}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@datasource_group.command("update")
@click.option("--id", type=int, help="Data source ID")
@click.option("--uuid", type=str, help="Data source UUID")
@click.option("--name", "-n", type=str, help="Data source name (for lookup) or new name")
@click.option("--source-uri", "-u", type=str, help="New source URI")
@click.option("--new-name", type=str, help="New name (when using --id or --uuid for lookup)")
@click.pass_context
def update_datasource(
    ctx,
    id: Optional[int],
    uuid: Optional[str],
    name: Optional[str],
    source_uri: Optional[str],
    new_name: Optional[str],
):
    """Update an existing data source in the cloud."""
    client = ctx.obj["client"]
    service = DataSourceService(client)

    # Validate that exactly one identifier is provided
    identifiers = [id, uuid, name]
    if sum(x is not None for x in identifiers) != 1:
        click.echo("Error: Must provide exactly one of --id, --uuid, or --name for lookup", err=True)
        sys.exit(1)

    # If using name for lookup but also want to change the name
    if name and new_name:
        # Lookup by name first
        existing = service.get_by_name(name)
        if not existing:
            click.echo(f"Error: Data source '{name}' not found", err=True)
            sys.exit(1)
        id = existing.id
        name = new_name

    try:
        updated = service.update(
            data_source_id=id,
            data_source_uuid=UUID(uuid) if uuid else None,
            name=name or new_name,
            source_uri=source_uri,
        )
        click.echo(f"Updated data source: {updated.name}")
        click.echo(f"ID:   {updated.id}")
        click.echo(f"UUID: {updated.uuid}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@datasource_group.command("delete")
@click.option("--id", type=int, help="Data source ID")
@click.option("--uuid", type=str, help="Data source UUID")
@click.option("--name", "-n", type=str, help="Data source name")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def delete_datasource(ctx, id: Optional[int], uuid: Optional[str], name: Optional[str], yes: bool):
    """Delete a data source from the cloud."""
    client = ctx.obj["client"]
    service = DataSourceService(client)

    # Validate that exactly one identifier is provided
    identifiers = [id, uuid, name]
    if sum(x is not None for x in identifiers) != 1:
        click.echo("Error: Must provide exactly one of --id, --uuid, or --name", err=True)
        sys.exit(1)

    # Lookup by name if needed
    if name:
        source = service.get_by_name(name)
        if not source:
            click.echo(f"Error: Data source '{name}' not found", err=True)
            sys.exit(1)
        id = source.id
        display_name = name
    else:
        # Fetch to show what we're deleting
        if id:
            source = service.get_by_id(id)
        else:
            source = service.get_by_uuid(UUID(uuid))

        if not source:
            click.echo("Error: Data source not found", err=True)
            sys.exit(1)
        display_name = source.name

    # Confirm deletion
    if not yes:
        confirm = click.confirm(f"Are you sure you want to delete data source '{display_name}'?")
        if not confirm:
            click.echo("Aborted.")
            return

    try:
        service.destroy(data_source_id=id, data_source_uuid=UUID(uuid) if uuid else None)
        click.echo(f"Deleted data source: {display_name}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@datasource_group.command("sync")
@click.option("--input", "-i", type=click.Path(exists=True), required=True, help="Input data sources file")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (if not specified, updates input file in-place)",
)
@click.option(
    "--match-by",
    type=click.Choice(["id", "uuid", "name", "source_uri", "auto"]),
    default="auto",
    show_default=True,
    help="Matching strategy (use source_uri to skip duplicate URIs, use uuid to allow duplicates)",
)
@click.option("--dry-run", is_flag=True, help="Preview matches without writing output")
@click.pass_context
def sync_datasources(
    ctx,
    input: str,
    output: Optional[str],
    match_by: str,
    dry_run: bool,
):
    """Align a local datasources file with what's already in cloud.

    This does NOT create or update anything in the cloud. It only fetches
    cloud data sources, matches them to local entries, and writes matched
    cloud IDs/UUIDs back into the local file.
    """
    client = ctx.obj["client"]
    service = DataSourceService(client)

    input_path = Path(input)
    output_path = Path(output) if output else input_path

    # Load local file
    data_source_file = service.load_file(input_path)
    click.echo(f"Loaded {len(data_source_file.data_sources)} data sources from {input_path}")

    # Fetch cloud data sources
    click.echo("Fetching data sources from cloud...")
    cloud_sources = service.fetch_from_cloud()
    click.echo(f"Found {len(cloud_sources)} data sources in cloud")

    # Match entries
    matches = service.match_entries(data_source_file.data_sources, cloud_sources, match_by)

    # Display results
    matched_count = sum(1 for m in matches if m.is_matched)
    unmatched_count = len(matches) - matched_count

    click.echo(f"\nMatching results:")
    click.echo(f"  Matched:   {matched_count}")
    click.echo(f"  Unmatched: {unmatched_count}")

    if dry_run:
        click.echo("\nDry run - showing matches:")
        for match in matches:
            if match.is_matched:
                click.echo(
                    f"  ✓ {match.local.name} -> Cloud ID: {match.cloud.id} (matched by {match.match_type})"
                )
            else:
                click.echo(f"  ✗ {match.local.name} (no match)")
        return

    # Update local entries with cloud IDs
    for match in matches:
        if match.is_matched:
            match.local.id = match.cloud.id
            match.local.uuid = match.cloud.uuid

    # Save updated file
    service.save_file(output_path, data_source_file)
    click.echo(f"\nSaved updated data sources to {output_path}")


@datasource_group.command("import")
@click.option("--input", "-i", type=click.Path(exists=True), required=True, help="Input data sources file")
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file with updated cloud IDs (if not specified, updates input in-place)",
)
@click.option("--create-missing", is_flag=True, help="Create data sources that don't exist in cloud")
@click.option("--update-existing", is_flag=True, help="Update existing cloud data sources with local values")
@click.option(
    "--match-by",
    type=click.Choice(["id", "uuid", "name", "source_uri", "auto"]),
    default="auto",
    show_default=True,
    help="Matching strategy for existing data sources (source_uri skips duplicates, uuid allows duplicates)",
)
@click.option("--dry-run", is_flag=True, help="Preview changes without applying them")
@click.pass_context
def import_datasources(
    ctx,
    input: str,
    output: Optional[str],
    create_missing: bool,
    update_existing: bool,
    match_by: str,
    dry_run: bool,
):
    """Push a local datasources file into the cloud.

    Supports creating missing entries (--create-missing) and/or updating
    existing ones (--update-existing). Writes back cloud IDs/UUIDs to the file
    after applying changes.
    """
    client = ctx.obj["client"]
    service = DataSourceService(client)

    input_path = Path(input)
    output_path = Path(output) if output else input_path

    # Load local file
    data_source_file = service.load_file(input_path)
    click.echo(f"Loaded {len(data_source_file.data_sources)} data sources from {input_path}")

    if dry_run:
        # Fetch cloud data sources for preview
        click.echo("Fetching data sources from cloud...")
        cloud_sources = service.fetch_from_cloud()
        matches = service.match_entries(data_source_file.data_sources, cloud_sources, match_by)

        click.echo("\nDry run - preview of actions:")
        for match in matches:
            if match.is_matched:
                if update_existing:
                    click.echo(f"  UPDATE: {match.local.name} (ID: {match.cloud.id})")
                else:
                    click.echo(f"  SKIP:   {match.local.name} (already exists)")
            else:
                if create_missing:
                    click.echo(f"  CREATE: {match.local.name}")
                else:
                    click.echo(f"  SKIP:   {match.local.name} (not found)")
        return

    # Perform import
    click.echo("Importing data sources to cloud...")
    updated_entries, result = service.import_to_cloud(
        data_source_file.data_sources,
        create_missing=create_missing,
        update_existing=update_existing,
        match_by=match_by,
    )

    # Display results
    click.echo(f"\nImport results:")
    click.echo(f"  Matched:  {result.matched}")
    click.echo(f"  Created:  {result.created}")
    click.echo(f"  Updated:  {result.updated}")
    if result.skipped_duplicates:
        click.echo(f"  Skipped (duplicate source_uri): {result.skipped_duplicates}")
    click.echo(f"  Failed:   {result.failed}")

    if result.skipped_reasons:
        click.echo("\nSkipped:")
        for reason in result.skipped_reasons:
            click.echo(f"  - {reason}")

    if result.errors:
        click.echo("\nErrors:")
        for error in result.errors:
            click.echo(f"  - {error}", err=True)

    # Update file with new entries
    data_source_file.data_sources = updated_entries
    service.save_file(output_path, data_source_file)
    click.echo(f"\nSaved updated data sources to {output_path}")

    # Exit with error code if there were any failures
    if result.failed > 0 or result.errors:
        sys.exit(1)


@datasource_group.group("template")
def template_group():
    """Manage data source templates."""
    pass


@template_group.command("list")
@click.pass_context
def list_templates(ctx):
    """List available templates."""
    client = ctx.obj["client"]
    service = DataSourceService(client)

    templates = service.list_templates()

    if not templates:
        click.echo("No templates found.")
        return

    click.echo(f"Available templates ({len(templates)}):")
    for t in templates:
        click.echo(f"  - {t}")


@template_group.command("show")
@click.argument("template_name")
@click.pass_context
def show_template(ctx, template_name: str):
    """Show details of a template."""
    client = ctx.obj["client"]
    service = DataSourceService(client)

    template = service.load_template(template_name)

    if not template:
        click.echo(f"Error: Template '{template_name}' not found", err=True)
        sys.exit(1)

    click.echo(f"Template: {template.name}")
    click.echo(f"Description: {template.description}")
    click.echo(f"URI Pattern: {template.source_uri_pattern}")
    if template.default_port:
        click.echo(f"Default Port: {template.default_port}")
    if template.default_path:
        click.echo(f"Default Path: {template.default_path}")
