import pytest

from reskyblock.urls import _prepare_auctions_ended_url, _prepare_auctions_url, _prepare_bazaar_url


def test__prepare_auctions_ended_url() -> None:
    assert _prepare_auctions_ended_url() == "https://api.hypixel.net/v2/skyblock/auctions_ended"


@pytest.mark.parametrize("page", [0, 1, 100])
def test__prepare_auctions_url(page: int | None) -> None:
    assert _prepare_auctions_url(page) == f"https://api.hypixel.net/v2/skyblock/auctions?page={page}"


def test__prepare_auctions_url_none() -> None:
    assert _prepare_auctions_url() == "https://api.hypixel.net/v2/skyblock/auctions?page=0"


def test__prepare_bazaar_url() -> None:
    assert _prepare_bazaar_url() == "https://api.hypixel.net/v2/skyblock/bazaar"
