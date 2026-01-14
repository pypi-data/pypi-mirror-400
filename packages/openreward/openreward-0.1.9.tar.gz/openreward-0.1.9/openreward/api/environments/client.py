import asyncio
import base64
import os
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Coroutine, overload

import aiohttp
from .http import request_retryable, resumable_sse
from .ping import ErrorResponse, PingManager
from .types import (
    ImageBlock,
    JSONObject,
    JSONValue,
    Provider,
    Server,
    Task,
    TextBlock,
    ToolCallError,
    ToolOutput,
    ToolSpec,
    Literal,
    Mapping,
)


def _strip_titles(value: Any) -> Any:
    """Recursively remove JSON schema `title` keys."""
    if isinstance(value, dict):
        return {
            k: _strip_titles(v)
            for k, v in value.items()
            if k != "title"
        }
    if isinstance(value, list):
        return [_strip_titles(item) for item in value]
    return value

@overload
def convert_tool_response(res: Mapping[str, Any], format: None = None) -> list[ToolSpec]: ...

@overload
def convert_tool_response(res: Mapping[str, Any], format: Provider = ...) -> list[dict[str, Any]]: ...

def convert_tool_response(
    res: Mapping[str, Any],
    format: Provider | None = None,
) -> list[ToolSpec] | list[dict[str, Any]]:
    if format is not None:
        if format == "openai":
            return [
                {
                    "type": "function",
                    **{
                        k: _strip_titles(v)
                        for k, v in tool.items()
                        if k not in {"input_schema", "title"}
                    },
                    "parameters": _strip_titles(tool["input_schema"]) if tool.get("input_schema") else None
                }
                for tool in res["tools"]
            ]
        elif format == "openrouter":
            return [
                {
                    "type": "function",
                    "function": {
                        k: _strip_titles(v)
                        for k, v in tool.items()
                        if k not in {"input_schema", "title"}
                    },
                    "parameters": _strip_titles(tool["input_schema"]) if tool.get("input_schema") else None
                }
                for tool in res["tools"]
            ]
        elif format == "anthropic":
            return [
                {
                    "type": "custom",
                    **{
                        k: _strip_titles(v)
                        for k, v in tool.items()
                        if k not in {"input_schema", "title"}
                    },
                    "input_schema": _strip_titles(tool["input_schema"]) if tool.get("input_schema") else None
                }
                for tool in res["tools"]
            ]
        elif format == "google":
            return [
                {
                    **{
                        k: _strip_titles(v)
                        for k, v in tool.items()
                        if k not in {"input_schema", "title"}
                    },
                    "parameters": _strip_titles(tool["input_schema"]) if tool.get("input_schema") else None
                }
                for tool in res["tools"]
            ]
        else:
            raise ValueError(f"Invalid format: {format!r}")

    return [ToolSpec(**tool) for tool in res["tools"]]

@asynccontextmanager
async def matrix_sid_provider(client: aiohttp.ClientSession, server_name: str, token: str | None) -> AsyncGenerator[str, None]:
    sid = await request_retryable(client, "POST", "/create_session", expect_json=True, deployment=server_name, token=token)
    try:
        yield sid["sid"]
    finally:
        await request_retryable(client, "POST", "/delete_session", sid=sid["sid"], expect_json=False, deployment=server_name, token=token)

def _finalize_session(session: aiohttp.ClientSession):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            asyncio.run(session.close())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(session.close())
            loop.close()
    else:
        if not session.closed:
            loop.create_task(session.close())

class SessionTerminatedError(RuntimeError):
    def __init__(self, reason: str, *, sid: str | None):
        super().__init__(f"Session terminated (sid={sid!r}): {reason}")
        self.reason = reason
        self.sid = sid

