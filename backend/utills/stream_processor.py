# stream_processor.py LangGraph ke raw streaming events ko filter, clean, format, aur transform karke frontend-friendly real-time messages banata hai, jisme agent responses, tool executions, aur workflow updates clearly separated hote hain.


from typing import Any, AsyncIterable, AsyncGenerator, Dict, List, Optional, Tuple, Union

# These classes are assumed LangChain-compatible Python equivalents
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


# TYPES

StreamOutput = Dict[str, Any]
MessageContent = Dict[str, Any]

SubgraphEvent = Tuple[List[str], str, Any]
ParentEvent = Tuple[str, Any]
StreamEvent = Union[SubgraphEvent, ParentEvent]


# BUILDER TOOL TYPES

class BuilderToolBase:
    def __init__(
        self,
        tool_name: str,
        display_title: str,
        get_custom_display_title=None,
    ):
        self.toolName = tool_name
        self.displayTitle = display_title
        self.getCustomDisplayTitle = get_custom_display_title


# CONFIGURATION

DEFAULT_WORKFLOW_UPDATE_TOOLS = [
    "add_nodes",
    "connect_nodes",
    "update_node_parameters",
    "remove_node",
]

EMITTING_NODES = ["agent", "responder"]

SKIPPED_NODES = [
    "supervisor",
    "tools",
    "cleanup_dangling_tool_calls",
    "create_workflow_name",
    "auto_compact_messages",
    "configurator_subgraph",
    "discovery_subgraph",
    "builder_subgraph",
]

SKIPPED_SUBGRAPH_PREFIXES = [
    "discovery_subgraph",
    "builder_subgraph",
    "configurator_subgraph",
]


# FILTERING LOGIC


def is_from_skipped_subgraph(namespace: List[str]) -> bool:
    return any(
        ns.startswith(prefix)
        for ns in namespace
        for prefix in SKIPPED_SUBGRAPH_PREFIXES
    )


def should_skip_node(node_name: str) -> bool:
    return node_name in SKIPPED_NODES


def should_emit_from_node(node_name: str) -> bool:
    return node_name in EMITTING_NODES


def has_message_in_update(update: Any) -> bool:
    return isinstance(update, dict) and isinstance(update.get("messages"), list)


def should_filter_subgraph_update(namespace: List[str], data: Dict[str, Any]) -> bool:
    if not is_from_skipped_subgraph(namespace):
        return False

    for node_name, update in data.items():
        if should_skip_node(node_name):
            continue
        if has_message_in_update(update):
            return True

    return False


def is_subgraph_event(event: Any) -> bool:
    return (
        isinstance(event, tuple)
        and len(event) == 3
        and isinstance(event[0], list)
    )


def is_parent_event(event: Any) -> bool:
    return (
        isinstance(event, tuple)
        and len(event) == 2
        and isinstance(event[0], str)
    )

# CONTENT EXTRACTION


def extract_message_content(messages: List[MessageContent]) -> Optional[str]:
    if not messages:
        return None

    last = messages[-1]
    content = last.get("content")

    if not content:
        return None

    if isinstance(content, list):
        text = "\n".join(
            c.get("text", "")
            for c in content
            if isinstance(c, dict) and c.get("type") == "text"
        )
        return text or None

    return content


def clean_context_tags(text: str) -> str:
    import re
    return re.sub(
        r"\n*<current_workflow_json>[\s\S]*?</current_execution_nodes_schemas>",
        "",
        text,
    )


# CHUNK PROCESSORS

def process_operations_update(update: Any) -> Optional[StreamOutput]:
    if not isinstance(update, dict):
        return None

    if "workflowJSON" not in update or "workflowOperations" not in update:
        return None

    return {
        "messages": [{
            "role": "assistant",
            "type": "workflow-updated",
            "codeSnippet": __import__("json").dumps(update["workflowJSON"], indent=2),
        }]
    }


def process_agent_node_update(node_name: str, update: Any) -> Optional[StreamOutput]:
    if not should_emit_from_node(node_name):
        return None

    if not isinstance(update, dict):
        return None

    messages = update.get("messages")
    if not messages:
        return None

    content = extract_message_content(messages)
    if not content or "<current_workflow_json>" in content:
        return None

    return {
        "messages": [{
            "role": "assistant",
            "type": "message",
            "text": content,
        }]
    }


