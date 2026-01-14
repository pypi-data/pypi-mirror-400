from gllm_inference.schema import Attachment as Attachment
from gllm_tools.code_interpreter.code_sandbox.sandbox import BaseSandbox as BaseSandbox
from typing import Callable

def create_execute_code_tool(sandbox: BaseSandbox, execution_outputs: list[str], files: list[Attachment] = None) -> Callable:
    """Create the execute code tool with bound context.

    Args:
        sandbox (BaseSandbox): The sandbox instance for code execution.
        execution_outputs (list[str]): List to store execution outputs.
        files (list[Attachment], optional): List of files available for execution. Defaults to None.

    Returns:
        Callable: The execute code tool function.
    """
