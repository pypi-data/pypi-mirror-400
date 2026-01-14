"""
Utilities for filtering Langfuse traces based on tool call success.

Uses the OTEL parser to get structured messages, then filters traces with failed tool calls.
"""

import os
from typing import List

from agentops.data_annotator import ERROR_KEYWORDS


class LangfuseToolSuccessFilter:
    """
    Filter Langfuse sessions to keep only those without failed tool calls.

    Uses the OTEL parser to handle framework-specific trace parsing
    (LangGraph, Pydantic AI, LangFlow, etc.)

    Assumption: 1 session_id = 1 trajectory

    Example:
        >>> filter = LangfuseToolSuccessFilter()
        >>> session_ids = ["session-1", "session-2", "session-3"]
        >>> successful = filter.filter_sessions(session_ids)
        >>> print(f"Kept {len(successful)}/{len(session_ids)} sessions")
    """

    def __init__(
        self,
        public_key: str = None,
        secret_key: str = None,
        host: str = None,
    ):
        """
        Initialize the filter.

        Args:
            public_key: Langfuse public key (defaults to LANGFUSE_PUBLIC_KEY env var)
            secret_key: Langfuse secret key (defaults to LANGFUSE_SECRET_KEY env var)
            host: Langfuse host URL (defaults to LANGFUSE_HOST env var or cloud.langfuse.com)
        """
        # Set environment variables for OTEL parser to use
        if public_key:
            os.environ["LANGFUSE_PUBLIC_KEY"] = public_key
        if secret_key:
            os.environ["LANGFUSE_SECRET_KEY"] = secret_key
        if host:
            os.environ["LANGFUSE_HOST"] = host

    ## TODO: FIlter only based on tool plan.
    def filter_sessions(self, session_ids: List[str]) -> List[str]:
        """
        Filter sessions, keeping only those without failed tool calls.

        Assumption: 1 session_id = 1 trajectory (may have multiple traces,
        but OTEL parser stitches them together).

        Args:
            session_ids: List of Langfuse session IDs to filter

        Returns:
            List of successful session IDs (no failed tool calls)
        """
        from agentops.otel_parser import otel_parser as parser

        successful_session_ids = []

        for session_id in session_ids:
            # Parse all traces in this session (stitched together by OTEL parser)
            messages = parser.poll_messages(session_id)

            # Check if this session has failed tool calls
            if not self._has_failed_tool_calls(messages):
                # This session is successful, keep it
                successful_session_ids.append(session_id)

        return successful_session_ids

    def _has_failed_tool_calls(self, messages: List) -> bool:
        """
        Check if any message in the list has failed tool calls.

        Args:
            messages: List of OTelParserMessage objects

        Returns:
            True if any tool call failed, False otherwise
        """
        for msg in messages:
            # Check message content for error indicators
            if self._message_has_error(msg):
                return True

        return False

    def _message_has_error(self, msg) -> bool:
        """
        Check if a single message indicates an error.

        Args:
            msg: OTelParserMessage object

        Returns:
            True if message indicates error, False otherwise
        """
        # Check content for error keywords
        if msg.content and msg.role == "tool":
            content_str = str(msg.content).lower()
            if any(keyword in content_str for keyword in ERROR_KEYWORDS):
                return True

        # Check if it's a tool message with error type
        if msg.type and "error" in str(msg.type).lower():
            return True

        return False
