# LlamaIndex Tools Integration: AgentBay

AgentBay tools integration for LlamaIndex, enabling browser automation, file operations, and command execution.

## Installation

```bash
pip install llama-index-tools-agentbay llama-index-llms-openai-like
```

## Setup

Set your API keys as environment variables:

```bash
export AGENTBAY_API_KEY="your-agentbay-api-key"
export DASHSCOPE_API_KEY="your-dashscope-api-key"  # Optional: For DashScope LLM
```

## Quick Start

Use the context manager for automatic resource cleanup:

```python
import os
import asyncio
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.agent import ReActAgent
from llama_index.tools.agentbay import create_code_tools, AgentBaySessionManager
from contextlib import contextmanager

@contextmanager
def agentbay_tools():
    manager = AgentBaySessionManager(api_key=os.getenv("AGENTBAY_API_KEY"))
    try:
        yield create_code_tools(manager)
    finally:
        manager.cleanup()

async def main():
    llm = OpenAILike(
        model="qwen-plus",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        is_chat_model=True
    )

    with agentbay_tools() as tools:
        # Note: ReActAgent in llama-index-core >= 0.14.0 is workflow-based
        agent = ReActAgent.from_tools(tools, llm=llm, verbose=True)
        response = await agent.achat("Calculate the 10th Fibonacci number using Python")
        print(response.response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Tools

*   **Code Execution**: `create_code_tools` (Recommended) - Run Python/JS code directly.
*   **Browser Automation**: `create_browser_tools` - Take screenshots, inspect pages.
*   **File Operations**: `create_filesystem_tools` - Read/Write files.
*   **Command Execution**: `create_command_tools` - Run shell commands.

## RAG Integration

Extract insights from execution results:

```python
from llama_index.tools.agentbay import create_rag_manager

rag = create_rag_manager()
rag.add_execution_result("result content", "task description")
print(rag.query("What was the result?"))
```

## Support

*   [AgentBay Console](https://agentbay.console.aliyun.com/)
*   [AgentBay SDK Documentation](https://github.com/aliyun/wuying-agentbay-sdk)
*   [LlamaIndex Documentation](https://docs.llamaindex.ai/)

## License

MIT
