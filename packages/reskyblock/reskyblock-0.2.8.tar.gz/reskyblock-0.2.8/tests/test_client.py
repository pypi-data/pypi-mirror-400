import json
import pathlib

import pytest
from pytest_httpx import HTTPXMock

from reskyblock import Client

_AUCTIONS_DATA = (pathlib.Path(__file__).resolve().parents[0] / "data" / "auctions.json").read_text(encoding="utf-8")
_AUCTIONS_DATA2 = (pathlib.Path(__file__).resolve().parents[0] / "data" / "auctions2.json").read_text(encoding="utf-8")

_AUCTIONS_ENDED_DATA = (pathlib.Path(__file__).resolve().parents[0] / "data" / "auctions_ended.json").read_text(
    encoding="utf-8"
)
_BAZAAR_DATA = (pathlib.Path(__file__).resolve().parents[0] / "data" / "bazaar.json").read_text(encoding="utf-8")


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.mark.asyncio
async def test_client() -> None:
    _ = Client()


@pytest.mark.asyncio
async def test_get_auctions(httpx_mock: HTTPXMock, client: Client) -> None:
    httpx_mock.add_response(json=json.loads(_AUCTIONS_DATA))
    await client.get_auctions()


@pytest.mark.asyncio
async def test_get_auctions_ended(httpx_mock: HTTPXMock, client: Client) -> None:
    httpx_mock.add_response(json=json.loads(_AUCTIONS_ENDED_DATA))

    await client.get_auctions_ended()


@pytest.mark.asyncio
async def test_get_bazaar(httpx_mock: HTTPXMock, client: Client) -> None:
    httpx_mock.add_response(json=json.loads(_BAZAAR_DATA))

    await client.get_bazaar()


@pytest.mark.asyncio
async def test_continuous_update_auctions(httpx_mock: HTTPXMock, client: Client) -> None:
    httpx_mock.add_response(json=json.loads(_AUCTIONS_DATA))

    async for auction in await client.get_auctions_continuous():
        assert len(auction.auctions) == 1000
        assert auction.received_at > 0
        break


@pytest.mark.asyncio
async def test_continuous_update_auctions_ended(httpx_mock: HTTPXMock, client: Client) -> None:
    httpx_mock.add_response(json=json.loads(_AUCTIONS_ENDED_DATA))

    async for _ in await client.get_auctions_ended_continuous():
        break


@pytest.mark.asyncio
async def test_continuous_update_bazaar(httpx_mock: HTTPXMock, client: Client) -> None:
    httpx_mock.add_response(json=json.loads(_BAZAAR_DATA))

    async for _ in await client.get_bazaar_continuous():
        break


@pytest.mark.asyncio
async def test_get_all_auctions(httpx_mock: HTTPXMock, client: Client) -> None:
    httpx_mock.add_response(url="https://api.hypixel.net/v2/skyblock/auctions?page=0", json=json.loads(_AUCTIONS_DATA))
    httpx_mock.add_response(url="https://api.hypixel.net/v2/skyblock/auctions?page=1", json=json.loads(_AUCTIONS_DATA2))
    httpx_mock.add_response(url="https://api.hypixel.net/v2/skyblock/auctions?page=2", status_code=404)

    auctions = await client.get_all_auctions()
    assert len(auctions.auctions) == 2000
    assert auctions.received_at > 0


@pytest.mark.asyncio
async def test_get_all_auctions_continuous(httpx_mock: HTTPXMock, client: Client) -> None:
    httpx_mock.add_response(url="https://api.hypixel.net/v2/skyblock/auctions?page=0", json=json.loads(_AUCTIONS_DATA))
    httpx_mock.add_response(url="https://api.hypixel.net/v2/skyblock/auctions?page=0", json=json.loads(_AUCTIONS_DATA))
    httpx_mock.add_response(url="https://api.hypixel.net/v2/skyblock/auctions?page=1", json=json.loads(_AUCTIONS_DATA2))
    httpx_mock.add_response(url="https://api.hypixel.net/v2/skyblock/auctions?page=2", status_code=404)
    async for _ in await client.get_all_auctions_continuous():
        break
