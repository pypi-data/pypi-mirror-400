import asyncio
import time

from httpx import AsyncClient
from httpx_sse import aconnect_sse
from pydantic import TypeAdapter

from progtc.types import (
    ExecuteCodeError,
    ExecuteCodeMessage,
    ExecuteCodeSuccess,
    ToolCall,
    ToolHandler,
)

ExecuteCodeMessageAdapter = TypeAdapter[ExecuteCodeMessage](ExecuteCodeMessage)


class AsyncProgtcClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        headers: dict[str, str] | None = None,
    ):
        self._base_url = base_url
        self._api_key = api_key
        self._headers = headers or {}

    async def ping(self, headers: dict[str, str] | None = None) -> bool:
        merged_headers = {**self._headers, **(headers or {})}
        async with AsyncClient(
            base_url=self._base_url, headers=merged_headers
        ) as client:
            try:
                response = await client.get("/ping")
                return response.status_code == 200
            except Exception:
                return False

    async def wait_for_server(
        self, timeout: float = 10.0, headers: dict[str, str] | None = None
    ) -> None:
        t0 = time.monotonic()
        while not await self.ping(headers=headers):
            await asyncio.sleep(0.5)
            if time.monotonic() - t0 > timeout:
                raise TimeoutError(f"Progtc server not ready after {timeout}s")

    async def execute_code(
        self,
        code: str,
        tools: dict[str, ToolHandler],
        headers: dict[str, str] | None = None,
    ) -> ExecuteCodeSuccess | ExecuteCodeError:
        merged_headers = {
            **self._headers,
            **(headers or {}),
            "X-Progtc-API-Key": self._api_key,
        }
        async with (
            AsyncClient(
                base_url=self._base_url,
                headers=merged_headers,
            ) as client,
            aconnect_sse(
                client,
                "POST",
                "/execute-code",
                json={
                    "tool_names": list(tools.keys()),
                    "code": code,
                },
            ) as event_source,
        ):
            async for event in event_source.aiter_sse():
                event_obj = ExecuteCodeMessageAdapter.validate_python(event.json())
                if isinstance(event_obj, ToolCall):
                    handler = tools[event_obj.tool_name]
                    result = await handler(*event_obj.args, **event_obj.kwargs)
                    await client.post(
                        "/tool-results",
                        json={
                            "execution_id": event_obj.execution_id,
                            "tool_call_id": event_obj.id,
                            "result": result,
                        },
                    )
                else:
                    return event_obj

        raise RuntimeError("Stream ended without result")
