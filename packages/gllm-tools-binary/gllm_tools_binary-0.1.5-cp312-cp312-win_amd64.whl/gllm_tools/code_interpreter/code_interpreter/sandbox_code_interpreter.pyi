from _typeshed import Incomplete
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker
from gllm_inference.schema import Attachment, LMOutput, ToolCall as ToolCall
from gllm_tools.code_interpreter.code_interpreter.code_interpreter import BaseCodeInterpreter as BaseCodeInterpreter
from gllm_tools.code_interpreter.code_interpreter.tools import create_execute_code_tool as create_execute_code_tool
from gllm_tools.code_interpreter.code_sandbox.sandbox import BaseSandbox as BaseSandbox
from typing import Any

logger: Incomplete

class SandboxCodeInterpreter(BaseCodeInterpreter):
    """Code interpreter that uses LM invoker with sandbox execution.

    This implementation leverages LM invoker for structured prompt building,
    language model invocation, and request processing while maintaining sandbox execution
    capabilities.


    Attributes:
        sandbox (BaseSandbox): The sandbox instance used for code execution.
        lm_invoker (BaseLMInvoker): Language model invoker for generating responses.
    """
    sandbox: Incomplete
    lm_invoker: Incomplete
    def __init__(self, sandbox: BaseSandbox, lm_invoker: BaseLMInvoker) -> None:
        """Initialize the sandbox-based code interpreter.

        Args:
            sandbox (BaseSandbox): The sandbox instance to use for code execution.
            lm_invoker (BaseLMInvoker): Language model invoker for generating responses.

        Raises:
            TypeError: If lm_invoker is not a BaseLMInvoker instance.
        """
    async def execute(self, message: str, files: list[Attachment] | None = None, **kwargs: Any) -> LMOutput:
        """Send a message to the LM invoker and get a response with code execution capabilities.

        Args:
            message (str): The user message/query.
            files (list[Attachment] | None, optional): Optional files for the execution. Defaults to None.
            **kwargs (Any): Additional parameters for the execution.

        Returns:
            LMOutput: Complete response including text, execution results, and output files.

        Raises:
            Exception: If the LM invocation fails.
        """
