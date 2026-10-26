# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Serve the reasoning_engine ``{class_method, input}`` contract over HTTP."""

import inspect
import json
from typing import Any

from agentplatform.agent_engines.templates.adk import AdkApp
from fastapi import FastAPI, HTTPException, Request, encoders, responses
from starlette.concurrency import iterate_in_threadpool, run_in_threadpool

from app.app_utils import services


def _no_op_instrumentor_builder(project_id: str) -> None:
    """No-op so set_up() keeps the startup instrumentor and generate_content spans."""
    return None


def attach_reasoning_engine_routes(app: FastAPI) -> None:
    """Register reasoning_engine routes that dispatch to an AdkApp."""
    runtime: AdkApp | None = None
    streaming_methods: set[str] = set()
    sync_methods: set[str] = set()

    def get_runtime() -> AdkApp:
        nonlocal runtime, streaming_methods, sync_methods
        if runtime is None:
            from app.agent import app as adk_app

            runtime = AdkApp(
                app=adk_app,
                session_service_builder=services.get_session_service,
                artifact_service_builder=services.get_artifact_service,
                instrumentor_builder=_no_op_instrumentor_builder,
            )
            runtime.set_up()
            operations = runtime.register_operations()
            streaming_methods = set(operations.get("stream", [])) | set(
                operations.get("async_stream", [])
            )
            sync_methods = set(operations.get("", [])) | set(
                operations.get("async", [])
            )
        return runtime

    def resolve_method(class_method: str, *, streaming: bool):
        rt = get_runtime()
        allowed = streaming_methods if streaming else sync_methods
        if class_method not in allowed:
            raise HTTPException(
                status_code=404,
                detail=f"Unsupported reasoning_engine method: {class_method!r}",
            )
        return getattr(rt, class_method)

    def _normalize_input_for_method(
        method_name: str, method: Any, raw_input: Any
    ) -> dict[str, Any]:
        """Normalizes raw request input according to the target method's expected signature."""
        if method_name == "streaming_agent_run_with_events":
            req_dict: dict[str, Any] = {}
            if isinstance(raw_input, dict):
                if "request_json" in raw_input and isinstance(
                    raw_input["request_json"], str
                ):
                    try:
                        req_dict = json.loads(raw_input["request_json"])
                    except Exception:
                        req_dict = {"message": raw_input["request_json"]}
                else:
                    req_dict = dict(raw_input)
            elif isinstance(raw_input, str):
                try:
                    req_dict = json.loads(raw_input)
                except Exception:
                    req_dict = {"message": raw_input}

            msg = req_dict.get("message")
            if msg is None and "input" in req_dict:
                msg = req_dict.pop("input")

            if isinstance(msg, str):
                req_dict["message"] = {
                    "role": "user",
                    "parts": [{"text": msg}],
                }
            elif isinstance(msg, dict):
                if "parts" not in msg:
                    txt = msg.get("text", "")
                    req_dict["message"] = {
                        "role": msg.get("role", "user"),
                        "parts": [{"text": txt}],
                    }
            elif msg is None:
                req_dict["message"] = {
                    "role": "user",
                    "parts": [{"text": ""}],
                }

            if "user_id" not in req_dict:
                req_dict["user_id"] = "default_user"

            return {"request_json": json.dumps(req_dict)}

        if isinstance(raw_input, dict):
            kwargs = dict(raw_input)
            if "message" not in kwargs and "input" in kwargs:
                kwargs["message"] = kwargs.pop("input")
        elif isinstance(raw_input, str):
            kwargs = {"message": raw_input}
        else:
            kwargs = {}

        try:
            sig = inspect.signature(method)
            has_var_keyword = any(
                p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
            )
            if "user_id" in sig.parameters and "user_id" not in kwargs:
                kwargs["user_id"] = "default_user"
            if not has_var_keyword:
                kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        except Exception:
            kwargs.setdefault("user_id", "default_user")

        return kwargs

    @app.post("/api/stream_reasoning_engine")
    async def stream_query(request: Request) -> responses.StreamingResponse:
        body = await request.json()
        class_method = body.get("class_method") or "async_stream_query"
        raw_input = body.get("input") or {}

        method = resolve_method(class_method, streaming=True)
        kwargs = _normalize_input_for_method(class_method, method, raw_input)

        stream = (
            await method(**kwargs)
            if inspect.iscoroutinefunction(method)
            else method(**kwargs)
        )

        async def generator():
            if hasattr(stream, "__aiter__"):
                async for event in stream:
                    yield json.dumps(encoders.jsonable_encoder(event)) + "\n"
            else:
                async for event in iterate_in_threadpool(stream):
                    yield json.dumps(encoders.jsonable_encoder(event)) + "\n"

        return responses.StreamingResponse(
            content=generator(), media_type="application/json"
        )

    @app.post("/api/reasoning_engine")
    async def query(request: Request) -> responses.JSONResponse:
        body = await request.json()
        class_method = body.get("class_method")
        raw_input = body.get("input") or {}

        rt = get_runtime()
        if class_method and class_method in sync_methods:
            method = getattr(rt, class_method)
            kwargs = _normalize_input_for_method(class_method, method, raw_input)
            if inspect.iscoroutinefunction(method):
                output = await method(**kwargs)
            else:
                output = await run_in_threadpool(method, **kwargs)
        else:
            method = rt.async_stream_query
            kwargs = _normalize_input_for_method(
                "async_stream_query", method, raw_input
            )
            events = []
            async for event in rt.async_stream_query(**kwargs):
                events.append(event)
            output = events

        return responses.JSONResponse(
            content=encoders.jsonable_encoder({"output": output})
        )
