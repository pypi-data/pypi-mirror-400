import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Awaitable, Callable
from functools import partial

from httpx import HTTPStatusError

from reskyblock.http import AbstractAsyncHTTPClient, HTTPXAsyncClient
from reskyblock.models import (
    AllAuctions,
    Auction,
    Auctions,
    AuctionsEnded,
    Bazaar,
    EndedAuction,
    Product,
    QuickStatus,
    Summary,
)
from reskyblock.nbt import DecodedNBT
from reskyblock.serialization import AbstractJSONDecoder, MSGSpecDecoder
from reskyblock.urls import _prepare_auctions_ended_url, _prepare_auctions_url, _prepare_bazaar_url

type APIEndpoint = Auctions | AuctionsEnded | Bazaar | AllAuctions
type APIEndpointGetter = Callable[[], Awaitable[APIEndpoint]]

__all__ = ("Client", "MockClient", "AbstractClient")


class AbstractClient(ABC):
    @abstractmethod
    async def get_auctions(self, page: int = 0) -> Auctions:
        pass

    @abstractmethod
    async def get_auctions_ended(self) -> AuctionsEnded:
        pass

    @abstractmethod
    async def get_bazaar(self) -> Bazaar:
        pass

    @abstractmethod
    async def get_all_auctions(self, max_pages: int = 100) -> AllAuctions:
        pass

    @abstractmethod
    async def get_auctions_continuous(self) -> AsyncIterator[Auctions]:
        pass

    @abstractmethod
    async def get_auctions_ended_continuous(self) -> AsyncIterator[AuctionsEnded]:
        pass

    @abstractmethod
    async def get_bazaar_continuous(self) -> AsyncIterator[Bazaar]:
        pass

    @abstractmethod
    async def get_all_auctions_continuous(self, max_pages: int = 100) -> AsyncIterator[AllAuctions]:
        pass


class Client(AbstractClient):
    def __init__(self) -> None:
        self._http_client: AbstractAsyncHTTPClient = HTTPXAsyncClient()
        self._json_decoder: AbstractJSONDecoder = MSGSpecDecoder()
        self._auctions_last_updated: int = 0
        self._auctions_ended_last_updated: int = 0
        self._bazaar_last_updated: int = 0

    async def get_auctions(self, page: int = 0) -> Auctions:
        """Get a single page of active auctions"""
        resp_bytes = await self._http_client.get(url=_prepare_auctions_url(page))
        auctions: Auctions = self._json_decoder.serialize(resp_bytes, Auctions)
        auctions.received_at = time.time() * 1000
        self._auctions_last_updated = auctions.last_updated
        return auctions

    async def get_auctions_ended(self) -> AuctionsEnded:
        """Get ended auctions"""
        resp_bytes = await self._http_client.get(url=_prepare_auctions_ended_url())
        auctions_ended: AuctionsEnded = self._json_decoder.serialize(resp_bytes, AuctionsEnded)
        auctions_ended.received_at = time.time() * 1000
        self._auctions_ended_last_updated = auctions_ended.last_updated
        return auctions_ended

    async def get_bazaar(self) -> Bazaar:
        """Get bazaar endpoint"""
        resp_bytes = await self._http_client.get(url=_prepare_bazaar_url())
        bazaar: Bazaar = self._json_decoder.serialize(resp_bytes, Bazaar)
        bazaar.received_at = time.time() * 1000
        self._bazaar_last_updated = bazaar.last_updated
        return bazaar

    async def get_all_auctions(self, max_pages: int = 100) -> AllAuctions:
        """Get auctions from all pages"""
        auctions = []
        page = 0
        last_updated = 0
        while page <= max_pages:
            try:
                auctions_page = await self.get_auctions(page)
                auctions.extend(auctions_page.auctions)
                last_updated = auctions_page.last_updated
                page += 1
            except HTTPStatusError:
                break
        return AllAuctions(last_updated, auctions, time.time() * 1000)

    @staticmethod
    async def _get_continuous[T: APIEndpoint](
        getter: APIEndpointGetter, expected_update_interval: float, update_getter: APIEndpointGetter | None = None
    ) -> AsyncIterator[T]:
        use_update_getter_for_return = update_getter is None
        if update_getter is None:
            update_getter = getter

        last_updated = 0
        while 1:
            next_update = last_updated / 1000 + expected_update_interval
            if next_update > time.time():  # the next update is in the future
                sleep_for = next_update - time.time()
                await asyncio.sleep(max(sleep_for, 0.1))
            try:
                update_api_endpoint = await update_getter()
            except Exception as e:
                logging.exception(e)
                continue

            if update_api_endpoint.last_updated == last_updated:
                continue  # the API has not updated yet

            last_updated = update_api_endpoint.last_updated
            if use_update_getter_for_return:
                api_endpoint = update_api_endpoint
            else:
                try:
                    api_endpoint = await getter()
                except Exception as e:
                    logging.exception(e)
                    continue
            yield api_endpoint

    async def get_auctions_continuous(self) -> AsyncIterator[Auctions]:
        return self._get_continuous(self.get_auctions, 66.5)

    async def get_auctions_ended_continuous(self) -> AsyncIterator[AuctionsEnded]:
        return self._get_continuous(self.get_auctions_ended, 60)

    async def get_bazaar_continuous(self) -> AsyncIterator[Bazaar]:
        return self._get_continuous(self.get_bazaar, 20)

    async def get_all_auctions_continuous(self, max_pages: int = 100) -> AsyncIterator[AllAuctions]:
        return self._get_continuous(partial(self.get_all_auctions, max_pages), 66.5, self.get_auctions)


