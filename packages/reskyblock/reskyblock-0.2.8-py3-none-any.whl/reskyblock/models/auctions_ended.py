import msgspec

from reskyblock.nbt import DecodedNBT

__all__ = (
    "AuctionsEnded",
    "EndedAuction",
)


class EndedAuction(msgspec.Struct):
    """Represent an instance of an auction that has ended"""

    auction_id: str
    seller: str
    seller_profile: str
    buyer: str
    timestamp: int
    price: int
    bin: bool
    item_bytes: str
    decoded_nbt: DecodedNBT | None = None

    def __post_init__(self) -> None:
        if self.decoded_nbt is None:
            self.decoded_nbt = DecodedNBT(raw_data=self.item_bytes)


class AuctionsEnded(msgspec.Struct, rename="camel"):
    success: bool
    last_updated: int
    auctions: list[EndedAuction]
    received_at: float = 0
