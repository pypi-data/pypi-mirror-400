import msgspec

__all__ = (
    "Bazaar",
    "Product",
    "QuickStatus",
    "Summary",
)


class Summary(msgspec.Struct, rename="camel"):
    amount: int
    price_per_unit: float
    orders: int


class QuickStatus(msgspec.Struct, rename="camel"):
    product_id: str
    sell_price: float
    sell_volume: int
    sell_moving_week: int
    sell_orders: int
    buy_price: float
    buy_volume: int
    buy_moving_week: int
    buy_orders: int


class Product(msgspec.Struct):
    product_id: str
    sell_summary: list[Summary]
    buy_summary: list[Summary]
    quick_status: QuickStatus


class Bazaar(msgspec.Struct, rename="camel"):
    success: bool
    last_updated: int
    products: dict[str, Product]
    received_at: float = 0
