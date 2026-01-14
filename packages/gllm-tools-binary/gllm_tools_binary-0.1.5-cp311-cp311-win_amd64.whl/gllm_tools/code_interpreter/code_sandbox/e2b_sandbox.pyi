from _typeshed import Incomplete
from e2b.sandbox_sync.commands.command import Commands
from e2b.sandbox_sync.filesystem.filesystem import Filesystem
from e2b_code_interpreter import Sandbox
from gllm_inference.schema import Attachment as Attachment
from gllm_tools.code_interpreter.code_sandbox.models import ExecutionResult as ExecutionResult, ExecutionStatus as ExecutionStatus
from gllm_tools.code_interpreter.code_sandbox.sandbox import BaseSandbox as BaseSandbox
from gllm_tools.code_interpreter.code_sandbox.utils import calculate_duration_ms as calculate_duration_ms
from typing import Any, Self

logger: Incomplete

class E2BSandbox(BaseSandbox):
    """Implementation of Sandbox interface for E2B.

    Attributes:
        sandbox (Sandbox | None): E2B sandbox instance.
        files (Filesystem | None): File interface for the sandbox.
        commands (Commands | None): Command interface for the sandbox.
        additional_packages (list[str]): Additional packages to install during initialization.
    """
    additional_packages: list[str]
    sandbox: Sandbox | None
    files: Filesystem | None
    commands: Commands | None
    def __init__(self, language: str = 'python') -> None:
        '''Initialize E2B Sandbox instance.

        Don\'t use this method directly. Use `E2BSandbox.create()` instead.

        Args:
            language (str, optional): Programming language for dependency installation. Defaults to "python".
        '''
    @classmethod
    async def create(cls, api_key: str, domain: str | None = None, template: str | None = None, language: str = 'python', additional_packages: list[str] | None = None, **kwargs: Any) -> Self:
        '''Create a new E2B sandbox without blocking the event loop.

        Use this method in async contexts instead of calling __init__ directly.

        Args:
            api_key (str): E2B API key.
            domain (str | None, optional): E2B domain. Defaults to None (will connect to E2B SaaS).
            template (str | None, optional): E2B template. Defaults to None.
            language (str, optional): Programming language for dependency installation. Defaults to "python".
            additional_packages (list[str] | None, optional): Additional packages to install during initialization.
                Defaults to None.
            **kwargs (Any): Additional initialization parameters for E2B Sandbox.

        Returns:
            E2BSandbox: Initialized E2B Sandbox instance.
        '''
    async def execute_code(self, code: str, timeout: int = 30, files: list[Attachment] | None = None, **kwargs: Any) -> ExecutionResult:
        """Execute code in the E2B sandbox.

        Args:
            code (str): The code to execute.
            timeout (int, optional): Maximum execution time in seconds. Defaults to 30.
            files (list[Attachment] | None, optional): List of Attachment objects with file details. Defaults to None.
            **kwargs (Any): Additional execution parameters.

        Returns:
            ExecutionResult: Structured result of the execution.

        Raises:
            RuntimeError: If sandbox is not initialized.
        """
    def terminate(self) -> None:
        """Terminate the sandbox environment and clean up resources."""
    def download_file(self, file_path: str) -> bytes | None:
        """Download file content from the sandbox.

        Args:
            file_path (str): Path to the file in the sandbox.

        Returns:
            bytes | None: File content as bytes, or None if download fails.

        Raises:
            RuntimeError: If Filesystem is not found.
        """
