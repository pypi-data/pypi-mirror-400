"""Command execution tools for AgentBay."""

from typing import Optional

from llama_index.core.tools import FunctionTool

from .base import AgentBaySessionManager


def create_command_execute_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create command execution tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session.

    Returns:
        FunctionTool for executing commands.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def execute_command(command: str) -> str:
        """
        Execute a shell command in the AgentBay session.

        Args:
            command: Command to execute.

        Returns:
            Command output.
        """
        try:
            session = session_manager.get_or_create_session(image_id)
            result = session.command.execute_command(command, timeout_ms=30000)

            if not result.success:
                return f"Command failed: {result.error_message}"

            return f"Command executed successfully:\n{result.output}"

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=execute_command,
        name="command_execute",
        description=(
            "Execute a shell command in the AgentBay session. "
            "Input should be the command to execute. "
            "Example: 'ls -la' or 'python script.py' or 'npm install'"
        ),
    )


def create_python_execute_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create Python code execution tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session.

    Returns:
        FunctionTool for executing Python code.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def execute_python(code: str) -> str:
        """
        Execute Python code in the AgentBay session.

        Args:
            code: Python code to execute.

        Returns:
            Execution result.
        """
        try:
            session = session_manager.get_or_create_session(image_id)

            temp_file = "/tmp/temp_script.py"
            # Updated to use keyword arguments for better compatibility
            write_result = session.file_system.write_file(
                path=temp_file, 
                content=code, 
                mode="overwrite"
            )

            if not write_result.success:
                return f"Failed to write code: {write_result.error_message}"

            exec_result = session.command.execute_command(command=f"python {temp_file}", timeout_ms=30000)

            if not exec_result.success:
                return f"Execution failed: {exec_result.error_message}"

            return f"Python code executed successfully:\n{exec_result.output}"

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=execute_python,
        name="python_execute",
        description=(
            "Execute Python code in the AgentBay session. "
            "Input should be valid Python code. "
            'Example: \'print("Hello")\' or \'import json; print(json.dumps({"a": 1}))\''
        ),
    )