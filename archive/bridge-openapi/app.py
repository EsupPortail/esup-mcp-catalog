import json
import logging
import os
import re
from copy import deepcopy
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


logger = logging.getLogger("mcp_bridge")

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def require_api_key(api_key: str | None = Security(api_key_header)) -> None:
    expected_key = os.environ.get("BRIDGE_API_KEY")
    if not expected_key:
        raise RuntimeError("BRIDGE_API_KEY is not configured")
    if api_key != f"Bearer {expected_key}":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bridge API key",
        )


def load_server_config() -> dict[str, dict[str, Any]]:
    raw_config = os.environ.get("MCP_SERVERS_JSON", "{}")
    config = json.loads(os.path.expandvars(raw_config))
    if not isinstance(config, dict):
        raise ValueError("MCP_SERVERS_JSON must contain an object")
    return config


def operation_id(server_name: str, tool_name: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_]+", "_", f"{server_name}_{tool_name}")
    return f"mcp_{value.strip('_')}"


class MCPBridge:
    def __init__(self, server_config: dict[str, dict[str, Any]]) -> None:
        self.server_config = server_config
        self.sessions: dict[str, ClientSession] = {}
        self.tools: dict[tuple[str, str], dict[str, Any]] = {}
        self.server_stacks: dict[str, AsyncExitStack] = {}

    async def start(self) -> None:
        for server_name, config in self.server_config.items():
            try:
                await self._start_server(server_name, config)
            except BaseException:
                # A failing streamable-http connection can surface as a
                # BaseExceptionGroup wrapping GeneratorExit during anyio's
                # task-group cleanup, which `except Exception` would miss.
                logger.exception(
                    "Failed to start MCP server %r, skipping it", server_name
                )

    async def _start_server(self, server_name: str, config: dict[str, Any]) -> None:
        if config.get("transport") != "streamable-http":
            raise ValueError(
                f"Server {server_name!r} must use transport streamable-http"
            )
        url = config.get("url")
        if not url:
            raise ValueError(f"Server {server_name!r} has no URL")
        headers = config.get("headers", {})

        stack = AsyncExitStack()
        try:
            http_client = await stack.enter_async_context(
                httpx.AsyncClient(headers=headers)
            )
            transport = await stack.enter_async_context(
                streamable_http_client(url, http_client=http_client)
            )
            read_stream, write_stream, _ = transport
            session = await stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await session.initialize()
            tool_result = await session.list_tools()
        except BaseException:
            await stack.aclose()
            raise

        old_stack = self.server_stacks.pop(server_name, None)
        if old_stack is not None:
            await old_stack.aclose()
        self.server_stacks[server_name] = stack
        self.sessions[server_name] = session
        for tool in tool_result.tools:
            self.tools[(server_name, tool.name)] = {
                "name": tool.name,
                "description": tool.description or "MCP tool",
                "inputSchema": tool.inputSchema or {"type": "object"},
            }

    async def stop(self) -> None:
        for stack in self.server_stacks.values():
            await stack.aclose()

    async def call(
        self, server_name: str, tool_name: str, arguments: dict[str, Any]
    ) -> Any:
        session = self.sessions.get(server_name)
        if session is None or (server_name, tool_name) not in self.tools:
            raise HTTPException(status_code=404, detail="MCP tool not found")
        try:
            result = await session.call_tool(tool_name, arguments=arguments)
        except Exception:
            # The underlying MCP session can go stale (e.g. the target server
            # restarted and no longer recognizes it) well after startup.
            # Reconnect once before giving up on this call.
            logger.warning(
                "Tool call failed on %r, reconnecting and retrying once",
                server_name,
            )
            try:
                await self._start_server(server_name, self.server_config[server_name])
            except BaseException:
                logger.exception("Reconnect failed for %r", server_name)
                raise HTTPException(
                    status_code=502, detail="MCP server unavailable"
                ) from None
            session = self.sessions[server_name]
            result = await session.call_tool(tool_name, arguments=arguments)
        return result.model_dump(mode="json")


bridge: MCPBridge | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global bridge
    bridge = MCPBridge(load_server_config())
    await bridge.start()
    yield
    await bridge.stop()
    bridge = None


app = FastAPI(
    title="MCP OpenAPI Bridge",
    description="Expose configured MCP tools as OpenAPI operations for OpenWebUI.",
    version="0.1.0",
    lifespan=lifespan,
)

# OpenWebUI's admin UI verifies a tool connection from the browser, so the
# spec fetch is cross-origin from wherever OpenWebUI is served. The actual
# tool calls go through OpenWebUI's backend and don't need this, but the
# discovery step does.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/tools/{server_name}/{tool_name}",
    operation_id="call_mcp_tool",
    dependencies=[Depends(require_api_key)],
)
async def call_mcp_tool(
    server_name: str, tool_name: str, request: Request
) -> Any:
    if bridge is None:
        raise HTTPException(status_code=503, detail="Bridge is not ready")
    arguments = await request.json()
    if not isinstance(arguments, dict):
        raise HTTPException(status_code=422, detail="Tool arguments must be an object")
    return await bridge.call(server_name, tool_name, arguments)


@app.get("/tools", include_in_schema=False)
async def list_tools(_: None = Depends(require_api_key)) -> dict[str, Any]:
    if bridge is None:
        raise HTTPException(status_code=503, detail="Bridge is not ready")
    return {
        "tools": [
            {"server": server, **tool}
            for (server, _), tool in bridge.tools.items()
        ]
    }


def build_openapi_schema(server_filter: str | None = None) -> dict[str, Any]:
    from fastapi.openapi.utils import get_openapi

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    paths = schema["paths"]
    generic_operation = paths["/tools/{server_name}/{tool_name}"]["post"]
    items = bridge.tools.items() if bridge else []
    if server_filter is not None:
        items = [
            ((server_name, tool_name), tool)
            for (server_name, tool_name), tool in items
            if server_name == server_filter
        ]
    for (server_name, tool_name), tool in items:
        path = f"/tools/{server_name}/{tool_name}"
        operation = deepcopy(generic_operation)
        operation.pop("parameters", None)
        paths[path] = {"post": operation}
        operation["operationId"] = operation_id(server_name, tool_name)
        operation["summary"] = tool["name"]
        operation["description"] = tool["description"]
        operation["security"] = [{"BearerAuth": []}]
        operation["requestBody"] = {
            "required": False,
            "content": {
                "application/json": {
                    "schema": tool["inputSchema"],
                }
            },
        }
    del paths["/tools/{server_name}/{tool_name}"]
    return schema


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema is None:
        app.openapi_schema = build_openapi_schema()
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/servers/{server_name}/openapi.json", include_in_schema=False)
async def server_openapi(server_name: str) -> dict[str, Any]:
    if bridge is None:
        raise HTTPException(status_code=503, detail="Bridge is not ready")
    if server_name not in bridge.server_config:
        raise HTTPException(status_code=404, detail="Unknown MCP server")
    return build_openapi_schema(server_filter=server_name)
