from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from highlighter.client.assessments import finalise
from highlighter.client.base_models.base_models import CaseType, TaskType
from highlighter.client.gql_client import HLClient, get_threadsafe_hlclient
from highlighter.core.gql_base_model import GQLBaseModel

if TYPE_CHECKING:
    from highlighter.agent.capabilities.recorder import Recorder

logger = logging.getLogger(__name__)

__all__ = [
    "update_task_status",
    "update_task",
    "lease_task",
    "lease_tasks_from_steps",
]


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"

    @staticmethod
    def validate_str(s) -> bool:
        return s in [s.value for s in TaskStatus]


class UpdateTaskResultPayload(GQLBaseModel):
    submission: CreateSubmissionNotFinalisedPayload.SubmissionType
    errors: List[Any]


class Case(GQLBaseModel):
    class CaseSubmission(GQLBaseModel):
        class DataFile(GQLBaseModel):
            uuid: str
            original_source_url: str
            file_url_original: str
            content_type: str

        id: str
        uuid: UUID
        data_files: List[DataFile]

    id: str
    latest_submission: CaseSubmission
    entity_id: Optional[str] = None


class Task(GQLBaseModel):
    id: str
    status: Optional[TaskStatus] = None
    case: Optional[Case] = None
    leased_until: Optional[datetime] = None
    parameters: Optional[Dict[str, Any]] = None


def update_task_status(
    client: HLClient,
    task_id: str,
    status: Union[str, TaskStatus],
    message: Optional[str] = None,
):

    assert isinstance(status, TaskStatus) or TaskStatus.validate_str(status), f"Got: {status}"

    class UpdateTaskStatusResponse(GQLBaseModel):
        errors: List[Any]

    kwargs = {
        "id": task_id,
        "status": status,
    }
    if message is not None:
        kwargs["message"] = message

    response = client.update_task_status(return_type=UpdateTaskStatusResponse, **kwargs)
    if response.errors:
        raise ValueError(f"{response.errors}")

    return response


def update_task(
    client: HLClient,
    task_id: Union[UUID, str],
    status: Optional[Union[str, TaskStatus]] = None,
    leased_until: Optional[Union[datetime, str]] = None,
    lease_sec: Optional[int] = None,
    **kwargs,
) -> Task:

    if lease_sec:
        assert leased_until is None, "Cannot use both leased_until and lease_sec"
        leased_until = (datetime.now(UTC) + timedelta(seconds=lease_sec)).isoformat()

    if isinstance(leased_until, datetime):
        leased_until = leased_until.isoformat()

    class TaskResponse(GQLBaseModel):
        task: Task
        errors: Any

    kwargs = dict(
        id=str(task_id),
        status=status,
        leasedUntil=leased_until,
        **kwargs,
    )

    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    response = client.updateTask(return_type=TaskResponse, **kwargs)

    if response.errors:
        raise ValueError(f"Errors: {response.errors}")

    return response.task


def lease_task(
    client: HLClient,
    task_id: Union[UUID, str],
    set_status_to: Optional[Union[str, TaskStatus]] = None,
    leased_until: Optional[Union[datetime, str]] = None,
    lease_sec: Optional[float] = None,
) -> Task:

    if lease_sec:
        assert leased_until is None, "Cannot use both leased_until and lease_sec"
        leased_until = (datetime.now(UTC) + timedelta(seconds=lease_sec)).isoformat()

    if isinstance(leased_until, datetime):
        leased_until = leased_until.isoformat()

    class TaskResponse(GQLBaseModel):
        task: Task
        errors: Any

    update_task_args = {"id": str(task_id), "leasedUntil": leased_until}
    if set_status_to is not None:
        update_task_args["status"] = set_status_to
    response = client.updateTask(return_type=TaskResponse, **update_task_args)
    if response.errors:
        raise ValueError(f"Errors: {response.errors}")
    return response.task


