"""Token limit middleware and utilities for MCP servers."""
# pylint: disable=duplicate-code

import functools
import inspect
import logging
import types
from collections.abc import Awaitable
from datetime import datetime
from pathlib import PurePosixPath
from typing import Any, Callable, Optional, Union, get_args, get_origin

import aiofiles
from fastmcp.server.dependencies import get_context
from fastmcp.server.middleware.middleware import Middleware, MiddlewareContext
from fastmcp.tools.tool import ToolResult
from mcp.types import TextContent
from pydantic import TypeAdapter

from aixtools.agents.prompt import count_tokens
from aixtools.server.path import container_to_host_path
from aixtools.utils.truncation import truncate_text_head_tail

# Directory where full tool responses are saved when truncated
FULL_TOOL_RESPONSES_DIR = "/workspace/full_tool_responses/"
MAX_TOOL_RETURN_TOKENS = 10000

logger = logging.Logger(__name__)


class FormatPreviewError(Exception):
    """Error when formatting a preview of truncated tool response."""


# This implementation is at parity with the way PydanticAI 1.12.0 serializes tool responses into context
_tool_return_adapter = TypeAdapter(
    Any, config={"defer_build": True, "ser_json_bytes": "base64", "val_json_bytes": "base64"}
)


def serialize_result(result: Any, indent: int | None = None) -> str:
    """Serialize a result in the same way as PydanticAI.

    Args:
        result: The object to serialize
        indent: Optional indentation level for pretty-printing (None for compact output)

    Returns:
        JSON string representation
    """
    try:
        return _tool_return_adapter.dump_json(result, indent=indent).decode()  # type: ignore
    except Exception as e:
        raise ValueError(f"Result must be serializable: {e}") from e