def process_tool_chunk(chunk: Any) -> Optional[StreamOutput]:
    if isinstance(chunk, dict) and chunk.get("type") == "tool":
        return {"messages": [chunk]}
    return None


# MAIN STREAM PROCESSOR


def process_updates_chunk(node_update: Dict[str, Any]) -> Optional[StreamOutput]:
    if not isinstance(node_update, dict):
        return None

    if node_update.get("delete_messages") or node_update.get("compact_messages"):
        return None

    if "process_operations" in node_update:
        return process_operations_update(node_update["process_operations"])

    for node_name, update in node_update.items():
        if should_skip_node(node_name):
            continue

        result = process_agent_node_update(node_name, update)
        if result:
            return result

    return None


def process_stream_chunk(stream_mode: str, chunk: Any) -> Optional[StreamOutput]:
    if stream_mode == "updates":
        return process_updates_chunk(chunk)

    if stream_mode == "custom":
        return process_tool_chunk(chunk)

    return None


def process_subgraph_event(event: SubgraphEvent) -> Optional[StreamOutput]:
    namespace, stream_mode, data = event

    if (
        stream_mode == "updates"
        and isinstance(data, dict)
        and should_filter_subgraph_update(namespace, data)
    ):
        return None

    return process_stream_chunk(stream_mode, data)


def process_parent_event(event: ParentEvent) -> Optional[StreamOutput]:
    stream_mode, chunk = event
    return process_stream_chunk(stream_mode, chunk)


def process_event(event: StreamEvent) -> Optional[StreamOutput]:
    if is_subgraph_event(event):
        return process_subgraph_event(event)

    if is_parent_event(event):
        return process_parent_event(event)

    return None


async def createStreamProcessor(
    stream: AsyncIterable[StreamEvent],
) -> AsyncGenerator[StreamOutput, None]:
    async for event in stream:
        result = process_event(event)
        if result:
            yield result


# MESSAGE FORMATTING


def extract_human_message_text(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            c.get("text", "")
            for c in content
            if isinstance(c, dict) and c.get("type") == "text"
        )

    return ""


def format_human_message(msg: HumanMessage) -> Dict[str, Any]:
    raw = extract_human_message_text(msg.content)
    return {
        "role": "user",
        "type": "message",
        "text": clean_context_tags(raw),
    }


def process_ai_message_content(msg: AIMessage) -> List[Dict[str, Any]]:
    if not msg.content:
        return []

    if isinstance(msg.content, list):
        return [
            {
                "role": "assistant",
                "type": "message",
                "text": c["text"],
            }
            for c in msg.content
            if isinstance(c, dict) and c.get("type") == "text"
        ]

    return [{
        "role": "assistant",
        "type": "message",
        "text": msg.content,
    }]


def create_tool_call_message(tool_call: Any, builder_tool: Optional[BuilderToolBase]):
    return {
        "id": tool_call["id"],
        "toolCallId": tool_call["id"],
        "role": "assistant",
        "type": "tool",
        "toolName": tool_call["name"],
        "displayTitle": builder_tool.displayTitle if builder_tool else None,
        "customDisplayTitle": (
            builder_tool.getCustomDisplayTitle(tool_call.get("args"))
            if builder_tool and builder_tool.getCustomDisplayTitle
            else None
        ),
        "status": "completed",
        "updates": [{
            "type": "input",
            "data": tool_call.get("args", {}),
        }],
    }


def formatMessages(
    messages: List[Union[AIMessage, HumanMessage, ToolMessage]],
    builder_tools: Optional[List[BuilderToolBase]] = None,
) -> List[Dict[str, Any]]:
    formatted: List[Dict[str, Any]] = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted.append(format_human_message(msg))

        elif isinstance(msg, AIMessage):
            formatted.extend(process_ai_message_content(msg))

            if msg.tool_calls:
                for tc in msg.tool_calls:
                    tool = next(
                        (bt for bt in builder_tools or [] if bt.toolName == tc["name"]),
                        None,
                    )
                    formatted.append(create_tool_call_message(tc, tool))

        elif isinstance(msg, ToolMessage):
            for m in reversed(formatted):
                if m.get("type") == "tool" and m.get("id") == msg.tool_call_id:
                    m.setdefault("updates", []).append({
                        "type": "output",
                        "data": {"result": msg.content} if isinstance(msg.content, str) else msg.content,
                    })
                    break

    return formatted
