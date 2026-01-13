"""AgentBay code execution tools for LlamaIndex."""

from typing import Optional

from llama_index.core.tools import FunctionTool

from .base import AgentBaySessionManager


def create_python_run_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create Python code execution tool using run_code.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "code_latest".

    Returns:
        FunctionTool for executing Python code directly.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def run_python_code(code: str, timeout_s: int = 60) -> str:
        """
        Execute Python code directly in the AgentBay session without creating a file.

        IMPORTANT FOR LLM AGENTS:
        - The code will be executed in a secure Python sandbox
        - Use print() to output results - stdout will be captured
        - Use 'FILE_GENERATED:path' to signal file creation for tracking
        - Available libraries: pandas, numpy, matplotlib, requests, and more
        - Code timeout: 60 seconds

        Args:
            code: Complete Python code to execute. Must be syntactically valid Python code.
            timeout_s: Timeout in seconds (default: 60).

        Returns:
            Execution result including stdout/stderr, or detailed error message.

        Example 1 - Generate CSV data:
            code = '''
import pandas as pd
data = {"name": ["Alice", "Bob"], "age": [25, 30]}
df = pd.DataFrame(data)
df.to_csv("/tmp/data.csv", index=False)
print("FILE_GENERATED:/tmp/data.csv")
print(f"Created CSV with {len(df)} rows")
'''

        Example 2 - Analyze and visualize:
            code = '''
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("/tmp/data.csv")
avg_age = df["age"].mean()
print(f"Average Age: {avg_age}")

plt.bar(df["name"], df["age"])
plt.savefig("/tmp/chart.png")
print("FILE_GENERATED:/tmp/chart.png")
'''
        """
        # Validate input
        if not code or not isinstance(code, str):
            return "Error: 'code' parameter must be a non-empty string containing valid Python code."

        if len(code.strip()) < 5:
            return "Error: Code is too short. Please provide complete Python code."

        try:
            session = session_manager.get_or_create_session(image_id)
            result = session.code.run_code(code, "python", timeout_s)

            if not result.success:
                error_msg = result.error_message or "Unknown error"
                return (
                    f"Code execution failed:\n{error_msg}\n\n"
                    f"Please check:\n"
                    f"1. Python syntax is correct\n"
                    f"2. Required libraries are available\n"
                    f"3. File paths are absolute (e.g., '/tmp/file.csv')"
                )

            output = result.result.strip()
            if not output:
                return (
                    "Code executed successfully but produced no output.\n"
                    "Consider adding print() statements to see results."
                )

            return f"Code executed successfully:\n{output}"

        except Exception as e:
            return (
                f"Error executing code: {str(e)}\n\n"
                f"This may be due to:\n"
                f"1. Network/connection issues\n"
                f"2. Invalid code syntax\n"
                f"3. Timeout (current: {timeout_s}s)\n"
                f"Please verify the code and try again."
            )

    return FunctionTool.from_defaults(
        fn=run_python_code,
        name="python_run_code",
        description=(
            "Execute Python code in a secure sandbox environment. "
            "Use this when you need to:\n"
            "- Generate or manipulate data\n"
            "- Perform calculations or analysis\n"
            "- Create visualizations or files\n"
            "- Process data with Python libraries\n\n"
            "Available libraries: pandas, numpy, matplotlib, requests, and more.\n"
            "Timeout: 60 seconds.\n"
            "Use print() to output results.\n"
            "Use 'FILE_GENERATED:path' to signal file creation.\n"
            "All file paths must be absolute (e.g., '/tmp/file.csv')."
        ),
    )


def create_javascript_run_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> FunctionTool:
    """
    Create JavaScript code execution tool using run_code.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "code_latest".

    Returns:
        FunctionTool for executing JavaScript code directly.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def run_javascript_code(code: str, timeout_s: int = 60) -> str:
        """
        Execute JavaScript code directly in the AgentBay session without creating a file.

        Args:
            code: The JavaScript code to execute.
            timeout_s: Timeout in seconds (default: 60).

        Returns:
            Execution result (stdout/stderr) or error message.
        """
        try:
            session = session_manager.get_or_create_session(image_id)
            result = session.code.run_code(code, "javascript", timeout_s)

            if not result.success:
                return f"Code execution failed: {result.error_message}"

            return f"Code executed successfully:\n{result.result}"

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=run_javascript_code,
        name="javascript_run_code",
        description=(
            "Execute JavaScript code directly in the AgentBay session without creating a file. "
            "This is more efficient than writing a file and then executing it. "
            "The code will be executed in a sandboxed environment with Node.js available. "
            "Input should be the JavaScript code as a string."
        ),
    )


def create_code_tools(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> list:
    """
    Create all code execution tools.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "code_latest".

    Returns:
        List of code execution tools.

    Example:
        >>> from llama_index.tools.agentbay import create_code_tools
        >>> tools = create_code_tools()
    """
    return [
        create_python_run_tool(session_manager, image_id),
        create_javascript_run_tool(session_manager, image_id),
    ]

