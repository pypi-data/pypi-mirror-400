"""AgentBay tools integration for LlamaIndex."""

from typing import Optional

from .base import AgentBaySessionManager
from .browser_tools import (
    create_browser_screenshot_tool,
    create_browser_info_tool,
)
from .code_tools import (
    create_python_run_tool,
    create_javascript_run_tool,
    create_code_tools,
)
from .command_tools import create_command_execute_tool, create_python_execute_tool
from .filesystem_tools import (
    create_file_list_tool,
    create_file_read_tool,
    create_file_write_tool,
    create_file_download_tool,
)
from .rag_helper import (
    AgentBayRAGManager,
    InsightExtractor,
    create_rag_manager,
)

__all__ = [
    "AgentBaySessionManager",
    "AgentBayRAGManager",
    "InsightExtractor",
    "create_browser_screenshot_tool",
    "create_browser_info_tool",
    "create_file_read_tool",
    "create_file_write_tool",
    "create_file_list_tool",
    "create_file_download_tool",
    "create_command_execute_tool",
    "create_python_execute_tool",
    "create_python_run_tool",
    "create_javascript_run_tool",
    "create_rag_manager",
    "create_browser_tools",
    "create_filesystem_tools",
    "create_command_tools",
    "create_code_tools",
    "create_all_tools",
]


def create_browser_tools(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "browser_latest",
) -> list:
    """
    Create all browser tools.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "browser_latest".

    Returns:
        List of browser tools.

    Example:
        >>> from llama_index.tools.agentbay import create_browser_tools
        >>> tools = create_browser_tools()

    Note:
        Browser tools provide basic screenshot and info capabilities.
        For advanced browser automation (navigation, clicking, etc.),
        use Playwright directly with the browser endpoint from browser_info tool.
    """
    return [
        create_browser_screenshot_tool(session_manager, image_id),
        create_browser_info_tool(session_manager, image_id),
    ]


def create_filesystem_tools(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> list:
    """
    Create all filesystem tools.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "code_latest".

    Returns:
        List of filesystem tools.

    Example:
        >>> from llama_index.tools.agentbay import create_filesystem_tools
        >>> tools = create_filesystem_tools()
    """
    return [
        create_file_read_tool(session_manager, image_id),
        create_file_write_tool(session_manager, image_id),
        create_file_list_tool(session_manager, image_id),
        create_file_download_tool(session_manager, image_id),
    ]


def create_command_tools(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "code_latest",
) -> list:
    """
    Create all command execution tools.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "code_latest".

    Returns:
        List of command execution tools.

    Example:
        >>> from llama_index.tools.agentbay import create_command_tools
        >>> tools = create_command_tools()
    """
    return [
        create_command_execute_tool(session_manager, image_id),
        create_python_execute_tool(session_manager, image_id),
    ]


def create_all_tools(
    api_key: Optional[str] = None,
    browser_enabled: bool = True,
    filesystem_enabled: bool = True,
    command_enabled: bool = True,
    code_enabled: bool = True,
) -> list:
    """
    Create all AgentBay tools.

    Args:
        api_key: AgentBay API key. If not provided, reads from AGENTBAY_API_KEY env var.
        browser_enabled: Whether to enable browser tools. Defaults to True.
        filesystem_enabled: Whether to enable filesystem tools. Defaults to True.
        command_enabled: Whether to enable command execution tools. Defaults to True.
        code_enabled: Whether to enable code execution tools (run_code). Defaults to True.

    Returns:
        List of all enabled tools.

    Example:
        >>> from llama_index.tools.agentbay import create_all_tools
        >>> tools = create_all_tools()
    """
    session_manager = AgentBaySessionManager(api_key=api_key)

    tools = []

    if browser_enabled:
        tools.extend(create_browser_tools(session_manager))

    if filesystem_enabled:
        tools.extend(create_filesystem_tools(session_manager))

    if command_enabled:
        tools.extend(create_command_tools(session_manager))

    if code_enabled:
        tools.extend(create_code_tools(session_manager))

    return tools
