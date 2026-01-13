import pytest

from reskyblock import Client, MockClient


@pytest.fixture
def client() -> MockClient:
    return MockClient()


@pytest.mark.asyncio
async def test_client() -> None:
    _ = MockClient()


@pytest.mark.asyncio
async def test_get_auctions(client: Client) -> None:
    auctions = await client.get_auctions()
    assert auctions.auctions[0].decoded_nbt is not None
    assert auctions.auctions[0].decoded_nbt.skyblock_id == "MOCK_ITEM"


@pytest.mark.asyncio
async def test_get_auctions_ended(client: Client) -> None:
    auctions_ended = await client.get_auctions_ended()
    assert auctions_ended.auctions[0].decoded_nbt is not None
    assert auctions_ended.auctions[0].decoded_nbt.skyblock_id == "MOCK_ITEM"


@pytest.mark.asyncio
async def test_get_bazaar(client: Client) -> None:
    assert (await client.get_bazaar()).products["MOCK_PRODUCT"].quick_status.sell_price == 1.0


@pytest.mark.asyncio
async def test_continuous_update_auctions(client: Client) -> None:
    async for auctions in await client.get_auctions_continuous():
        assert len(auctions.auctions) == 1
    assert True


@pytest.mark.asyncio
async def test_continuous_update_auctions_ended(client: Client) -> None:
    async for ended_auctions in await client.get_auctions_ended_continuous():
        assert len(ended_auctions.auctions) == 1
    assert True


@pytest.mark.asyncio
async def test_continuous_update_bazaar(client: Client) -> None:
    async for bazaar in await client.get_bazaar_continuous():
        assert len(bazaar.products) == 1
    assert True


@pytest.mark.asyncio
async def test_get_all_auctions(client: Client) -> None:
    auctions = await client.get_all_auctions()
    assert len(auctions.auctions) == 1


@pytest.mark.asyncio
async def test_get_all_auctions_continuous(client: Client) -> None:
    n_iter = 0
    async for all_auctions in await client.get_all_auctions_continuous():
        n_iter += 1
        assert len(all_auctions.auctions) == 1
    assert n_iter == 1
