import pytest
from pytest_httpx import HTTPXMock

from reskyblock.http import HTTPXAsyncClient, HTTPXClient


@pytest.mark.parametrize("params", [None, {"a": "a", "b": "b"}])
def test_httpx_client(httpx_mock: HTTPXMock, params: dict[str, str] | None) -> None:
    httpx_mock.add_response()

    data = HTTPXClient().get("https://test_url", params=params)
    assert data == b""


@pytest.mark.asyncio
@pytest.mark.parametrize("params", [None, {"a": "a", "b": "b"}])
async def test_async_httpx_client(httpx_mock: HTTPXMock, params: dict[str, str] | None) -> None:
    httpx_mock.add_response()

    data = await HTTPXAsyncClient().get("https://test_url", params=params)
    assert data == b""