def lease_tasks_from_steps(
    client: HLClient,
    step_ids: List[Union[UUID, str]],
    count: int = 1,
    filter_by_status: Optional[Union[str, TaskStatus]] = None,
    set_status_to: Optional[Union[str, TaskStatus]] = None,
    leased_until: Optional[Union[datetime, str]] = None,
    lease_sec: Optional[float] = None,
    filter_by_task_id: Optional[List[UUID]] = None,
) -> List[Task]:

    if filter_by_status:
        assert isinstance(filter_by_status, TaskStatus) or TaskStatus.validate_str(filter_by_status)

    if set_status_to:
        assert isinstance(set_status_to, TaskStatus) or TaskStatus.validate_str(set_status_to)

    if lease_sec:
        assert leased_until is None, "Cannot use both leased_until and lease_sec"
        leased_until = (datetime.now(UTC) + timedelta(seconds=lease_sec)).isoformat()

    if isinstance(leased_until, datetime):
        leased_until = leased_until.isoformat()

    class TaskResponse(GQLBaseModel):
        errors: List[Any]
        tasks: List[Task]

    response = client.leaseTasksFromSteps(
        return_type=TaskResponse,
        stepIds=[str(s) for s in step_ids],
        count=count,
        leasedUntil=leased_until,
    )

    if len(response.errors) > 0:
        raise ValueError(response.errors)

    if filter_by_status:
        tasks = [t for t in response.tasks if t.status == filter_by_status]
    else:
        tasks = response.tasks

    if filter_by_task_id:
        task_ids = []

        for i in filter_by_task_id:
            if isinstance(i, str):
                task_ids.append(i)
            elif isinstance(i, UUID):
                task_ids.append(str(i))
            else:
                raise ValueError()

        tasks = [t for t in tasks if t.id in task_ids]

    if set_status_to:
        for task in tasks:
            _ = update_task_status(client, task.id, set_status_to)
    return tasks


# FIXME: (Josh). Should the be merged with TaskType? We have 2 modes of using Task
# one for Gql and the other for Agents. I think they should be one-in-the-same.


@dataclass
class ProcessorState:
    """Lock-free coordination record shared between TaskContext and Recorder workers."""

    processor: "Recorder"  # forward-declared to avoid import cycle
    submission: CreateSubmissionNotFinalisedPayload.SubmissionType
    case_id: Optional[str] = None  # Case ID for logging and tracking
    pending_chunks: int = 0
    stopping: bool = False
    finished: bool = False
    error: Optional[BaseException] = None


@dataclass
class RecordingSession:
    """Tracks the processors contributing to a submission and their progress."""

    submission: CreateSubmissionNotFinalisedPayload.SubmissionType
    case_id: str
    processors: List[ProcessorState] = field(default_factory=list)

    def all_finished(self) -> bool:
        return all(p.finished for p in self.processors)

    def has_error(self) -> bool:
        return any(p.error is not None for p in self.processors)

    def iter_errors(self):
        for state in self.processors:
            if state.error is not None:
                yield state


