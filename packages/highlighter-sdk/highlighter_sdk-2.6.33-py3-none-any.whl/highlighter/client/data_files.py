import logging
import threading
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional, Union
from uuid import UUID

from highlighter.cli.cli_logging import COLOURS, RESET, format_timing

from ..core import GQLBaseModel, paginate
from .aws_s3 import upload_file_to_s3
from .base_models import Image as ImageType
from .base_models import PageInfo
from .gql_client import HLClient

__all__ = [
    "get_data_files",
    "create_data_file",
]

BYTES_PER_MEGABYTE = 1_000_000
BITS_PER_MEGABIT = 1_000_000


def get_data_files(
    client,
    data_file_ids: Optional[List[int]] = None,
    data_file_uuids: Optional[List[Union[str, UUID]]] = None,
    data_source_id: Optional[List[int]] = None,
    data_source_uuid: Optional[List[str]] = None,
    file_hash: Optional[List[str]] = None,
):
    class ImageTypeConnection(GQLBaseModel):
        page_info: PageInfo
        nodes: List[ImageType]

    kwargs = {
        "id": data_file_ids,
        "uuid": data_file_uuids,
        "dataSourceId": data_source_id,
        "dataSourceUuid": data_source_uuid,
        "fileHash": file_hash,
    }
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    return paginate(client.imageConnection, ImageTypeConnection, **kwargs)


def create_data_file(
    client: HLClient,
    data_file_path: Union[str, Path],
    data_source_uuid: UUID,
    site_id: Optional[str] = None,
    observed_timezone: Optional[str] = None,
    recorded_at: Optional[str] = None,
    recorded_until: Optional[datetime] = None,
    metadata: str = "{}",
    uuid: Optional[str] = None,
    multipart_filesize: Optional[str] = None,
    content_type: str = "image",
) -> ImageType:
    logger = logging.getLogger(__name__)
    current_thread = threading.current_thread()
    thread_id = current_thread.ident
    thread_name = current_thread.name

    data_file_path = Path(data_file_path)
    if not data_file_path.exists():
        raise FileNotFoundError(f"{data_file_path}")

    # Get file size for context
    file_size_bytes = data_file_path.stat().st_size
    file_size_mb = file_size_bytes / BYTES_PER_MEGABYTE

    # Time the S3 upload
    logger.debug(
        f"[Thread {thread_id}/{thread_name}] Starting S3 upload for {data_file_path.name} ({file_size_mb:.2f} MB)"
    )
    s3_upload_start = time.perf_counter()
    file_data = upload_file_to_s3(
        client,
        str(data_file_path),
        multipart_filesize=multipart_filesize,
        data_source_uuid=str(data_source_uuid),
    )
    s3_upload_elapsed = time.perf_counter() - s3_upload_start
    upload_mbps = (
        (file_size_bytes * 8) / (s3_upload_elapsed * BITS_PER_MEGABIT) if s3_upload_elapsed > 0 else 0
    )
    logger.debug(
        f"[Thread {thread_id}/{thread_name}] S3 upload for {data_file_path.name} took {s3_upload_elapsed:.3f}s"
    )

    if recorded_at is None:
        recorded_at = datetime.now(timezone.utc).isoformat()

    class CreateImageResponse(GQLBaseModel):
        image: Optional[ImageType] = None
        errors: Any = None

    # Time the GraphQL API call
    logger.debug(
        f"[Thread {thread_id}/{thread_name}] Starting GraphQL create_image for {data_file_path.name}"
    )
    api_call_start = time.perf_counter()
    create_data_file_response = client.create_image(
        return_type=CreateImageResponse,
        dataSourceUuid=str(data_source_uuid),
        originalSourceUrl=str(data_file_path),
        fileData=file_data,
        siteId=site_id,
        observedTimezone=observed_timezone,
        recordedAt=recorded_at,
        recordedUntil=recorded_until,
        metadata=metadata,
        uuid=uuid,
        contentType=content_type,
    )
    api_call_elapsed = time.perf_counter() - api_call_start

    # Format thread info with color
    thread_info = f"{COLOURS['grey']}[Thread {thread_id}/{thread_name}]{RESET}"

    # Format timings with colors
    timing_s3 = format_timing("S3", s3_upload_elapsed, "s", color_threshold={"fast": 1.0, "slow": 5.0})
    timing_graphql = format_timing(
        "GraphQL", api_call_elapsed, "s", color_threshold={"fast": 0.5, "slow": 2.0}
    )

    # Single consolidated log line with all timing information
    logger.info(
        f"{thread_info} {data_file_path.name} | " f"{timing_s3}({upload_mbps:.1f}Mbps) {timing_graphql}"
    )

    errors = create_data_file_response.errors
    if errors:
        # If it's a string, just raise it
        if isinstance(errors, str):
            raise ValueError(errors)
        # If it's an iterable (e.g. list of strings)
        elif isinstance(errors, (list, tuple)):
            raise ValueError(". ".join(str(e) for e in errors))
        # If it's something else, convert to string
        else:
            raise ValueError(str(errors))
    return create_data_file_response.image
