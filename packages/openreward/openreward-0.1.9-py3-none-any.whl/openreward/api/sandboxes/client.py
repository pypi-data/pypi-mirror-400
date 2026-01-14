import asyncio
import base64
from pathlib import Path
from typing import Tuple

import aiohttp
from openreward.api.sandboxes.http import request_retryable, resumable_sse
from openreward.api.sandboxes.ping import ErrorResponse, get_ping_manager
from openreward.api.sandboxes.types import PodTerminatedError, SandboxSettings


def _decode_output(output: str) -> str:
    """Output from the terminal is base64 encoded, as it can arbitrary binary data."""
    return base64.b64decode(output.encode('utf-8')).decode('utf-8', 'surrogateescape').rstrip()

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

class SandboxesAPI:
    def __init__(self,
        base_url: str,
        api_key: str,
        settings: SandboxSettings,
        creation_timeout: int = 60*30,
        # session_headers = None,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.settings = settings
        self.creation_timeout = creation_timeout
        
        # TODO: maybe use shared client session for all sandboxes?
        self.connector = aiohttp.TCPConnector(limit=1_000_000)
        # self.client = aiohttp.ClientSession(base_url=base_url, connector=self.connector, headers=self.session_headers)
        self.client = aiohttp.ClientSession(base_url=base_url, connector=self.connector)
        self.client_id = None

        self._ping_manager = get_ping_manager()
        self._ping_id = id(self)  # Unique ID for this sandbox
        self._dead = asyncio.Event()
        self._dead_exception: BaseException | None = None

    def _ensure_alive(self):
        if self._dead_exception is not None:
            raise self._dead_exception

    def _mark_dead(self, exc: ErrorResponse):
        if self._dead_exception is None:
            self._dead_exception = PodTerminatedError(exc.message, client_id=self.client_id)
            self._dead.set()

    async def run(
        self,
        cmd: str,
        timeout: float | None = 300,
        max_bytes: int | None = 10_000_000, # 10mb
    ) -> Tuple[str, int]:
        """Run a command in the container."""
        self._ensure_alive()

        run_task = asyncio.create_task(resumable_sse(
            self.client,
            "/run",
            token=self.api_key,
            json={
                "cmd": cmd,
                "timeout_s": timeout,
                "max_bytes": max_bytes,
                "shell": "/bin/bash",
            },
            client_id=self.client_id,
            max_retries=5,
        ))
        dead_task = asyncio.create_task(self._dead.wait())

        done, pending = await asyncio.wait(
            [run_task, dead_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if dead_task in done:
            run_task.cancel()
            try:
                await run_task
            except asyncio.CancelledError:
                pass
            raise self._dead_exception or PodTerminatedError("Pod died", client_id=self.client_id)

        dead_task.cancel()
        try:
            res = await run_task
        finally:
            try:
                await dead_task
            except asyncio.CancelledError:
                pass

        return_code = res["return_code"]
        output = _decode_output(res["output"])
        return output, return_code

    async def check_run(
        self,
        cmd: str,
        timeout: float | None = 300,
        max_bytes: int | None = 10_000_000, # 10mb
    ) -> str:
        """Run a command in the container and raise an error if it fails."""
        self._ensure_alive()
        output, exit_code = await self.run(cmd, timeout=timeout, max_bytes=max_bytes)
        if exit_code != 0:
            raise RuntimeError(f"Command failed: {cmd}\n{output}")
        return output

    # TODO: nicer upload and download methods on the sandbox server
    async def upload(self, local_path: str | Path, container_path: str) -> None:
        """Upload a single file from local filesystem to the container."""
        self._ensure_alive()
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        max_size = 10 * 1024 * 1024 # make sure the file is not too large (10mb)
        if local_path.stat().st_size > max_size:
            raise ValueError(f"File is too large: {local_path.stat().st_size} bytes > {max_size} bytes")

        file_content = local_path.read_bytes()
        encoded_content = base64.b64encode(file_content).decode('ascii')

        cmd = f"echo '{encoded_content}' | base64 -d > {container_path}"
        await self.check_run(cmd, max_bytes=max_size)


    async def download(self, container_path: str) -> bytes:
        """Download a single file from the container."""
        self._ensure_alive()
        cmd = f"base64 {container_path}"
        output = await self.check_run(cmd, max_bytes=None)

        try:
            file_content = base64.b64decode(output.encode('ascii'))
            return file_content
        except Exception as e:
            raise RuntimeError(f"Failed to decode and write file: {e}")

    async def start(self) -> None:
        # get client id
        res = await resumable_sse(
            self.client,
            "/create",
            token=self.api_key,
            json={
                "creation_request": self.settings.model_dump(),
            },
            max_retries=3,
            timeout=self.creation_timeout,
        )
        self.client_id = res["client_id"]

        # Register with ping manager
        await self._ping_manager.start_ping(
            task_id=str(self._ping_id),
            url=f"{self.base_url}/ping",
            client_id=self.client_id,
            api_key=self.api_key,
            sleep_time=10,
            on_error=self._mark_dead,
        )

    async def stop(self) -> None:
        # stop ping
        try:
            await self._ping_manager.stop_ping(str(self._ping_id))
        except:
            pass

        # delete pod
        try:
            await request_retryable(
                self.client,
                "POST",
                "/delete",
                expect_json=True,
                token=self.api_key,
                client_id=self.client_id,
            )
        except:
            pass
        # close client
        if not self.client.closed:
            await self.client.close()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *_):
        await self.stop()


    def __del__(self):
        _finalize_session(self.client)