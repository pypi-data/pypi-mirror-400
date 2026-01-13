"""Data models for data source management."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class LocalDataSourceEntry(BaseModel):
    """Represents a single data source entry in a local file."""

    id: Optional[int] = Field(default=None, description="Cloud data source ID")
    uuid: Optional[UUID] = Field(default=None, description="Cloud data source UUID")
    name: str = Field(description="Data source name")
    source_uri: Optional[str] = Field(
        default=None, description="Source URI (e.g., rtsp://hostname:554/stream)"
    )
    mac: Optional[str] = Field(default=None, description="Device MAC address")
    serial: Optional[str] = Field(default=None, description="Device serial number")
    hostname: Optional[str] = Field(default=None, description="Device hostname")
    ip: Optional[str] = Field(default=None, description="Device IP address")
    port: Optional[str] = Field(default=None, description="Device port")
    template: Optional[str] = Field(default=None, description="Template name used")


class DataSourceMetadata(BaseModel):
    """Metadata for a data source file."""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LocalDataSourceFile(BaseModel):
    """Represents a local data source file structure."""

    data_sources: List[LocalDataSourceEntry] = Field(default_factory=list)
    template: Optional[str] = Field(default=None, description="Default template for all entries")
    metadata: DataSourceMetadata = Field(default_factory=DataSourceMetadata)


class DataSourceTemplateField(BaseModel):
    """Field definition in a template."""

    required: bool = False
    type: str = "string"
    default: Optional[Any] = None


class DataSourceTemplate(BaseModel):
    """Template for creating data sources."""

    name: str
    description: str
    source_uri_pattern: str = Field(
        description="URI pattern with placeholders like {ip}, {hostname}, {port}, {serial}, {mac}, {name}"
    )
    name_pattern: Optional[str] = Field(
        default=None,
        description="Optional name pattern with placeholders like {name}, {hostname}, {ip}",
    )
    default_port: Optional[int] = None
    default_path: Optional[str] = None
    fields: Dict[str, DataSourceTemplateField] = Field(default_factory=dict)


@dataclass
class SyncResult:
    """Result of a sync or import operation."""

    matched: int = 0
    created: int = 0
    updated: int = 0
    failed: int = 0
    skipped_duplicates: int = 0
    errors: List[str] = None
    skipped_reasons: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.skipped_reasons is None:
            self.skipped_reasons = []


@dataclass
class MatchedDataSource:
    """A data source that has been matched between local and cloud."""

    local: LocalDataSourceEntry
    cloud: Optional[Any] = None  # DataSourceType from cloud
    match_type: Optional[Literal["id", "uuid", "name", "source_uri"]] = None
    is_matched: bool = False