def get_base_filename() -> str:
    """Generate a base filename for tool responses with timestamp.

    Returns:
        Base filename without extension (e.g., 'full_tool_response_20240106_123456_789')
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
    return f"full_tool_response_{timestamp}"


async def write_to_workspace(content: str, base_filename: str, extension: str) -> str:
    """Write content to a file in the workspace and return the container path.

    Args:
        content: The content to write
        base_filename: Base filename without extension
        extension: File extension (without dot), e.g., 'txt' or 'json'

    Returns:
        Container path as string
    """
    container_path = PurePosixPath(FULL_TOOL_RESPONSES_DIR) / f"{base_filename}.{extension}"

    fastmcp_ctx = get_context()
    host_path = container_to_host_path(container_path, ctx=fastmcp_ctx)

    if host_path is None:
        raise RuntimeError(f"Failed to convert container path to host path: {container_path}")

    host_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(host_path, "w", encoding="utf-8") as f:
        await f.write(content)

    return str(container_path)


def format_preview(
    content: str,
    preview_chars_start: int,
    preview_chars_end: int,
    format_preview_fn: Optional[Callable[[str], str]],
) -> str:
    """Format the full preview message with prefix and content."""
    if format_preview_fn is not None:
        try:
            preview_content = format_preview_fn(content)
        except Exception as e:  # pylint: disable=broad-exception-caught
            raise FormatPreviewError(f"Error in custom format_preview_fn: {e}") from e
    else:
        preview_content, _ = truncate_text_head_tail(content, preview_chars_start, preview_chars_end)

    return (
        f"Tool call response exceeded max tokens for context; full response saved to `{FULL_TOOL_RESPONSES_DIR}` "
        "instead.\nDo not attempt to read the whole response from the file but instead use the tools available"
        "to you to search for relevant content within the file.\n"
        "Response preview:\n\n"
        f"{preview_content}"
    )


def _truncate_structured_data(data: Any, max_str_length: int = 500, max_list_items: int = 10) -> Any:
    """Recursively truncate long strings and limit list sizes in a dict/list structure.

    Args:
        data: The data structure to truncate (dict, list, or other)
        max_str_length: Maximum length for string values before truncation
        max_list_items: Maximum number of items to keep in lists

    Returns:
        A copy of the data with long strings truncated and lists limited

    Note:
        - Tuples do not need explicit handling because `structured_content` has already been
        processed by `pydantic_core.to_jsonable_python()` in `ToolResult.init`, which
        converts tuples to lists (since JSON doesn't have a tuple type).
        - When called from `TokenLimitMiddleware`, the top-level data is always a dict because
        `ToolResult.init` validates that `structured_content` must be either None or dict,
        raising `ValueError` otherwise.
    """

    # Helper for recursive calls with fixed parameters
    def recurse(item: Any) -> Any:
        return _truncate_structured_data(item, max_str_length, max_list_items)

    if isinstance(data, dict):
        return {key: recurse(value) for key, value in data.items()}
    if isinstance(data, list):
        # Limit list size to prevent excessive token usage
        # Keep head and tail items, removing middle (consistent with string truncation)
        if len(data) > max_list_items:
            head_items = max_list_items // 2
            tail_items = max_list_items - head_items
            return [recurse(item) for item in data[:head_items]] + [recurse(item) for item in data[-tail_items:]]
        return [recurse(item) for item in data]
    if isinstance(data, str) and len(data) > max_str_length:
        preview_end = min(100, max_str_length // 4)
        preview_start = max_str_length - preview_end - 50  # Leave room for ellipsis message
        truncated, _ = truncate_text_head_tail(data, preview_start, preview_end)
        return f"{truncated}\n...[truncated, full content saved to `{FULL_TOOL_RESPONSES_DIR}`]"
    return data


async def _process_raw_result(
    result: Any,
    max_tokens: int,
    preview_chars_start: int,
    preview_chars_end: int,
    format_preview_fn: Optional[Callable[[str], str]],
) -> Any:
    """Process a raw result and truncate if it exceeds max_tokens.

    Args:
        result: The raw result to process (can be any serializable type)
        max_tokens: Maximum number of tokens allowed before truncation
        preview_chars_start: Number of characters to show from the beginning
        preview_chars_end: Number of characters to show from the end
        format_preview_fn: Optional custom preview formatting function

    Returns:
        The original result or a truncated preview string
    """
    result_str = serialize_result(result)

    token_count = count_tokens(result_str)

    if token_count <= max_tokens:
        return result

    # Write full result to file
    try:
        base_filename = get_base_filename()
        await write_to_workspace(result_str, base_filename, "txt")
    except Exception as e:  # pylint: disable=broad-exception-caught
        raise RuntimeError(
            f"Tool response exceeded {max_tokens} tokens but failed to write to file: {e}\n\n{result_str[:1000]}..."
        ) from e

    # Return preview string
    return format_preview(result_str, preview_chars_start, preview_chars_end, format_preview_fn)


def limit_response(
    max_tokens: int = MAX_TOOL_RETURN_TOKENS,
    preview_chars_start: int = 2000,
    preview_chars_end: int = 2000,
    format_preview_fn: Optional[Callable[[str], str]] = None,
) -> Callable:
    """Decorator to automatically truncate long tool responses and save them to files.

    When a tool response exceeds max_tokens, the full response is written to a fil
    in the workspace and a truncated preview is returned instead.

    Args:
        max_tokens: Maximum number of tokens allowed in a tool response before truncation.
        preview_chars_start: Number of characters to show from the beginning of the content.
        preview_chars_end: Number of characters to show from the end of the content.
        format_preview_fn: Optional function for custom preview formatting. Takes the content string
            and returns a preview string. If passed will overwrite the default behavior.

    Warning: Converts synchronous return types into coroutines that must be awaited.
    Warning: Will convert the response to a string when truncating.

    Usage:
        @limit_response(max_tokens=1000)
        def my_tool():
            return "Very long response..."
    """

    def decorator(func: Callable) -> Callable[..., Awaitable[Any]]:
        sig = inspect.signature(func)
        return_annotation = sig.return_annotation
        is_str_type = False

        if return_annotation != inspect.Signature.empty:
            if return_annotation is str:
                is_str_type = True
            elif get_origin(return_annotation) in (types.UnionType, Union):
                args = get_args(return_annotation)
                is_str_type = str in args

            if not is_str_type:
                logger.warning(  # pylint: disable=logging-fstring-interpolation
                    f"Function '{func.__name__}' is decorated with @limit_response but has a non-str return type "
                    f"annotation: {return_annotation}. The decorator will serialize non-str returns to string, "
                    "which may not be the desired behavior. Consider annotating the return type as 'str' or "
                    "handling truncation explicitly in the function."
                )

        is_coroutine_func = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if is_coroutine_func:
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            if not is_str_type and not isinstance(result, str):
                logger.warning(
                    "Non string tool return serialized to string unexpectedly by limit_response!\n"
                    "Consider adding logic to truncate large return values for this function"
                )
            return await _process_raw_result(
                result, max_tokens, preview_chars_start, preview_chars_end, format_preview_fn
            )

        return wrapper

    return decorator


class TokenLimitMiddleware(Middleware):
    """Middleware to limit tool response size by writing large responses to files.

    When a tool response exceeds max_tokens, the full response is written
    to a file in the workspace and a truncated preview is returned instead.

    WARNING: Never apply this middleware to the file edit MCP, as we want the LLM to
    use the windowed file read and regex search from the file edit MCP to extract the
    relevant information without loading the full response into context.

    Args:
        max_tokens: Maximum number of tokens allowed in a tool response before
            truncation. Defaults to MAX_TOOL_RETURN_TOKENS
        preview_chars_start: Number of characters to show from the beginning
            of the content in the default preview. Defaults to 2000.
        preview_chars_end: Number of characters to show from the end of the
            content in the default preview. Defaults to 2000.
        format_preview_fn: Optional function for custom preview formatting. If passed will
            overwrite the default behavior for truncating tool output.
    """

    def __init__(
        self,
        max_tokens: int = MAX_TOOL_RETURN_TOKENS,
        preview_chars_start: int = 2000,
        preview_chars_end: int = 2000,
        format_preview_fn: Optional[Callable[[str], str]] = None,
    ):
        self.max_tokens = max_tokens
        self.preview_chars_start = preview_chars_start
        self.preview_chars_end = preview_chars_end
        self.format_preview_fn = format_preview_fn

    async def on_call_tool(self, context: MiddlewareContext, call_next) -> ToolResult:  # pylint: disable=too-many-locals
        """Process tool response and limit size if needed."""
        result: ToolResult = await call_next(context)

        # Convert ToolResult to MCP result format for serialization
        mcp_result = result.to_mcp_result()
        result_str = serialize_result(mcp_result)

        token_count = count_tokens(result_str)

        if token_count <= self.max_tokens:
            return result

        # Write full results to appropriate file formats using same base filename
        content_file = None
        structured_file = None
        base_filename = get_base_filename()

        try:
            # Save the full serialized content as text if present
            if result.content:
                content_str = serialize_result(result.content)
                content_file = await write_to_workspace(content_str, base_filename, "txt")

            # Save structured_content as JSON if present - use serialize_result with indent for readability
            if result.structured_content is not None:
                # serialize_result handles special types like bytes (as base64) and pretty-prints with indent
                json_str = serialize_result(result.structured_content, indent=2)
                structured_file = await write_to_workspace(json_str, base_filename, "json")
        except Exception as e:  # pylint: disable=broad-exception-caught
            raise RuntimeError(
                f"Tool response exceeded {self.max_tokens} tokens but failed to write to file: "
                f"{e}\n\n{result_str[:1000]}..."
            ) from e

        # Replace content with preview
        text_content_found = False
        for item in result.content:
            if isinstance(item, TextContent):
                file_ref = f"`{content_file}`" if content_file else f"`{FULL_TOOL_RESPONSES_DIR}`"
                preview_text = format_preview(
                    item.text, self.preview_chars_start, self.preview_chars_end, self.format_preview_fn
                )
                # Update the message to reference the specific file
                preview_text = preview_text.replace(f"`{FULL_TOOL_RESPONSES_DIR}`", file_ref)
                item.text = preview_text
                text_content_found = True
                break

        # If no text content was found but we have structured content, add a text notification
        if not text_content_found and result.structured_content is not None:
            file_ref = f"`{content_file}`" if content_file else f"`{FULL_TOOL_RESPONSES_DIR}`"
            notification_text = (
                f"Tool call response exceeded {self.max_tokens} tokens; full response saved to {file_ref}.\n"
                "Do not attempt to read the whole response from the file but instead use the tools available "
                "to you to search for relevant content within the file."
            )
            result.content.append(TextContent(type="text", text=notification_text))

        # Truncate long strings and limit list sizes in structured_content while preserving structure
        # This keeps the schema valid while reducing token usage
        if result.structured_content is not None:
            result.structured_content = _truncate_structured_data(result.structured_content)
            # Add truncation notice to structured_content since clients often prefer it over content
            assert isinstance(result.structured_content, dict)
            file_ref = f"`{structured_file}`" if structured_file else f"`{FULL_TOOL_RESPONSES_DIR}*.json`"
            result.structured_content["_truncation_notice"] = (
                f"Response exceeded {self.max_tokens} tokens. Full structured data saved to {file_ref}. "
                "This structured data has been truncated (long strings and large lists reduced). "
                "Do not attempt to read the whole JSON file but instead use available tools "
                "to search for relevant content within it."
            )

        return result
