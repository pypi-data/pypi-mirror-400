"""Service layer for data source operations."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional, Sequence, Tuple
from uuid import UUID

from highlighter.client import HLClient
from highlighter.client.base_models.base_models import DataSourceType
from highlighter.core.gql_base_model import GQLBaseModel
from highlighter.datasource.models import (
    DataSourceTemplate,
    LocalDataSourceEntry,
    LocalDataSourceFile,
    MatchedDataSource,
    SyncResult,
)
from highlighter.network.mdns import DiscoveredDevice, DiscoveryConfig, discover_devices


class DataSourceService:
    """Service for managing data sources."""

    def __init__(self, client: HLClient):
        self.client = client

    def discover_to_datasources(
        self,
        config: DiscoveryConfig,
        resolve_macs: bool,
        template_obj: Optional[DataSourceTemplate] = None,
        uri_pattern: Optional[str] = None,
        name_pattern: Optional[str] = None,
    ) -> List[LocalDataSourceEntry]:
        """Run mDNS discovery and convert devices to data source entries.

        Args:
            config: Discovery configuration
            resolve_macs: Whether to resolve MAC addresses
            template_obj: Optional template to apply (uses template defaults)
            uri_pattern: Optional URI pattern (only used when template_obj is None)
            name_pattern: Optional name pattern (only used when template_obj is None)

        Returns:
            List of data source entries

        Raises:
            ValueError: If neither template_obj nor uri_pattern is provided
        """
        if template_obj is None and uri_pattern is None:
            raise ValueError("Either template_obj or uri_pattern must be provided")

        devices = discover_devices(config=config, resolve_macs=resolve_macs)

        entries = []
        for device in devices:
            if template_obj:
                # Template mode: use apply_template which handles defaults
                entry = self.apply_template(template_obj, device)
            else:
                # Pattern mode: use custom patterns
                placeholders = {
                    "ip": device.ip or "",
                    "hostname": device.hostname or "",
                    "port": device.port or "",
                    "serial": device.serial or "",
                    "mac": device.mac or "",
                    "service_name": device.service_name or "",
                }

                # Generate source URI and name
                source_uri = uri_pattern.format(**placeholders)
                name = name_pattern.format(**placeholders)

                entry = LocalDataSourceEntry(
                    name=name,
                    source_uri=source_uri,
                    mac=device.mac,
                    serial=device.serial,
                    hostname=device.hostname,
                    ip=device.ip,
                    port=device.port,
                    template=None,
                )

            entries.append(entry)

        return entries

    def load_file(self, file_path: Path) -> LocalDataSourceFile:
        """Load and validate a local data source file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return LocalDataSourceFile(**data)

    def save_file(self, file_path: Path, data_source_file: LocalDataSourceFile) -> None:
        """Save data source entries to a JSON file."""
        # Update metadata
        data_source_file.metadata.updated_at = datetime.now()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                data_source_file.model_dump(mode="json", exclude_none=False),
                f,
                indent=2,
                default=str,
            )

    def fetch_from_cloud(self, limit: Optional[int] = None) -> List[DataSourceType]:
        """Query cloud for all data sources with optional limit.

        Tries the paginated `dataSourcesConnection` endpoint; falls back to
        the legacy `dataSources` list if the connection query is unavailable.

        Args:
            limit: Maximum number of data sources to return (None fetches all).
        """

        class PageInfo(GQLBaseModel):
            has_next_page: bool
            end_cursor: Optional[str] = None

        class DataSourceEdge(GQLBaseModel):
            node: DataSourceType

        class DataSourcesConnection(GQLBaseModel):
            edges: List[DataSourceEdge]
            page_info: PageInfo

        page_size = 100
        after = None
        all_sources: List[DataSourceType] = []

        try:
            while True:
                kwargs = {"first": page_size}
                if after:
                    kwargs["after"] = after

                result = self.client.data_sources_connection(return_type=DataSourcesConnection, **kwargs)

                all_sources.extend(edge.node for edge in result.edges)

                if limit and len(all_sources) >= limit:
                    return all_sources[:limit]

                if not result.page_info.has_next_page:
                    break

                after = result.page_info.end_cursor

            return all_sources
        except ValueError as exc:
            # Backward compatibility when the connection query is not supported
            if "dataSourcesConnection" not in str(exc):
                raise

            sources = self.client.data_sources(return_type=List[DataSourceType])
            if limit is not None:
                return sources[:limit]
            return sources

    def get_by_id(self, data_source_id: int) -> Optional[DataSourceType]:
        """Get a single data source by ID."""
        try:
            return self.client.data_source(return_type=DataSourceType, id=data_source_id)
        except Exception:
            return None

    def get_by_uuid(self, data_source_uuid: UUID) -> Optional[DataSourceType]:
        """Get a single data source by UUID."""
        try:
            return self.client.data_source(return_type=DataSourceType, uuid=str(data_source_uuid))
        except Exception:
            return None

    def get_by_name(self, name: str) -> Optional[DataSourceType]:
        """Get a single data source by name.

        Note: Returns the first match if multiple data sources have the same name.
        """
        all_sources = self.fetch_from_cloud()
        for source in all_sources:
            if source.name == name:
                return source
        return None

    def create(
        self, name: str, source_uri: Optional[str] = None, uuid: Optional[UUID] = None
    ) -> DataSourceType:
        """Create a single data source in the cloud."""

        class CreateDataSourcePayload(GQLBaseModel):
            data_source: Optional[DataSourceType]
            errors: List[str]

        kwargs = {"name": name}
        if uuid:
            kwargs["uuid"] = str(uuid)
        if source_uri:
            # GraphQL expects camelCase
            kwargs["sourceUri"] = source_uri

        response = self.client.create_data_source(return_type=CreateDataSourcePayload, **kwargs)

        if response.errors:
            raise ValueError(f"Failed to create data source: {response.errors}")

        return response.data_source

    def update(
        self,
        data_source_id: Optional[int] = None,
        data_source_uuid: Optional[UUID] = None,
        name: Optional[str] = None,
        source_uri: Optional[str] = None,
    ) -> DataSourceType:
        """Update an existing data source in the cloud."""

        class UpdateDataSourcePayload(GQLBaseModel):
            data_source: Optional[DataSourceType]
            errors: List[str]

        kwargs = {}
        if data_source_id:
            kwargs["id"] = data_source_id
        elif data_source_uuid:
            kwargs["uuid"] = str(data_source_uuid)

        if name:
            kwargs["name"] = name
        if source_uri:
            kwargs["sourceUri"] = source_uri

        response = self.client.update_data_source(return_type=UpdateDataSourcePayload, **kwargs)

        if response.errors:
            raise ValueError(f"Failed to update data source: {response.errors}")

        return response.data_source

    def destroy(self, data_source_id: Optional[int] = None, data_source_uuid: Optional[UUID] = None) -> bool:
        """Delete a data source from the cloud."""

        class DeleteDataSourcePayload(GQLBaseModel):
            success: bool
            errors: List[str]

        kwargs = {}
        if data_source_id:
            kwargs["id"] = data_source_id
        elif data_source_uuid:
            kwargs["uuid"] = str(data_source_uuid)

        response = self.client.delete_data_source(return_type=DeleteDataSourcePayload, **kwargs)

        if response.errors:
            raise ValueError(f"Failed to delete data source: {response.errors}")

        return response.success

    def match_entries(
        self,
        local_entries: List[LocalDataSourceEntry],
        cloud_sources: List[DataSourceType],
        match_by: Literal["id", "uuid", "name", "source_uri", "auto"] = "auto",
    ) -> List[MatchedDataSource]:
        """Match local data source entries against cloud data sources."""
        matches = []

        # Create lookup dictionaries for cloud sources
        by_id: Dict[int, DataSourceType] = {s.id: s for s in cloud_sources}
        by_uuid: Dict[UUID, DataSourceType] = {s.uuid: s for s in cloud_sources}
        by_name: Dict[str, DataSourceType] = {s.name: s for s in cloud_sources}
        by_source_uri: Dict[str, DataSourceType] = {
            getattr(s, "source_uri", None): s for s in cloud_sources if getattr(s, "source_uri", None)
        }

        for entry in local_entries:
            matched = MatchedDataSource(local=entry)

            if match_by == "auto":
                # Try matching in order: id -> uuid -> source_uri -> name
                if entry.id and entry.id in by_id:
                    matched.cloud = by_id[entry.id]
                    matched.match_type = "id"
                    matched.is_matched = True
                elif entry.uuid and entry.uuid in by_uuid:
                    matched.cloud = by_uuid[entry.uuid]
                    matched.match_type = "uuid"
                    matched.is_matched = True
                elif entry.source_uri and entry.source_uri in by_source_uri:
                    matched.cloud = by_source_uri[entry.source_uri]
                    matched.match_type = "source_uri"
                    matched.is_matched = True
                elif entry.name in by_name:
                    matched.cloud = by_name[entry.name]
                    matched.match_type = "name"
                    matched.is_matched = True
            elif match_by == "id" and entry.id and entry.id in by_id:
                matched.cloud = by_id[entry.id]
                matched.match_type = "id"
                matched.is_matched = True
            elif match_by == "uuid" and entry.uuid and entry.uuid in by_uuid:
                matched.cloud = by_uuid[entry.uuid]
                matched.match_type = "uuid"
                matched.is_matched = True
            elif match_by == "source_uri" and entry.source_uri and entry.source_uri in by_source_uri:
                matched.cloud = by_source_uri[entry.source_uri]
                matched.match_type = "source_uri"
                matched.is_matched = True
            elif match_by == "name" and entry.name in by_name:
                matched.cloud = by_name[entry.name]
                matched.match_type = "name"
                matched.is_matched = True

            matches.append(matched)

        return matches

    def import_to_cloud(
        self,
        entries: List[LocalDataSourceEntry],
        create_missing: bool = False,
        update_existing: bool = False,
        match_by: Literal["id", "uuid", "name", "source_uri", "auto"] = "auto",
    ) -> Tuple[List[LocalDataSourceEntry], SyncResult]:
        """Import data sources to cloud, optionally creating or updating."""
        cloud_sources = self.fetch_from_cloud()
        matches = self.match_entries(entries, cloud_sources, match_by)

        result = SyncResult()
        updated_entries = []

        for match in matches:
            try:
                if match.is_matched:
                    result.matched += 1
                    # Update cloud ID/UUID in local entry
                    match.local.id = match.cloud.id
                    match.local.uuid = match.cloud.uuid

                    if match.match_type == "source_uri" and create_missing and not update_existing:
                        result.skipped_duplicates += 1
                        result.skipped_reasons.append(
                            f"Skipping create: source_uri '{match.local.source_uri}' already exists in cloud "
                            f"(id={match.cloud.id}, name={match.cloud.name})"
                        )

                    if update_existing:
                        # Update the cloud entry
                        self.update(
                            data_source_id=match.cloud.id,
                            name=match.local.name,
                            source_uri=match.local.source_uri,
                        )
                        result.updated += 1

                    updated_entries.append(match.local)
                else:
                    # No match found
                    if create_missing:
                        # Create new data source (no source_uri dedupe unless matched above)
                        created = self.create(name=match.local.name, source_uri=match.local.source_uri)
                        match.local.id = created.id
                        match.local.uuid = created.uuid
                        result.created += 1

                    updated_entries.append(match.local)

            except Exception as e:
                result.failed += 1
                result.errors.append(f"Failed to process {match.local.name}: {str(e)}")
                updated_entries.append(match.local)

        return updated_entries, result

    def apply_template(
        self, template: DataSourceTemplate, device: DiscoveredDevice, requested_name: Optional[str] = None
    ) -> LocalDataSourceEntry:
        """Apply a template to generate a data source entry from a discovered device.

        Applies template defaults and persists the resolved values in the entry fields.
        Validates required fields according to template definition.

        Args:
            template: Template with field requirements and defaults
            device: Discovered device

        Raises:
            ValueError: If required template fields are missing from device
        """
        # Map device attributes to template field names
        device_values = {
            "ip": device.ip,
            "hostname": device.hostname,
            "port": device.port,
            "serial": device.serial,
            "mac": device.mac,
            "name": device.service_name,
        }

        # Validate required fields (skip generated fields like source_uri)
        generated_fields = {"source_uri"}  # These are generated by the template, not from device
        missing_fields = []
        for field_name, field_def in template.fields.items():
            if field_def.required and field_name not in generated_fields:
                value = device_values.get(field_name)
                # Check if value is None or empty string
                if not value:
                    # Check if there's a default in the template
                    has_default = field_def.default is not None
                    # Check if there's a default_port/default_path for specific fields
                    has_template_default = (field_name == "port" and template.default_port) or (
                        field_name == "path" and template.default_path
                    )
                    if not has_default and not has_template_default:
                        missing_fields.append(field_name)

        if missing_fields:
            device_desc = device.service_name or device.ip or "unknown"
            raise ValueError(
                f"Device '{device_desc}' is missing required template fields: {', '.join(missing_fields)}"
            )

        # Resolve values with template defaults
        resolved_port = device.port or (str(template.default_port) if template.default_port else None)

        # Build placeholders for URI/name generation
        base_name = requested_name or device.service_name or ""

        placeholders = {
            "ip": device.ip or "",
            "hostname": device.hostname or "",
            "port": resolved_port or "",
            "serial": device.serial or "",
            "mac": device.mac or "",
            "path": template.default_path or "",
            "name": base_name,
            "service_name": base_name,
        }

        source_uri = template.source_uri_pattern.format(**placeholders)
        if template.name_pattern:
            entry_name = template.name_pattern.format(**placeholders)
        else:
            entry_name = base_name or "Unknown Device"

        # Persist the resolved port value (not the original device.port which may be None)
        return LocalDataSourceEntry(
            name=entry_name,
            source_uri=source_uri,
            mac=device.mac,
            serial=device.serial,
            hostname=device.hostname,
            ip=device.ip,
            port=resolved_port,  # Use resolved value with template defaults
            template=template.name,
        )

    def load_template(self, template_name: str) -> Optional[DataSourceTemplate]:
        """Load a template by name from built-in or a user-provided JSON file path."""
        # First check built-in templates
        builtin_path = Path(__file__).parent / "templates" / f"{template_name}.json"
        if builtin_path.exists():
            with open(builtin_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return DataSourceTemplate(**data)

        # Then check user-provided path
        candidate_paths = []
        raw_path = Path(template_name)
        candidate_paths.append(raw_path)
        if raw_path.suffix == "":
            candidate_paths.append(raw_path.with_suffix(".json"))

        for path in candidate_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return DataSourceTemplate(**data)

        return None

    def list_templates(self) -> List[str]:
        """List available template names."""
        templates_dir = Path(__file__).parent / "templates"
        if not templates_dir.exists():
            return []

        return [p.stem for p in templates_dir.glob("*.json")]