class Session:
    
    def __init__(
        self, 
        env: "Environment", 
        task: Task, 
        secrets: dict[str, str] | None = None, 
        api_key: str | None = None
    ):
        self.client = env.client
        self.task = task
        self.api_key = api_key
        self.base_url = str(env.client._base_url)
        self._sid_cm = None
        self.sid: str | None = None

        self.secrets = {**(secrets or {}), **{"api_key": api_key}}
        
        self._ping_manager = env.ping_manager
        self._ping_id = uuid.uuid4().hex
        self._dead = asyncio.Event()
        self._dead_exception: SessionTerminatedError | None = None

    def _mark_dead(self, exc: ErrorResponse):
        if self._dead_exception is None:
            self._dead_exception = SessionTerminatedError(exc.message, sid=self.sid)
            self._dead.set()

    async def _run_task(self, coro: Coroutine[Any, Any, Any]):
        """Run a coroutine until completion or until the session dies."""
        if self._dead_exception is not None:
            raise self._dead_exception

        task = asyncio.create_task(coro)
        stopper = asyncio.create_task(self._dead.wait())
        try:
            done, pending = await asyncio.wait(
                {task, stopper},
                return_when=asyncio.FIRST_COMPLETED,
            )

            # If session died first
            if self._dead.is_set() and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                if self._dead_exception:
                    raise self._dead_exception

            return await task  # return result (or raise from task)

        finally:
            stopper.cancel()
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    async def __aenter__(self) -> "Session":
        self._sid_cm = matrix_sid_provider(self.client, self.task.deployment_name, self.api_key)
        self.sid = await self._sid_cm.__aenter__()
        await request_retryable(
            self.client,
            "POST",
            "/create",
            expect_json=True,
            sid=self.sid,
            deployment=self.task.deployment_name,
            json={
                "env_name": self.task.environment_name,
                "task_spec": self.task.task_spec,
                "secrets": self.secrets
            },
            token=self.api_key
        )

        # register with ping manager
        await self._ping_manager.start_ping(
            task_id=str(self._ping_id),
            url=f"{self.base_url}/ping",
            deployment=self.task.deployment_name,
            session_id=self.sid,
            api_key=self.api_key,
            sleep_time=10,
            on_error=self._mark_dead,
        )

        return self

    async def __aexit__(self, *exc):
        try:
            await self._ping_manager.stop_ping(str(self._ping_id))
        except:
            pass
        
        try:
            await request_retryable(
                self.client,
                "POST",
                "/delete",
                expect_json=False,
                sid=self.sid,
                deployment=self.task.deployment_name,
                token=self.api_key
            )
        except:
            pass
        await self._sid_cm.__aexit__(*exc) # type: ignore
        self._sid_cm = None

    async def get_prompt(self) -> list[TextBlock | ImageBlock]:
        res = await self._run_task(
            request_retryable(
                self.client,
                "GET",
                f"/{self.task.environment_name}/prompt",
                expect_json=True,
                sid=self.sid,
                deployment=self.task.deployment_name,
                token=self.api_key,
            )
        )
        blocks: list[TextBlock | ImageBlock] = []
        for block in res:
            if block["type"] == "text":
                blocks.append(TextBlock(text=block["text"], detail=block["detail"]))
            elif block["type"] == "image":
                blocks.append(ImageBlock(mimeType=block["mimeType"], detail=block["detail"], data=block["data"]))
        return blocks

    @overload
    async def list_tools(self, format: None = None) -> list[ToolSpec]: ...

    @overload
    async def list_tools(self, format: Provider) -> list[dict]: ...

    async def list_tools(self, format: Provider | None = None) -> list[ToolSpec] | list[dict]:
        res = await self._run_task(
            request_retryable(
                self.client,
                "GET",
                f"/{self.task.environment_name}/tools",
                expect_json=True,
                sid=self.sid,
                deployment=self.task.deployment_name,
                token=self.api_key,
            )
        )
        return convert_tool_response(res, format=format)

    async def call_tool(self, tool_name: str, input: JSONObject = {}) -> ToolOutput:
        if not isinstance(input, Mapping):
            raise ToolCallError(f"Tool input must be a dictionary, got {type(input).__name__}")

        if not all(isinstance(k, str) for k in input.keys()):
            non_string_keys = [k for k in input.keys() if not isinstance(k, str)]
            raise ToolCallError(f"All keys in tool input must be strings. Found non-string keys: {non_string_keys}")

        res = await self._run_task(
            resumable_sse(
                self.client,
                f"/{self.task.environment_name}/call",
                sid=self.sid,
                deployment=self.task.deployment_name,
                token=self.api_key,
                json={"name": tool_name, "input": input},
                max_retries=5,
            )
        )

        if res["ok"]:
            blocks: list[TextBlock | ImageBlock] = []
            for block in res["output"]["blocks"]:
                if block["type"] == "text":
                    blocks.append(TextBlock(
                        text=block["text"],
                        detail=block["detail"]
                    ))
                elif block["type"] == "image":
                    blocks.append(ImageBlock(
                        mimeType=block["mimeType"],
                        detail=block["detail"],
                        data=block["data"]
                    ))
            return ToolOutput(
                blocks=blocks,
                metadata=res["output"]["metadata"],
                reward=res["output"]["reward"],
                finished=res["output"]["finished"]
            )
        else:
            raise ToolCallError(res["error"])
        