class TaskContext:

    def __init__(
        self,
    ):
        self._recording = deque()
        self.logger = logging.getLogger(__name__)
        self._hl_credentials: Optional[Tuple[str, str]] = None

    def _get_threadsafe_hl_client(self) -> HLClient:
        """Lazily capture credentials and return a thread-local HLClient."""
        if self._hl_credentials is None:
            base_client = HLClient.get_client()
            self._hl_credentials = (base_client.api_token, base_client.endpoint_url)

        api_token, endpoint_url = self._hl_credentials
        return get_threadsafe_hlclient(api_token, endpoint_url)

    def start_recording(
        self,
        dsps_to_record,
        workflow_order_id: UUID,
        case_name: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        *,
        log_context: Optional[str] = None,
    ):
        client = self._get_threadsafe_hl_client()
        case, sub = create_empty_case_with_not_finalized_submission(
            client,
            workflow_order_id,
            case_name=case_name,
            entity_id=entity_id,
            log_context=log_context,
        )
        session = RecordingSession(submission=sub, case_id=case.id)
        for dsp in dsps_to_record:
            processor_state = ProcessorState(processor=dsp, submission=sub, case_id=case.id)
            session.processors.append(processor_state)
            dsp.start_recording(sub, processor_state)

        prefix = f"{log_context} " if log_context else ""
        logger.info(
            f"{prefix}Start Recording: not_finalised_submission: {sub.id}, case: {case.id}",
            extra={"color": "green"},
        )
        self._recording.append(session)

    def finalise_submissions_on_recording_state_off(self):
        """Check for completed recordings and finalize their submissions.

        This method polls the shared ProcessorState records for the oldest recording session.
        Once every Recorder reports finished=True the submission is finalized.
        """
        if not self._recording:
            return

        recording_session = self._recording[0]

        # Surface any worker-thread errors to the runtime loop.
        for state in recording_session.iter_errors():
            self.logger.error(
                "Recording processor %s failed while handling submission %s: %s",
                state.processor,
                recording_session.submission.id,
                state.error,
            )
            # Propagate the first failure.
            raise state.error

        if not recording_session.all_finished():
            return

        submission = recording_session.submission
        self.logger.info(f"Finalized not_finalised_submission: {submission.id}")
        client = self._get_threadsafe_hl_client()
        finalise(client, submission)

        # Let each processor clear any per-submission state.
        for state in list(recording_session.processors):
            try:
                state.processor.clear_completed_recording(state)
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning(
                    "Failed to clear recording state for processor %s (%s): %s",
                    state.processor,
                    submission.id,
                    exc,
                )

        self._recording.popleft()

    def stop_recording(self):

        if not self._recording:
            return

        recording_session = self._recording[0]
        for state in list(recording_session.processors):
            dsp = state.processor
            self.logger.info(
                f"Stop Recording: not_finalised_submission: {recording_session.submission.id}, case: {recording_session.case_id}",
                extra={
                    "stream_id": getattr(dsp, "_stream_id", None),
                    "capability_name": getattr(dsp, "_capability_name", None),
                },
            )
            dsp.stop_recording(state)


from highlighter.core.gql_base_model import GQLBaseModel


class CreateCasePayload(GQLBaseModel):
    errors: List[str]
    case: Optional[CaseType] = None


class CreateSubmissionNotFinalisedPayload(GQLBaseModel):

    class SubmissionType(GQLBaseModel):
        id: str
        case_id: Optional[str] = None
        task_id: Optional[str] = None

    submission: Optional[SubmissionType] = None
    errors: List[str]


class CreateTaskPayload(GQLBaseModel):
    errors: List[str]
    task: Optional[TaskType] = None


def create_empty_case_with_not_finalized_submission(
    client: HLClient,
    workflow_order_id: UUID,
    case_name: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    *,
    log_context: Optional[str] = None,
) -> Tuple[CaseType, CreateSubmissionNotFinalisedPayload.SubmissionType]:
    """Creates an empty Case

    Args:
        client: HLClient instance
        workflow_order_id: Target workflow order ID
        case_name: Optional name for the case
        entity_id: Optional entity ID

    Returns:
        Case object

    Raises:
        RuntimeError: If case creation fails
    """
    # Create the case
    case_result = client.createCase(
        return_type=CreateCasePayload,
        workflowOrderId=workflow_order_id,
        name=case_name,
        entityId=entity_id,
        state="ready",
    )

    if case_result.errors:
        raise RuntimeError(f"Error in createCase: {case_result.errors}")

    if not case_result.case:
        raise RuntimeError("createCase succeeded but no CaseType returned")

    prefix = f"{log_context} " if log_context else ""
    logger.info(f"{prefix}Created case {case_result.case.id}", extra={"color": "green"})
    case = case_result.case

    sub_result = client.createSubmissionNotFinalised(
        return_type=CreateSubmissionNotFinalisedPayload,
        caseId=case.id,
    )

    if sub_result.errors:
        raise RuntimeError(f"Error in createSubmissionNotFinalised: {sub_result.errors}")

    if not sub_result.submission:
        raise RuntimeError(
            "createSubmissionNotFinalised succeeded but no CreateSubmissionNotFinalisedPayload.SubmissionType returned"
        )

    sub = sub_result.submission

    return case, sub
