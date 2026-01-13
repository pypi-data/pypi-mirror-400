"""Browser automation tools for AgentBay.

Note: Browser tools use AgentBay's browser_latest image and Playwright CDP protocol.
For complex browser automation, consider using Playwright directly with AgentBay browser endpoint.
"""

from typing import Optional

from agentbay import BrowserOption
from llama_index.core.tools import FunctionTool

from .base import AgentBaySessionManager


def create_browser_screenshot_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "browser_latest",
) -> FunctionTool:
    """
    Create browser screenshot tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "browser_latest".

    Returns:
        FunctionTool for taking screenshots.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def take_screenshot() -> str:
        """
        Take a screenshot of the current browser page.

        Returns:
            Screenshot data URL or error message.
        """
        try:
            session = session_manager.get_or_create_session(image_id)

            # Initialize browser if needed
            if not hasattr(session, "_browser_initialized"):
                browser_option = BrowserOption()
                success = session.browser.initialize(browser_option)
                if not success:
                    return "Failed to initialize browser"
                session._browser_initialized = True

            # Take screenshot using browser agent
            result = session.browser.agent.screenshot(full_page=True)

            if result.startswith("data:image"):
                return f"Screenshot captured successfully: {result[:100]}..."
            else:
                return f"Screenshot failed: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=take_screenshot,
        name="browser_screenshot",
        description=(
            "Take a screenshot of the current browser page. "
            "Returns a base64 encoded data URL of the screenshot. "
            "Note: Browser must be initialized first."
        ),
    )


def create_browser_info_tool(
    session_manager: Optional[AgentBaySessionManager] = None,
    image_id: str = "browser_latest",
) -> FunctionTool:
    """
    Create browser info tool.

    Args:
        session_manager: Optional session manager for sharing sessions.
        image_id: Image ID for the session. Defaults to "browser_latest".

    Returns:
        FunctionTool for getting browser information.
    """
    if session_manager is None:
        session_manager = AgentBaySessionManager()

    def get_browser_info() -> str:
        """
        Get browser endpoint information.

        Returns:
            Browser endpoint URL and status.
        """
        try:
            session = session_manager.get_or_create_session(image_id)

            # Initialize browser if needed
            if not hasattr(session, "_browser_initialized"):
                browser_option = BrowserOption()
                success = session.browser.initialize(browser_option)
                if not success:
                    return "Failed to initialize browser"
                session._browser_initialized = True

            # Get browser endpoint
            endpoint_url = session.browser.get_endpoint_url()

            return (
                f"Browser initialized successfully.\n"
                f"CDP Endpoint: {endpoint_url}\n"
                f"You can connect to this browser using Playwright:\n"
                f"  browser = await playwright.chromium.connect_over_cdp('{endpoint_url}')"
            )

        except Exception as e:
            return f"Error: {str(e)}"

    return FunctionTool.from_defaults(
        fn=get_browser_info,
        name="browser_info",
        description=(
            "Get browser endpoint information for Playwright connection. "
            "Returns the CDP endpoint URL that can be used to connect "
            "with Playwright for advanced browser automation."
        ),
    )
