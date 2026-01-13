import pytest

from reskyblock import Client


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.mark.asyncio
async def test_client() -> None:
    _ = Client()


@pytest.mark.asyncio
async def test_get_auctions(client: Client) -> None:
    auctions = await client.get_auctions()
    assert auctions.success
    assert auctions.auctions


@pytest.mark.asyncio
async def test_get_auctions_ended(client: Client) -> None:
    ended_auctions = await client.get_auctions_ended()
    assert ended_auctions.success
    assert ended_auctions.auctions


@pytest.mark.asyncio
async def test_get_bazaar(client: Client) -> None:
    bazaar = await client.get_bazaar()
    assert bazaar.success
    assert bazaar.products


@pytest.mark.asyncio
async def test_get_all_auctions(client: Client) -> None:
    auctions = await client.get_all_auctions(max_pages=1)
    assert len(auctions.auctions) == 2000
    assert auctions.received_at > 0
