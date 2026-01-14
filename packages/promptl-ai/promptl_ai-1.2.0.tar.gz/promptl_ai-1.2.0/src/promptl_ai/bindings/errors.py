from typing import Any, Dict, Union

from promptl_ai.bindings.types import Error


class PromptlError(Exception):
    cause: Error

    def __init__(
        self,
        cause: Union[Error, Dict[str, Any]],
    ):
        self.cause = Error.model_validate(cause)
        super().__init__(self.cause.message)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PromptlError) and self.cause == other.cause
