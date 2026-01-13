from typing import Literal, cast

ToolType = Literal["KNOWLEDGE_BASE_SEARCH"]

TOOL_TYPE_VALUES: set[ToolType] = {
    "KNOWLEDGE_BASE_SEARCH",
}


def check_tool_type(value: str) -> ToolType:
    if value in TOOL_TYPE_VALUES:
        return cast(ToolType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {TOOL_TYPE_VALUES!r}")
