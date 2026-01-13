"""File system tools for AgentBay."""

import os
from typing import Optional

from llama_index.core.tools import FunctionTool

from .base import AgentBaySessionManager


def create_file_read_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create file read tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session.

    Returns:
        FunctionTool for reading files.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def read_file(file_path: str) -> str:
        """
        Read the contents of a file in the AgentBay session.

        Args:
            file_path: Path to the file.

        Returns:
            File contents or error message.
        """
        try:
            session = session_manager.get_or_create_session(image_id)
            result = session.file_system.read_file(path=file_path)

            if not result.success:
                return f"Failed to read file: {result.error_message}"

            return result.content

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=read_file,
        name="file_read",
        description=(
            "Read the contents of a file in the AgentBay session. "
            "Input should be the file path. "
            "Example: '/tmp/data.txt' or '/home/user/document.json'"
        ),
    )


def create_file_write_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create file write tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session.

    Returns:
        FunctionTool for writing files.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def write_file(file_path: str, content: str) -> str:
        """
        Write content to a file in the AgentBay session.

        Args:
            file_path: Path to the file.
            content: Content to write.

        Returns:
            Operation result.
        """
        try:
            session = session_manager.get_or_create_session(image_id)

            # Updated to use keyword arguments for better compatibility
            result = session.file_system.write_file(
                path=file_path, 
                content=content, 
                mode="overwrite"
            )

            if not result.success:
                return f"Failed to write file: {result.error_message}"

            return f"Successfully wrote to {file_path}"

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=write_file,
        name="file_write",
        description=(
            "Write content to a file in the AgentBay session. "
            "Provide the file path and content to write."
        ),
    )


def create_file_list_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create file list tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session.

    Returns:
        FunctionTool for listing files.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def list_directory(directory: str) -> str:
        """
        List files in a directory in the AgentBay session.

        Args:
            directory: Directory path.

        Returns:
            File list or error message.
        """
        try:
            session = session_manager.get_or_create_session(image_id)
            result = session.file_system.list_directory(path=directory)

            if not result.success:
                return f"Failed to list directory: {result.error_message}"

            files = [entry.name for entry in result.entries]
            return f"Files in {directory}:\n" + "\n".join(files)

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=list_directory,
        name="file_list",
        description=(
            "List files in a directory in the AgentBay session. "
            "Input should be the directory path. "
            "Example: '/tmp' or '/home/user/documents'"
        ),
    )


def create_file_download_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create file download tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session.

    Returns:
        FunctionTool for downloading files from AgentBay session to local.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def download_file(remote_path: str, local_path: str) -> str:
        """
        Download a file from the AgentBay session to local filesystem.

        Args:
            remote_path: Path to the file in the AgentBay session.
            local_path: Local path where the file should be saved.

        Returns:
            Success message with local path or error message.
        """
        try:
            session = session_manager.get_or_create_session(image_id)
            result = session.file_system.download_file(
                remote_path=remote_path,
                local_path=local_path,
                overwrite=True,
                wait=True,
                wait_timeout=60.0,
            )

            # Verify download by checking if file exists and has content
            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                file_size = os.path.getsize(local_path)
                return f"Successfully downloaded {remote_path} to {local_path} ({file_size} bytes)"

            # If file doesn't exist or is empty, report actual error
            if not result.success:
                error_msg = getattr(result, 'error_message', None)
                if not error_msg:
                    # Try to get more details from the result object
                    error_details = []
                    for attr in ['error', 'message', 'status']:
                        val = getattr(result, attr, None)
                        if val:
                            error_details.append(f"{attr}={val}")
                    error_msg = ', '.join(error_details) if error_details else 'Unknown error'
                return f"Failed to download file: {error_msg}"

            # Edge case: result.success is True but file wasn't created
            return f"Download reported success but file not found at {local_path}"

        except Exception as e:
            import traceback
            return f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"

    return FunctionTool.from_defaults(
        fn=download_file,
        name="file_download",
        description=(
            "Download a file from the AgentBay session to local filesystem. "
            "Provide both the remote path (in session) and local path (where to save). "
            "This is useful for retrieving generated files like charts, reports, or data files. "
            "Example: remote_path='/tmp/chart.png', local_path='/Users/user/Downloads/chart.png'"
        ),
    )