class MockClient(AbstractClient):
    """This is mock client intended for the users of the library to test code that relies on
    the reskyblock client.

    The getters return a minimal complete representation of each API page. The continuous producers
    yield only a single item.
    """

    async def get_auctions(self, page: int = 0) -> Auctions:
        return Auctions(
            success=True,
            page=0,
            total_pages=1,
            total_auctions=1,
            last_updated=0,
            auctions=[
                Auction(
                    start=0,
                    end=0,
                    item_name="mock item",
                    extra="",
                    category="",
                    tier="",
                    starting_bid=1,
                    item_bytes="",
                    claimed=False,
                    highest_bid_amount=0,
                    last_updated=0,
                    bin=True,
                    uuid="",
                    auctioneer="",
                    profile_id="",
                    decoded_nbt=DecodedNBT(
                        raw_data="",
                        skyblock_id="MOCK_ITEM",
                    ),
                    command="",
                )
            ],
        )

    async def get_auctions_ended(self) -> AuctionsEnded:
        return AuctionsEnded(
            success=True,
            last_updated=0,
            auctions=[
                EndedAuction(
                    auction_id="",
                    seller="",
                    seller_profile="",
                    buyer="",
                    timestamp=0,
                    price=1,
                    bin=True,
                    item_bytes="",
                    decoded_nbt=DecodedNBT(
                        raw_data="",
                        skyblock_id="MOCK_ITEM",
                    ),
                )
            ],
        )

    async def get_bazaar(self) -> Bazaar:
        return Bazaar(
            success=True,
            last_updated=0,
            products={
                "MOCK_PRODUCT": Product(
                    product_id="MOCK_PRODUCT",
                    sell_summary=[
                        Summary(
                            amount=1,
                            price_per_unit=1.0,
                            orders=1,
                        )
                    ],
                    buy_summary=[
                        Summary(
                            amount=1,
                            price_per_unit=1.0,
                            orders=1,
                        )
                    ],
                    quick_status=QuickStatus(
                        product_id="MOCK_PRODUCT",
                        sell_price=1.0,
                        sell_volume=0,
                        sell_moving_week=0,
                        sell_orders=0,
                        buy_price=1.0,
                        buy_volume=0,
                        buy_moving_week=0,
                        buy_orders=0,
                    ),
                )
            },
        )

    async def get_all_auctions(self, max_pages: int = 100) -> AllAuctions:
        auctions = await self.get_auctions()
        return AllAuctions(last_updated=0, auctions=auctions.auctions)

    async def get_auctions_continuous(self) -> AsyncIterator[Auctions]:
        return self._iterator_single_item(self.get_auctions)

    async def get_auctions_ended_continuous(self) -> AsyncIterator[AuctionsEnded]:
        return self._iterator_single_item(self.get_auctions_ended)

    async def get_bazaar_continuous(self) -> AsyncIterator[Bazaar]:
        return self._iterator_single_item(self.get_bazaar)

    async def get_all_auctions_continuous(self, max_pages: int = 100) -> AsyncIterator[AllAuctions]:
        return self._iterator_single_item(self.get_all_auctions)

    @staticmethod
    async def _iterator_single_item[T: APIEndpoint](func: APIEndpointGetter) -> AsyncIterator[T]:
        """This is a helper function that creates an async iterator, which produces only one item.
        The produced item is the result of an `APIEndpoint` getter function.
        """
        yield await func()
