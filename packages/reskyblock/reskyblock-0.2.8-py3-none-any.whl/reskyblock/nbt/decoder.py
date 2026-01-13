"""NBT (Named Binary Tag) protocol decoder
This relies on the https://pypi.org/project/NBT/ library.
"""

import base64
import gzip
import json as dum_json

import nbt2dict
from msgspec import Struct

__all__ = ("DecodedNBT",)


def _decode_nbt(nbt_data) -> dict:
    nbt_data = base64.b64decode(nbt_data)
    nbt_data = gzip.decompress(nbt_data)

    return nbt2dict.parse_nbt(nbt_data)["i"][0]


class DecodedNBT(Struct):
    """Decoded NBT item data"""

    raw_data: str
    is_pet: bool = False
    skyblock_id: str = ""
    reforge: str | None = None
    dungeon_stars: int = 0
    hot_potato_count: int = 0
    rarity_upgrades: int = 0
    art_of_war_count: int = 0
    gems: list[str] | None = []
    scrolls: list[str] | None = []
    enchantments: list[str] | None = []

    def __post_init__(self) -> None:
        if self.raw_data == "":
            return
        nbt_data = _decode_nbt(self.raw_data)
        ea = nbt_data["tag"]["ExtraAttributes"]

        self.skyblock_id = str(ea["id"]).replace("STARRED_", "")
        self.reforge = ea.get("modifier")
        self.dungeon_stars = ea.get("dungeon_item_level") or ea.get("upgrade_level") or 0
        self.hot_potato_count = ea.get("hot_potato_count", 0)
        self.rarity_upgrades = ea.get("rarity_upgrades", 0)
        self.art_of_war_count = int(ea.get("art_of_war_count", 0))
        self.gems = ea.get("gems", [])
        self.scrolls = ea.get("ability_scroll", [])

        self.enchantments = [
            "ENCHANTMENT_" + keyval[0].upper() + "_" + str(keyval[1]) for keyval in ea.get("enchantments", {}).items()
        ]

        if self.skyblock_id == "PET":
            self.is_pet = True
            pet_info = dum_json.loads(ea["petInfo"])
            pet_type = pet_info["type"]
            self.skyblock_id = f"{pet_type}_PET"
