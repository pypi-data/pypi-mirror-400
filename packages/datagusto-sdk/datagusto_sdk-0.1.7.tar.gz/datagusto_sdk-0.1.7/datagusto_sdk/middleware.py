import inspect
import json
import logging
import os
import hashlib
import traceback
import urllib.request
import urllib.error
from typing import Any

from pydantic import BaseModel, TypeAdapter
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
)
from langgraph.runtime import Runtime


# =============================================================================
# Method 3: Class-based implementation (Recommended: when multiple hooks or configuration are needed)
# =============================================================================


class DatagustoSafetyMiddleware(AgentMiddleware):
    """
    Middleware class for extracting and managing tool definitions.

    Features:
        - before_agent: Tool definition extraction and logging
        - Configurable options (verbose logging, filtering, etc.)
    """

    def __init__(
        self,
        verbose: bool = True,
        include_schema: bool = True,
        tool_filter: list[str] | None = None,
        server_url: str | None = None,
        api_key: str | None = None,
    ):
        """
        Args:
            verbose: Whether to output detailed logs
            include_schema: Whether to include argument schema
            tool_filter: List of tool names to extract (None for all)
            server_url: Server URL (if None, reads from SERVER_URL environment variable)
            api_key: API key (if None, reads from API_KEY environment variable)
        """
        self.verbose = verbose
        self.include_schema = include_schema
        self.tool_filter = tool_filter
        self.server_url = server_url or os.getenv("SERVER_URL", "").strip()
        self.api_key = api_key or os.getenv("API_KEY", "").strip()
        self.extracted_tools: list[dict[str, Any]] = []
        # Prevent duplicate API registration submissions
        self._latest_payload_hash: str | None = None
        self._registered_payload_hash: str | None = None
        # Prevent duplicate alignment submissions (user prompt)
        self._last_alignment_user_instruction_hash: str | None = None
        # session_id from alignment API response (used in validate)
        self._alignment_session_id: str | None = None
        # Logger for this middleware
        self.logger = logging.getLogger(self.__class__.__name__)

    def before_agent(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """Hook before agent starts.

        Note:
            langgraph.runtime.Runtime does not contain tools, so extraction is not done here.
            The actual tool list is in ModelRequest.tools, so extraction is done in wrap_model_call.
        """
        self.extracted_tools = []
        self._latest_payload_hash = None
        self._last_alignment_user_instruction_hash = None
        self._alignment_session_id = None
        return None

    def before_model(
        self, state: AgentState, runtime: Runtime
    ) -> dict[str, Any] | None:
        """Hook immediately before model invocation.

        Tool registration/alignment submission requires request.tools / request.messages,
        so they are consolidated in wrap_model_call().
        """
        return None

    def wrap_model_call(self, request, handler):
        """Hook immediately before model invocation (preprocessing).

        Execution order:
            1) Extract tool definitions
            2) Register tools (if there are changes)
            3) Send alignment (if there are changes)
            4) Call LLM with handler(request)
        """
        try:
            tools = getattr(request, "tools", None) or []
            self._extract_from_tools(tools)
            if self.verbose:
                self._log_tools()
        except Exception:
            # Don't break agent execution if extraction fails
            pass

        # 2) Register tools (if there are changes)
        if (
            self._latest_payload_hash
            and self._registered_payload_hash != self._latest_payload_hash
            and self.server_url
            and self.api_key
        ):
            try:
                result = self.register_tools()
                if result.get("ok"):
                    self._registered_payload_hash = self._latest_payload_hash
            except Exception:
                # Don't break agent execution if registration fails
                if self.verbose:
                    self.logger.error(
                        "\n" + "=" * 60 + "\n"
                        "❌ register_tools failed\n"
                        "=" * 60 + "\n" + traceback.format_exc() + "\n"
                        "=" * 60 + "\n"
                    )

        # 3) Send alignment (if there are changes)
        try:
            messages = getattr(request, "messages", None) or []
            user_instruction = self._extract_latest_user_instruction_from_messages(
                messages
            )
        except Exception:
            user_instruction = None

        if user_instruction and self.server_url and self.api_key:
            h = hashlib.sha256(user_instruction.encode("utf-8")).hexdigest()
            if h != self._last_alignment_user_instruction_hash:
                try:
                    result = self.post_alignment(user_instruction=user_instruction)
                    if result.get("ok"):
                        self._last_alignment_user_instruction_hash = h
                except Exception:
                    # Don't break agent execution if alignment submission fails
                    if self.verbose:
                        self.logger.error(
                            "\n" + "=" * 60 + "\n"
                            "❌ post_alignment failed\n"
                            "=" * 60 + "\n" + traceback.format_exc() + "\n"
                            "=" * 60 + "\n"
                        )

        return handler(request)

    def wrap_tool_call(self, request, handler):
        """Hook before tool execution.

        Call validate API immediately before tool execution (equivalent to curl).

        - session_id: session_id from the previous alignment API response
        - process_name: Tool name
        - timing: on_start
        - context.input: Tool input variables (tool_call.args)
        """
        session_id = self._alignment_session_id
        if not session_id:
            return handler(request)

        if not (self.server_url and self.api_key):
            return handler(request)

        # Extract tool name/arguments from ToolCallRequest (best effort)
        tool_call = getattr(request, "tool_call", None) or {}
        tool_obj = getattr(request, "tool", None)
        process_name = (
            getattr(tool_obj, "name", None) or tool_call.get("name") or "unknown_tool"
        )
        args = tool_call.get("args")
        if args is None:
            args = {}

        # --- on_start ---
        try:
            result_start = self.post_validate(
                session_id=session_id,
                process_name=str(process_name),
                timing="on_start",
                context_input=args,
                context_output=None,
            )
        except Exception:
            if self.verbose:
                self.logger.error(
                    "\n" + "=" * 60 + "\n"
                    "❌ post_validate(on_start) failed\n"
                    "=" * 60 + "\n" + traceback.format_exc() + "\n"
                    "=" * 60 + "\n"
                )
        else:
            resp_json = result_start.get("response_json")
            if isinstance(resp_json, dict) and resp_json.get("should_proceed") is False:
                raise RuntimeError(
                    "Safety validate blocked tool execution (on_start). "
                    f"process_name={process_name} session_id={session_id} "
                    f"response={json.dumps(resp_json, ensure_ascii=False)}"
                )

        # Execute tool
        tool_result = handler(request)

        # --- on_end ---
        output_payload = self._serialize_tool_output(tool_result)
        try:
            result_end = self.post_validate(
                session_id=session_id,
                process_name=str(process_name),
                timing="on_end",
                context_input=args,
                context_output=output_payload,
            )
        except Exception:
            if self.verbose:
                self.logger.error(
                    "\n" + "=" * 60 + "\n"
                    "❌ post_validate(on_end) failed\n"
                    "=" * 60 + "\n" + traceback.format_exc() + "\n"
                    "=" * 60 + "\n"
                )
        else:
            resp_json = result_end.get("response_json")
            if isinstance(resp_json, dict) and resp_json.get("should_proceed") is False:
                raise RuntimeError(
                    "Safety validate blocked further processing (on_end). "
                    f"process_name={process_name} session_id={session_id} "
                    f"response={json.dumps(resp_json, ensure_ascii=False)}"
                )

        return tool_result

    def _extract_from_tools(self, tools: list[Any]) -> None:
        """Extract from BaseTool list (+ built-in dict) and update self.extracted_tools.

        Return format (aligned with attached JSON):
            {
              "name": str,
              "description": str,
              "input_schema": { ... JSON Schema ... },
              "output_schema": { ... JSON Schema ... }  # Always type=object
            }
        """
        self.extracted_tools = []

        for tool_def in tools:
            # Skip built-in provider tools that may be dict (extend later if needed)
            if isinstance(tool_def, dict):
                continue

            tool_name = getattr(tool_def, "name", "unknown")

            # Filtering
            if self.tool_filter and tool_name not in self.tool_filter:
                continue

            description = getattr(tool_def, "description", "")
            definition: dict[str, Any] = {"name": tool_name, "description": description}

            # Schema extraction (optional)
            if self.include_schema:
                definition["input_schema"] = self._build_input_schema(tool_def)
                definition["output_schema"] = self._build_output_schema(tool_def)

            self.extracted_tools.append(definition)

        # Update payload hash (used for diff detection in next before_model)
        self._latest_payload_hash = self._hash_payload(self.build_tools_payload())

    def _hash_payload(self, payload: dict[str, Any]) -> str:
        """Stable hash of payload (JSON serialized in dictionary order)"""
        data = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def _extract_latest_user_instruction_from_messages(
        self, messages: list[Any]
    ) -> str | None:
        """Extract the latest user prompt (HumanMessage) from messages (best effort)."""
        for msg in reversed(messages):
            try:
                msg_type = getattr(msg, "type", None) or getattr(msg, "role", None)
                if msg_type == "human":
                    content = getattr(msg, "content", None)
                    if content is None:
                        return None
                    return (
                        content
                        if isinstance(content, str)
                        else json.dumps(content, ensure_ascii=False)
                    )
            except Exception:
                continue
        return None

    def _serialize_tool_output(self, tool_result: Any) -> Any:
        """Convert tool execution result to a format suitable for validate's context.output (best effort)."""
        # ToolMessage-like format (langchain_core.messages.ToolMessage)
        content = getattr(tool_result, "content", None)
        status = getattr(tool_result, "status", None)
        name = getattr(tool_result, "name", None)
        tool_call_id = getattr(tool_result, "tool_call_id", None)

        if content is not None or status is not None or name is not None:
            out: dict[str, Any] = {}
            if name is not None:
                out["name"] = name
            if tool_call_id is not None:
                out["tool_call_id"] = tool_call_id
            if status is not None:
                out["status"] = status
            if content is not None:
                out["content"] = content
            return out

        # dict/list as-is
        if (
            isinstance(tool_result, (dict, list, str, int, float, bool))
            or tool_result is None
        ):
            return tool_result

        # Last resort
        return {"repr": repr(tool_result)}

    def post_alignment(
        self,
        *,
        user_instruction: str,
        timeout_sec: float = 600.0,
    ) -> dict[str, Any]:
        """Send user prompt to alignment API (same format as register_tools)."""
        if not self.server_url:
            raise ValueError("SERVER_URL is required")
        if not self.api_key:
            raise ValueError("API_KEY is required")

        endpoint = "/api/v1/public/safety/sessions/alignment"
        url = self.server_url.rstrip("/") + endpoint
        body_text = json.dumps(
            {"user_instruction": user_instruction}, ensure_ascii=False
        )
        body = body_text.encode("utf-8")

        if self.verbose:
            self.logger.info(
                "\n" + "=" * 60 + "\n"
                "📤 post_alignment request body\n"
                "=" * 60 + "\n" + body_text + "\n"
                "=" * 60 + "\n"
            )

        req = urllib.request.Request(
            url=url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                try:
                    parsed = json.loads(raw) if raw else None
                except Exception:
                    parsed = None
                if self.verbose:
                    self.logger.info(
                        "\n" + "=" * 60 + "\n"
                        f"📥 post_alignment response (status={resp.status})\n"
                        "=" * 60 + "\n" + raw + "\n"
                        "=" * 60 + "\n"
                    )
                # Save session_id (used in validate in wrap_tool_call)
                if isinstance(parsed, dict):
                    sid = parsed.get("session_id")
                    if isinstance(sid, str) and sid:
                        self._alignment_session_id = sid
                return {
                    "url": url,
                    "status": resp.status,
                    "ok": 200 <= resp.status < 300,
                    "response_text": raw,
                    "response_json": parsed,
                }
        except urllib.error.HTTPError as e:
            raw = (
                e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
            )
            try:
                parsed = json.loads(raw) if raw else None
            except Exception:
                parsed = None
            if self.verbose:
                self.logger.error(
                    "\n" + "=" * 60 + "\n"
                    f"📥 post_alignment error response (status={getattr(e, 'code', None)})\n"
                    "=" * 60 + "\n" + raw + "\n"
                    "=" * 60 + "\n"
                )
            return {
                "url": url,
                "status": getattr(e, "code", None),
                "ok": False,
                "response_text": raw,
                "response_json": parsed,
                "error": str(e),
            }
        except urllib.error.URLError as e:
            if self.verbose:
                self.logger.error(
                    "\n" + "=" * 60 + "\n"
                    "📥 post_alignment urlopen error (URLError)\n"
                    "=" * 60 + "\n" + str(e) + "\n"
                    "=" * 60 + "\n"
                )
            return {
                "url": url,
                "status": None,
                "ok": False,
                "response_text": "",
                "response_json": None,
                "error": str(e),
            }

    def post_validate(
        self,
        *,
        session_id: str,
        process_name: str,
        timing: str,
        context_input: dict[str, Any],
        context_output: Any | None,
        trace_id: str | None = None,
        timeout_sec: float = 600.0,
    ) -> dict[str, Any]:
        """Call validate API (same format as register_tools)."""
        if not self.server_url:
            raise ValueError("SERVER_URL is required")
        if not self.api_key:
            raise ValueError("API_KEY is required")

        endpoint = "/api/v1/public/safety/sessions/validate"
        url = self.server_url.rstrip("/") + endpoint
        payload: dict[str, Any] = {
            "session_id": session_id,
            "trace_id": trace_id,
            "process_name": process_name,
            "process_type": "tool",
            "timing": timing,
            "input": context_input,
            "output": context_output,
        }
        # Don't send trace_id if not specified (nullable in OpenAPI, but avoid unnecessary null)
        if trace_id is None:
            payload.pop("trace_id", None)
        body_text = json.dumps(payload, ensure_ascii=False)
        body = body_text.encode("utf-8")

        if self.verbose:
            self.logger.info(
                "\n" + "=" * 60 + "\n"
                "📤 post_validate request body\n"
                "=" * 60 + "\n" + body_text + "\n"
                "=" * 60 + "\n"
            )

        req = urllib.request.Request(
            url=url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                try:
                    parsed = json.loads(raw) if raw else None
                except Exception:
                    parsed = None
                if self.verbose:
                    self.logger.info(
                        "\n" + "=" * 60 + "\n"
                        f"📥 post_validate response (status={resp.status})\n"
                        "=" * 60 + "\n" + raw + "\n"
                        "=" * 60 + "\n"
                    )
                return {
                    "url": url,
                    "status": resp.status,
                    "ok": 200 <= resp.status < 300,
                    "response_text": raw,
                    "response_json": parsed,
                }
        except urllib.error.HTTPError as e:
            raw = (
                e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
            )
            try:
                parsed = json.loads(raw) if raw else None
            except Exception:
                parsed = None
            if self.verbose:
                self.logger.error(
                    "\n" + "=" * 60 + "\n"
                    f"📥 post_validate error response (status={getattr(e, 'code', None)})\n"
                    "=" * 60 + "\n" + raw + "\n"
                    "=" * 60 + "\n"
                )
            return {
                "url": url,
                "status": getattr(e, "code", None),
                "ok": False,
                "response_text": raw,
                "response_json": parsed,
                "error": str(e),
            }
        except urllib.error.URLError as e:
            if self.verbose:
                self.logger.error(
                    "\n" + "=" * 60 + "\n"
                    "📥 post_validate urlopen error (URLError)\n"
                    "=" * 60 + "\n" + str(e) + "\n"
                    "=" * 60 + "\n"
                )
            return {
                "url": url,
                "status": None,
                "ok": False,
                "response_text": "",
                "response_json": None,
                "error": str(e),
            }

    def _build_input_schema(self, tool_def: Any) -> dict[str, Any]:
        """Generate input schema (JSON Schema). Always returns object."""
        default: dict[str, Any] = {"type": "object", "properties": {}}

        schema_obj = getattr(tool_def, "args_schema", None)
        if not schema_obj:
            return default

        try:
            # pydantic v2: model_json_schema / v1: schema
            if hasattr(schema_obj, "model_json_schema"):
                schema = schema_obj.model_json_schema()
            elif hasattr(schema_obj, "schema"):
                schema = schema_obj.schema()
            else:
                return default
        except Exception:
            return default

        return self._coerce_object_schema(schema, default=default) or default

    def _build_output_schema(self, tool_def: Any) -> dict[str, Any]:
        """Generate output schema (JSON Schema). Always returns object.

        Policy:
            - If return type annotation exists and can be converted to JSON Schema, fill properties (best effort)
            - Otherwise return empty object schema
        """
        default: dict[str, Any] = {"type": "object", "properties": {}}

        func = getattr(tool_def, "func", None)
        if func is None:
            return default

        try:
            return_ann = inspect.signature(func).return_annotation
        except Exception:
            return default

        if return_ann is inspect.Signature.empty or return_ann is None:
            return default

        schema: dict[str, Any] | None = None
        try:
            # pydantic BaseModel subclass
            if isinstance(return_ann, type) and issubclass(return_ann, BaseModel):
                schema = return_ann.model_json_schema()
            else:
                schema = TypeAdapter(return_ann).json_schema()
        except Exception:
            schema = None

        if not schema:
            return default

        # If return value is object schema, use as-is (with completion)
        obj = self._coerce_object_schema(schema, default=None)
        if obj is not None:
            return obj

        # For non-object: store as result property (always maintain object)
        return {"type": "object", "properties": {"result": schema}}

    def _coerce_object_schema(
        self, schema: dict[str, Any], *, default: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        """Normalize JSON Schema to object form.

        - If already object, return as-is (allow even without properties/required)
        - If not object, return default (None if default=None)
        """
        if not isinstance(schema, dict):
            return default

        if schema.get("type") == "object" or "properties" in schema:
            # May lack "type", so complete it
            if schema.get("type") is None:
                schema = {**schema, "type": "object"}
            # properties may not exist, so complete it (empty is OK)
            if "properties" not in schema:
                schema = {**schema, "properties": {}}
            return schema

        return default

    def _log_tools(self) -> None:
        """Log extracted tool information"""
        self.logger.info("\n" + "=" * 60)
        self.logger.info("🔧 DatagustoSafetyMiddleware - Tool Definitions")
        self.logger.info("=" * 60)

        for tool_def in self.extracted_tools:
            self.logger.info(f"\n📌 {tool_def['name']}")
            self.logger.info(f"   Description: {tool_def['description']}")
            if "input_schema" in tool_def:
                self.logger.info(f"   input_schema: {tool_def['input_schema']}")
            if "output_schema" in tool_def:
                self.logger.info(f"   output_schema: {tool_def['output_schema']}")

        self.logger.info(f"\nTotal: {len(self.extracted_tools)} tools")
        self.logger.info("=" * 60 + "\n")

    def get_extracted_tools(self) -> list[dict[str, Any]]:
        """Get extracted tool definitions"""
        return self.extracted_tools

    def build_tools_payload(self) -> dict[str, Any]:
        """Generate payload to send to registration API (JSON body equivalent to curl -d @file)"""
        return {"tools": self.get_extracted_tools()}

    def register_tools(
        self,
        *,
        timeout_sec: float = 600.0,
    ) -> dict[str, Any]:
        """Send extracted tool definitions to registration API."""
        if not self.server_url:
            raise ValueError("SERVER_URL is required")
        if not self.api_key:
            raise ValueError("API_KEY is required")

        endpoint = "/api/v1/public/safety/tools/register"
        url = self.server_url.rstrip("/") + endpoint
        payload = self.build_tools_payload()
        body_text = json.dumps(payload, ensure_ascii=False)
        body = body_text.encode("utf-8")

        if self.verbose:
            self.logger.info(
                "\n" + "=" * 60 + "\n"
                "📤 register_tools request body\n"
                "=" * 60 + "\n" + body_text + "\n"
                "=" * 60 + "\n"
            )

        req = urllib.request.Request(
            url=url,
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                try:
                    parsed = json.loads(raw) if raw else None
                except Exception:
                    parsed = None
                if self.verbose:
                    self.logger.info(
                        "\n" + "=" * 60 + "\n"
                        f"📥 register_tools response (status={resp.status})\n"
                        "=" * 60 + "\n" + raw + "\n"
                        "=" * 60 + "\n"
                    )
                return {
                    "url": url,
                    "status": resp.status,
                    "ok": 200 <= resp.status < 300,
                    "response_text": raw,
                    "response_json": parsed,
                }
        except urllib.error.HTTPError as e:
            raw = (
                e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
            )
            try:
                parsed = json.loads(raw) if raw else None
            except Exception:
                parsed = None
            if self.verbose:
                self.logger.error(
                    "\n" + "=" * 60 + "\n"
                    f"📥 register_tools error response (status={getattr(e, 'code', None)})\n"
                    "=" * 60 + "\n" + raw + "\n"
                    "=" * 60 + "\n"
                )
            return {
                "url": url,
                "status": getattr(e, "code", None),
                "ok": False,
                "response_text": raw,
                "response_json": parsed,
                "error": str(e),
            }
        except urllib.error.URLError as e:
            if self.verbose:
                self.logger.error(
                    "\n" + "=" * 60 + "\n"
                    "📥 register_tools urlopen error (URLError)\n"
                    "=" * 60 + "\n" + str(e) + "\n"
                    "=" * 60 + "\n"
                )
            return {
                "url": url,
                "status": None,
                "ok": False,
                "response_text": "",
                "response_json": None,
                "error": str(e),
            }
