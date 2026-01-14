from _typeshed import Incomplete
from abc import ABC, abstractmethod
from gllm_inference.schema import Attachment as Attachment
from gllm_tools.code_interpreter.code_sandbox.models import ExecutionResult as ExecutionResult
from typing import Any

class BaseSandbox(ABC):
    """Base class for sandbox environments.

    Attributes:
        language (str): Programming language for the sandbox.
    """
    language: Incomplete
    def __init__(self, language: str = 'python', **kwargs: Any) -> None:
        '''Initialize the sandbox with language and additional parameters.

        Args:
            language (str): Programming language for the sandbox. Defaults to "python".
            **kwargs (Any): Additional initialization parameters.
        '''
    @abstractmethod
    async def execute_code(self, code: str, timeout: int = 30, files: list[Attachment] | None = None, **kwargs: Any) -> ExecutionResult:
        """Execute code in the sandbox environment.

        Args:
            code (str): The code to execute.
            timeout (int): Maximum execution time in seconds. Defaults to 30.
            files (list[Attachment] | None, optional): List of Attachment objects with file details. Defaults to None.
            **kwargs (Any): Additional execution parameters.

        Returns:
            ExecutionResult: Structured result of the execution.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
    @abstractmethod
    def terminate(self) -> None:
        """Terminate the sandbox environment and clean up resources.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
    @abstractmethod
    def download_file(self, file_path: str) -> bytes | None:
        """Download file content from the sandbox.

        Args:
            file_path (str): Path to the file in the sandbox.

        Returns:
            bytes | None: File content as bytes, or None if download fails.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
