"""LLM Tool Calling Support

This module provides the infrastructure for LLM capabilities to call tools
like creating case messages, querying data, etc.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID

from highlighter.client.gql_client import HLClient
from highlighter.client.tasks import TaskContext

__all__ = [
    "ToolExecutionContext",
    "LLMTools",
    "TOOL_USAGE_GUIDELINES",
]


@dataclass
class ToolExecutionContext:
    """Context provided to LLM tool functions.

    This contains all the information tools need to execute actions
    like creating case messages, querying data, etc.
    """

    stream: Any  # Current stream object
    logger: logging.Logger  # LLM capability logger
    client: HLClient  # Highlighter API client
    task_context: Optional[TaskContext]  # Current recording session (if active)
    case_id: Optional[str]  # Current case ID (if recording)

    # From stream variables
    stream_id: str
    capability_name: str  # Name of the capability (for logging)
    data_source_uuid: Optional[UUID] = None
    account_uuid: Optional[UUID] = None


class LLMTools:
    """Container for LLM-callable tool functions.

    Each tool is a static method that receives a ToolExecutionContext
    and returns a structured result dictionary.
    """

    @staticmethod
    def create_message_on_case(
        ctx: ToolExecutionContext,
        message: str,
        message_type: str = "info",
        severity: str = "info",
    ) -> Dict[str, Any]:
        """Add a message to the current recording case.

        This tool allows the LLM to annotate the case with observations,
        alerts, or analysis results.

        Args:
            ctx: Tool execution context
            message: Message content to add to the case
            message_type: Type of message (info, alert, observation, analysis, summary)
            severity: Severity level (info, warning, critical)

        Returns:
            Dict with success status and message_id or error:
            {
                "success": bool,
                "message_id": str (if success),
                "error": str (if failure)
            }
        """
        # Check if case is recording
        if not ctx.case_id:
            ctx.logger.warning(
                "create_message_on_case called but no case is recording",
                extra={"stream_id": ctx.stream_id, "capability_name": ctx.capability_name},
            )
            return {
                "success": False,
                "error": "No case is currently recording",
            }

        try:
            from highlighter.client.base_models.base_models import (
                CreateCaseMessagePayload,
            )

            ctx.logger.info(
                f"LLM tool creating case message: case={ctx.case_id}, "
                f"type={message_type}, severity={severity}, message='{message}'",
                extra={"stream_id": ctx.stream_id, "capability_name": ctx.capability_name},
            )

            # Call Highlighter API to create case message
            result = ctx.client.create_case_message(
                return_type=CreateCaseMessagePayload,
                caseId=ctx.case_id,
                content=message,
            )

            if result.errors:
                ctx.logger.error(
                    f"Failed to create case message: {result.errors}",
                    extra={"stream_id": ctx.stream_id, "capability_name": ctx.capability_name},
                )
                return {"success": False, "error": str(result.errors)}

            # Extract message ID from result
            message_id = None
            if result.user_message:
                message_id = result.user_message.id
            elif result.ai_message:
                message_id = result.ai_message.id

            ctx.logger.info(
                f"Successfully created case message: message_id={message_id}",
                extra={"stream_id": ctx.stream_id, "capability_name": ctx.capability_name},
            )

            return {
                "success": True,
                "message_id": message_id,
                "message": message,
            }

        except Exception as e:
            ctx.logger.error(
                f"Tool execution failed: create_message_on_case - {e}",
                extra={"stream_id": ctx.stream_id, "capability_name": ctx.capability_name},
            )
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_tool_schemas() -> List[Dict]:
        """Return OpenAI/Anthropic function calling schemas for all tools.

        Returns:
            List of tool schemas in the format expected by LLM APIs
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_message_on_case",
                    "description": (
                        "Add a message to the currently recording case. Use this when you detect "
                        "significant events, safety violations, unusual behavior, or anything that "
                        "requires human attention. Only create messages for noteworthy events, not "
                        "routine observations."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The message content to add to the case. Be specific and concise.",
                            },
                            "message_type": {
                                "type": "string",
                                "enum": ["info", "alert", "observation", "analysis", "summary"],
                                "description": (
                                    "Type of message: "
                                    "'info' for general information, "
                                    "'alert' for events requiring attention, "
                                    "'observation' for noteworthy observations, "
                                    "'analysis' for analytical findings, "
                                    "'summary' for summary of events"
                                ),
                                "default": "info",
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["info", "warning", "critical"],
                                "description": (
                                    "Severity level: "
                                    "'info' for normal events, "
                                    "'warning' for events that may need attention, "
                                    "'critical' for urgent events requiring immediate attention"
                                ),
                                "default": "info",
                            },
                        },
                        "required": ["message"],
                    },
                },
            }
        ]

    @staticmethod
    def get_tool_function(tool_name: str):
        """Get tool function by name.

        Args:
            tool_name: Name of the tool

        Returns:
            Tool function or None if not found
        """
        return getattr(LLMTools, tool_name, None)


# Prompt template fragment for tool usage guidance
TOOL_USAGE_GUIDELINES = """
## Available Actions

You can take the following actions based on your analysis:

- **create_message_on_case**: Add a message to the current case when you detect:
  * Safety violations or hazards
  * Unusual or anomalous behavior
  * Significant events requiring human attention
  * Equipment malfunctions or failures
  * Important observations or findings

Guidelines:
- Only create messages for noteworthy events, not routine observations
- Be specific and concise in your messages
- Use appropriate severity levels (info/warning/critical)
- Use appropriate message types (info/alert/observation/analysis/summary)
- Avoid creating duplicate messages for the same event

If no significant events are detected, provide a brief summary without creating case messages.
"""
