from _typeshed import Incomplete
from gllm_inference.schema import Attachment as Attachment
from gllm_tools.code_interpreter.code_sandbox.models import ExecutionResult as ExecutionResult, ExecutionStatus as ExecutionStatus
from gllm_tools.code_interpreter.code_sandbox.sandbox import BaseSandbox as BaseSandbox
from gllm_tools.code_interpreter.code_sandbox.utils import calculate_duration_ms as calculate_duration_ms
from pydantic import BaseModel
from typing import Any

logger: Incomplete

class CodeExecutionRequest(BaseModel):
    """Pydantic model for validating code execution requests."""
    code: str
    language: str
    timeout: int
    max_output_length: int

class MCPRequest(BaseModel):
    """Model for MCP server requests."""
    jsonrpc: str
    id: int
    method: str
    params: dict[str, Any]

class MCPResponse(BaseModel):
    """Model for MCP server responses."""
    jsonrpc: str
    id: int
    result: dict[str, Any] | None
    error: dict[str, Any] | None

class PydanticExecutorSandbox(BaseSandbox):
    """Pydantic MCP Code Executor.

    This executor communicates with the Pydantic MCP server to execute Python code
    in a secure sandboxed WebAssembly environment using Pyodide.


    Attributes:
        initialized (bool): Whether the MCP server is initialized.
        mcp_process (subprocess.Popen | None): MCP server process.
        request_id (int): Current request ID counter.
        mcp_server_path (str): Path to MCP server executable.
        mcp_args (list[str]): Arguments for MCP server.
    """
    initialized: bool
    mcp_process: Incomplete
    request_id: int
    mcp_server_path: Incomplete
    mcp_args: Incomplete
    def __init__(self, mcp_server_path: str | None = None, language: str = 'python', **kwargs: Any) -> None:
        '''Initialize Pydantic MCP Code Executor instance.

        Args:
            mcp_server_path (str, optional): Optional path to MCP server executable. Defaults to None.
            language (str, optional): Programming language (only "python" supported). Defaults to "python".
            **kwargs (Any): Additional initialization parameters (ignored for MCP).

        Raises:
            ValueError: If language is not "python".
            RuntimeError: If MCP server initialization fails.
        '''
    async def execute_code(self, code: str, timeout: int = 30, files: list[Attachment] | None = None, **kwargs: Any) -> ExecutionResult:
        """Execute code using the Pydantic MCP server.

        Args:
            code (str): The Python code to execute.
            timeout (int, optional): Maximum execution time in seconds. Defaults to 30.
            files (list[Attachment] | None, optional): List of Attachment objects with file details. Defaults to None.
            **kwargs (Any): Additional execution parameters.

        Returns:
            ExecutionResult: Structured result of the execution.

        Raises:
            RuntimeError: If executor is not initialized.
        """
    def terminate(self) -> None:
        """Terminate the sandbox environment and clean up resources."""
    def download_file(self, file_path: str) -> bytes | None:
        """Download file content from the sandbox.

        Args:
            file_path (str): Path to the file in the sandbox.

        Returns:
            bytes | None: File content as bytes, or None if download fails.
        """
