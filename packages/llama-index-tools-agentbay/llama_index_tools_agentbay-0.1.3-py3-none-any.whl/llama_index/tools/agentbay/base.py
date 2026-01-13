"""Base classes for AgentBay tools integration."""

import os
from threading import Lock
from typing import Dict, Optional

from agentbay import AgentBay, CreateSessionParams, Session
from llama_index.core.tools import BaseTool


class AgentBaySessionManager:
    """
    AgentBay session manager.

    Manages creation, reuse, and cleanup of AgentBay sessions.
    Supports multiple session types based on image_id.

    Args:
        api_key: AgentBay API key. If not provided, reads from AGENTBAY_API_KEY env var.
        default_image_id: Default image ID for sessions. Defaults to "browser_latest".

    Example:
        >>> manager = AgentBaySessionManager()
        >>> session = manager.get_or_create_session("browser_latest")
        >>> # Use session...
        >>> manager.cleanup()
    """

    def __init__(
        self, api_key: Optional[str] = None, default_image_id: str = "browser_latest"
    ):
        """Initialize session manager."""
        self.api_key = api_key or os.getenv("AGENTBAY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "AGENTBAY_API_KEY is required. "
                "Set it via environment variable or pass as argument."
            )

        # Updated to support security_token if provided in env
        self.security_token = os.getenv("AGENTBAY_SECURITY_TOKEN")
        if self.security_token:
            self.client = AgentBay(api_key=self.api_key, security_token=self.security_token)
        else:
            self.client = AgentBay(api_key=self.api_key)

        self.default_image_id = default_image_id
        self._session_ids: Dict[str, str] = {}  # image_id -> session_id mapping
        self._lock = Lock()

    def get_or_create_session(
        self,
        image_id: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
    ) -> Session:
        """
        Get or create a session for the specified image type.

        Args:
            image_id: Image ID for the session. Uses default if not provided.
            labels: Optional labels for the session.

        Returns:
            Session object.

        Example:
            >>> session = manager.get_or_create_session("browser_latest")
        """
        image_id = image_id or self.default_image_id

        with self._lock:
            # If we have a session_id for this image_id, get the session
            if image_id in self._session_ids:
                session_id = self._session_ids[image_id]
                result = self.client.get(session_id)
                if result.success:
                    return result.session
                else:
                    # Session no longer exists, remove from cache
                    del self._session_ids[image_id]

            # Create new session
            params = CreateSessionParams(
                image_id=image_id, labels=labels or {"source": "llama-index"}
            )
            result = self.client.create(params)

            if not result.success or result.session is None:
                raise RuntimeError(
                    f"Failed to create session: {getattr(result, 'error_message', 'Unknown error')}"
                )

            # Store session_id for future retrieval
            self._session_ids[image_id] = result.session.session_id

            return result.session

    def cleanup(self, image_id: Optional[str] = None) -> None:
        """
        Clean up sessions.

        Args:
            image_id: If provided, only cleanup this session type.
                     Otherwise, cleanup all sessions.

        Example:
            >>> manager.cleanup("browser_latest")  # Cleanup specific session
            >>> manager.cleanup()  # Cleanup all sessions
        """
        with self._lock:
            if image_id:
                if image_id in self._session_ids:
                    session_id = self._session_ids[image_id]
                    try:
                        # Get session and delete it
                        result = self.client.get(session_id)
                        if result.success:
                            self.client.delete(result.session)
                    except Exception:
                        pass
                    del self._session_ids[image_id]
            else:
                for session_id in list(self._session_ids.values()):
                    try:
                        result = self.client.get(session_id)
                        if result.success:
                            self.client.delete(result.session)
                    except Exception:
                        pass
                self._session_ids.clear()

    def __del__(self):
        """Cleanup all sessions on deletion."""
        try:
            self.cleanup()
        except Exception:
            pass