class Environment:

    def __init__(
        self,
        namespace: str | None,
        name: str,
        variant: str | None,
        client: aiohttp.ClientSession,
        api_key: str | None,
        ping_manager: PingManager
    ) -> None:

        self.server = name
        self.namespace = namespace
        self.name = name
        self.variant = variant
        self.client = client
        self.api_key = api_key
        self.ping_manager = ping_manager

    @property
    def deployment_name(self) -> str:
        if self.namespace is None:
            return self.name
        else:
            return f"{self.namespace}/{self.name}"
        
    async def list_splits(self) -> list[str]:
        async with matrix_sid_provider(self.client, self.deployment_name, self.api_key) as sid:
            path = "/splits" if self.variant is None else f"/{self.variant}/splits"
            res = await request_retryable(self.client, "GET", path, expect_json=True, sid=sid, deployment=self.deployment_name, token=self.api_key)
            return res

    async def list_tasks(self, split: str) -> list[Task]:
        async with matrix_sid_provider(self.client, self.deployment_name, self.api_key) as sid:
            path = "/tasks" if self.variant is None else f"/{self.variant}/tasks"
            res = await request_retryable(self.client, "POST", path, expect_json=True, sid=sid, deployment=self.deployment_name, json={"split": split}, token=self.api_key)
            return [Task(server_name=self.server, environment_name=res["env_name"], task_spec=task, namespace=self.namespace) for task in res["tasks"]]
        
    async def list_tools(self, format: Provider | None = None) -> list[ToolSpec] | list[dict]:
        path = "/tools" if self.variant is None else f"/{self.variant}/tools"
        async with matrix_sid_provider(self.client, self.deployment_name, self.api_key) as sid:
            res = await request_retryable(self.client, "GET", path, expect_json=True, sid=sid, deployment=self.deployment_name, token=self.api_key)
            return convert_tool_response(res, format=format)
        
    async def get_prompt(self, task: Task) -> str:
        async with matrix_sid_provider(self.client, task.deployment_name, self.api_key) as sid:
            path = "/prompt" if self.variant is None else f"/{self.variant}/prompt"
            res = await request_retryable(self.client, "GET", path, expect_json=True, sid=sid, deployment=task.deployment_name, token=self.api_key)
            return res
        
    def session(self, task: Task, secrets: dict[str, str] | None = None) -> Session:
        return Session(self, task, secrets, self.api_key)

class EnvironmentsAPI:

    def __init__(
        self,
        base_url: str,
        api_key: str
    ):
        self.api_key = api_key
        self.ping_manager = PingManager()

        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=None)
        self.connector = aiohttp.TCPConnector(limit=1_000_000)

        self._clients: dict[str, aiohttp.ClientSession] = {}

    def get(self, name: str, variant: str | None = None, base_url: str | None = None) -> Environment:

        parts = name.split("/", maxsplit=1)
        namespace = None
        if len(parts) == 1:
            env_name = parts[0]
        elif len(parts) == 2:
            namespace, env_name = parts
            pass
        else:
            raise RuntimeError("impossible")


        if namespace and self.api_key is None:
            raise ValueError(f"Expected api_key to be passed when accessing remote environment")

        if base_url is None:
            base_url = self.base_url

        if base_url not in self._clients:
            self._clients[base_url] = aiohttp.ClientSession(base_url=base_url, timeout=self.timeout, connector=self.connector)
        client = self._clients[base_url]

        return Environment(
            namespace=namespace,
            name=env_name,
            variant=variant,
            client=client,
            api_key=self.api_key,
            ping_manager=self.ping_manager
        )

    def __del__(self):
        for client in self._clients.values():
            _finalize_session(client)
        self.ping_manager.shutdown()