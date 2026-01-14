from abc import ABC, abstractmethod
from gllm_inference.schema import Attachment as Attachment
from gllm_tools.code_interpreter.code_sandbox.models import ExecutionResult as ExecutionResult
from typing import Any

class BaseCodeInterpreter(ABC):
    """Base class for code interpreter implementations."""
    @abstractmethod
    async def execute(self, message: str, files: list[Attachment] | None = None, **kwargs: Any) -> tuple[str, list[ExecutionResult]]:
        """Send a message to the code interpreter and get a response.

        Args:
            message (str): The user message/query.
            files (list[Attachment] | None, optional): Optional files for the execution. Defaults to None.
            **kwargs (Any): Additional parameters for the execution.

        Returns:
            tuple[str, list[ExecutionResult]]: The interpreter's response and execution results.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
