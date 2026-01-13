import logging
import threading
import time
from typing import List, Optional, Union
from uuid import UUID

from ..core import paginate
from .base_models import ImageConnection
from .base_models import ImagePresigned as ImagePresignedType
from .gql_client import HLClient

__all__ = [
    "get_presigned_url",
    "get_presigned_urls",
]


def get_presigned_url(
    client: HLClient,
    id: int,
):
    """Return a single ImagePresignedType BaseModel
    for the given file id
    """
    logger = logging.getLogger(__name__)
    current_thread = threading.current_thread()
    thread_id = current_thread.ident
    thread_name = current_thread.name

    logger.debug(f"[Thread {thread_id}/{thread_name}] Calling client.image() for id={id}")
    start = time.perf_counter()
    result = client.image(
        return_type=ImagePresignedType,
        id=id,
    )
    elapsed = time.perf_counter() - start
    logger.info(f"[Thread {thread_id}/{thread_name}] client.image() took {elapsed:.3f}s")
    return result


def get_presigned_urls(
    client,
    ids: List[int],
    uuids: List[Union[UUID, str]],
):
    """Return a generator of ImagePresignedType GQLBaseModels
    for the given list of file ids
    """
    kwargs = {}
    if ids:
        kwargs["id"] = ids
    if uuids:
        kwargs["uuid"] = uuids

    return paginate(
        client.imageConnection,
        ImageConnection,
        **kwargs,
    )
