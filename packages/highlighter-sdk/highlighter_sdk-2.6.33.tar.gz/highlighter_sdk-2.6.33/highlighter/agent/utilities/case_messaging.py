"""
Case messaging utilities for machine agents.

Provides helpers for agents to send messages to cases during task execution.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

from highlighter.client import HLClient
from highlighter.client.base_models.base_models import (
    CreateCaseMessagePayload,
    MessageType,
    TaskType,
)

logger = logging.getLogger(__name__)


class CaseMessageRateLimiter:
    """Rate limiter for case messages to prevent flooding."""

    def __init__(
        self,
        max_messages_per_case: int = 10,
        time_window_seconds: float = 300.0,  # 5 minutes
    ):
        """
        Initialize rate limiter.

        Args:
            max_messages_per_case: Maximum number of messages per case within time window
            time_window_seconds: Time window in seconds for rate limiting
        """
        self.max_messages = max_messages_per_case
        self.time_window = time_window_seconds
        self._message_timestamps: Dict[str, list] = {}

    def check_and_record(self, case_id: str) -> bool:
        """
        Check if a message can be sent to the case and record the timestamp.

        Args:
            case_id: The case ID to check

        Returns:
            True if message can be sent, False if rate limit exceeded
        """
        current_time = time.time()
        cutoff_time = current_time - self.time_window

        # Initialize list for case if not exists
        if case_id not in self._message_timestamps:
            self._message_timestamps[case_id] = []

        # Remove old timestamps outside the time window
        self._message_timestamps[case_id] = [
            ts for ts in self._message_timestamps[case_id] if ts > cutoff_time
        ]

        # Check if under limit
        if len(self._message_timestamps[case_id]) >= self.max_messages:
            return False

        # Record this message timestamp
        self._message_timestamps[case_id].append(current_time)
        return True


class CaseMessenger:
    """Helper for sending messages to cases from machine agents."""

    def __init__(
        self,
        client: Optional[HLClient] = None,
        enabled: bool = True,
        max_messages_per_case: int = 10,
        time_window_seconds: float = 300.0,
    ):
        """
        Initialize case messenger.

        Args:
            client: HLClient instance. If None, will use HLClient.get_client()
            enabled: Whether messaging is enabled
            max_messages_per_case: Maximum messages per case in time window
            time_window_seconds: Time window for rate limiting in seconds (default 5 minutes)
        """
        self.client = client
        self.enabled = enabled
        self.rate_limiter = CaseMessageRateLimiter(max_messages_per_case, time_window_seconds)
        self._no_case_warnings: set = set()  # Track tasks we've warned about

    def _get_client(self) -> HLClient:
        """Lazily acquire the HLClient to avoid requiring credentials at import time."""
        if self.client is None:
            self.client = HLClient.get_client()
        return self.client

    def send_message(
        self,
        task: TaskType,
        content: str,
        force: bool = False,
    ) -> Optional[MessageType]:
        """
        Send a message to the case associated with a task.

        Args:
            task: The task being processed
            content: Message content to send
            force: If True, bypass rate limiting

        Returns:
            The created message if successful, None otherwise
        """
        if not self.enabled:
            logger.debug("Case messaging is disabled")
            return None

        # Check if task has an associated case
        if not task.case or not task.case.id:
            # Log warning once per task
            if task.id not in self._no_case_warnings:
                logger.warning(
                    f"Task {task.id} has no associated case. Cannot send message. "
                    "This warning will only be shown once per task."
                )
                self._no_case_warnings.add(task.id)
            return None

        case_id = task.case.id

        # Check rate limit unless forced
        if not force:
            if not self.rate_limiter.check_and_record(case_id):
                logger.warning(
                    f"Rate limit exceeded for case {case_id}. Message not sent: '{content[:100]}...'"
                )
                return None

        try:
            # Send message via GraphQL mutation
            client = self._get_client()
            result = client.createCaseMessage(
                return_type=CreateCaseMessagePayload,
                caseId=case_id,
                content=content,
            )

            if result.errors:
                logger.error(f"Failed to send message to case {case_id}: {result.errors}")
                return None

            if result.user_message:
                logger.info(f"Sent message to case {case_id}: '{content[:100]}...'")
                return result.user_message
            else:
                logger.warning(f"No message returned after sending to case {case_id}")
                return None

        except Exception as e:
            logger.error(f"Error sending message to case {case_id}: {e}", exc_info=True)
            return None

    def send_status_message(
        self,
        task: TaskType,
        status: str,
        details: Optional[str] = None,
    ) -> Optional[MessageType]:
        """
        Send a status update message to the case.

        Args:
            task: The task being processed
            status: Status to report (e.g., "started", "processing", "completed")
            details: Optional additional details

        Returns:
            The created message if successful, None otherwise
        """
        agent_name = getattr(task, "name", "Agent")
        content = f"[{agent_name}] Status: {status}"
        if details:
            content += f" - {details}"

        return self.send_message(task, content)

    def send_error_message(
        self,
        task: TaskType,
        error: str,
    ) -> Optional[MessageType]:
        """
        Send an error message to the case.

        Args:
            task: The task being processed
            error: Error message to send

        Returns:
            The created message if successful, None otherwise
        """
        agent_name = getattr(task, "name", "Agent")
        content = f"[{agent_name}] Error: {error}"

        # Use force=True for error messages to bypass rate limiting
        return self.send_message(task, content, force=True)


# Global default messenger is created eagerly so instantiation is import-time serialized
_default_messenger = CaseMessenger()


def get_case_messenger() -> CaseMessenger:
    """Return the shared CaseMessenger instance with rate limiting state."""
    return _default_messenger


def send_case_message(
    task: TaskType,
    content: str,
    client: Optional[HLClient] = None,
) -> Optional[MessageType]:
    """
    Convenience function to send a message to a case.

    Note:
        Supplying a custom ``client`` creates a one-off CaseMessenger with its own
        rate limiter state. To reuse rate limiting across calls, rely on the
        shared messenger by omitting the ``client`` argument or manage a dedicated
        ``CaseMessenger`` instance yourself.

    Args:
        task: The task being processed
        content: Message content
        client: Optional HLClient instance

    Returns:
        The created message if successful, None otherwise
    """
    messenger = CaseMessenger(client=client) if client else get_case_messenger()
    return messenger.send_message(task, content)
