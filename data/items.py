"""
RAGNAROK GRIND — Item Database
Data-driven equipment, class restrictions, and Zeny economy.

Architecture:
  CLASS_GROUPS   — named sets of classes (Swordsman Path, etc.)
  ITEM_DB        — full item definitions keyed by item_id
  Lookup helpers — get_item(), items_by_slot(), can_equip()

Future hooks present for: refinement, cards, sockets, enchantments,
stat bonuses, consumables, crafting materials.
"""

from __future__ import annotations


# ─────────────────────────────────────────────────────────────────────────────
#  CLASS GROUP DEFINITIONS
#
#  A "path" is an inherited group: any class in the group (or descended
#  from it) counts as belonging to that path.
#
#  This avoids duplicating restrictions for every subclass.
#  e.g. "Swordsman Path" includes Swordsman, Knight, Crusader,
#       Lord Knight, Paladin, Rune Knight, Royal Guard.
# ─────────────────────────────────────────────────────────────────────────────

# Maps group name → set of all class names that belong to it
CLASS_GROUPS: dict[str, set[str]] = {
    "All": set(),        # sentinel — filled at bottom after CLASS_DB import
    "All Except Novice": set(),

    "Swordsman Path": {
        "Swordsman",
        "Knight",    "Crusader",
        "Lord Knight", "Paladin",
        "Rune Knight", "Royal Guard",
        "High Swordsman",
    },
    "Mage Path": {
        "Mage",
        "Wizard",   "Sage",
        "High Wizard", "Professor",
        "Warlock",  "Sorcerer",
        "High Mage",
    },
    "Archer Path": {
        "Archer",
        "Hunter",   "Bard",    "Dancer",
        "Sniper",   "Clown",   "Gypsy",
        "Ranger",   "Maestro", "Wanderer",
        "High Archer",
    },
    "Acolyte Path": {
        "Acolyte",
        "Priest",  "Monk",
        "High Priest", "Champion",
        "Arch Bishop", "Sura",
        "High Acolyte",
    },
    "Thief Path": {
        "Thief",
        "Assassin",       "Rogue",
        "Assassin Cross", "Stalker",
        "Guillotine Cross", "Shadow Chaser",
        "High Thief",
    },
    "Merchant Path": {
        "Merchant",
        "Blacksmith",  "Alchemist",
        "Whitesmith",  "Biochemist",
        "Mechanic",    "Geneticist",
        "High Merchant",
    },
    "Knight Path": {
        "Knight", "Lord Knight", "Rune Knight",
    },
    "Crusader Path": {
        "Crusader", "Paladin", "Royal Guard",
    },
    "Assassin Path": {
        "Assassin", "Assassin Cross", "Guillotine Cross",
    },
    "Rogue Path": {
        "Rogue", "Stalker", "Shadow Chaser",
    },
}


def _resolve_allowed(groups: list[str]) -> set[str]:
    """
    Expand a list of group names into a flat set of allowed class names.
    Handles 'All' and 'All Except Novice' sentinels lazily so the DB
    import isn't circular.
    """
    result: set[str] = set()
    for g in groups:
        if g in CLASS_GROUPS:
            result |= CLASS_GROUPS[g]
        else:
            # treat as a literal class name
            result.add(g)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  EQUIPMENT SLOTS
# ─────────────────────────────────────────────────────────────────────────────

EQUIPMENT_SLOTS: list[str] = ["weapon", "armor", "shield", "garment", "shoes"]

SLOT_DISPLAY: dict[str, str] = {
    "weapon":  "Weapon",
    "armor":   "Armor",
    "shield":  "Shield",
    "garment": "Garment",
    "shoes":   "Shoes",
}


# ─────────────────────────────────────────────────────────────────────────────
#  ITEM DATABASE
#
#  Each entry:
#    item_id       str   — unique key (snake_case)
#    name          str   — display name
#    category      str   — "weapon" | "armor" | "shield" | "garment" | "shoes"
#    slot          str   — which equipment slot it occupies
#    allowed_groups list  — list of CLASS_GROUPS keys or literal class names
#    sell_price    int   — Zeny received when sold to NPC (exact, never randomised)
#    two_handed    bool  — weapon blocks shield slot if True
#    description   str   — flavour text
#    rarity        str   — "common" | "uncommon" | "rare" | "legendary"
#    tier          int   — progression tier (0=novice, 1=early, 2=mid, 3=late)
#
#  Future hooks (all None until implemented):
#    stat_bonuses  dict | None   — {"atk": 5, "def": 2, ...}
#    slots         int           — card slots (future)
#    refineable    bool          — can be upgraded (future)
# ─────────────────────────────────────────────────────────────────────────────

ITEM_DB: dict[str, dict] = {

    # ── ARMOR ────────────────────────────────────────────────────────────────

    "novice_suit": {
        "item_id":       "novice_suit",
        "name":          "Novice Suit",
        "category":      "armor",
        "slot":          "armor",
        "allowed_groups": ["Novice"],
        "sell_price":    1,
        "two_handed":    False,
        "description":   "The humble clothes of every new adventurer. Outgrow them.",
        "rarity":        "common",
        "tier":          0,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    False,
    },
    "adventurers_garb": {
        "item_id":       "adventurers_garb",
        "name":          "Adventurer's Garb",
        "category":      "armor",
        "slot":          "armor",
        "allowed_groups": ["All"],
        "sell_price":    2_500,
        "two_handed":    False,
        "description":   "A sturdy travel coat worn by those who venture beyond the city.",
        "rarity":        "common",
        "tier":          1,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    False,
    },
    "cotton_shirt": {
        "item_id":       "cotton_shirt",
        "name":          "Cotton Shirt",
        "category":      "armor",
        "slot":          "armor",
        "allowed_groups": ["All"],
        "sell_price":    5,
        "two_handed":    False,
        "description":   "It's just a shirt. But it's yours.",
        "rarity":        "common",
        "tier":          0,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    False,
    },
    "mage_coat": {
        "item_id":       "mage_coat",
        "name":          "Mage Coat",
        "category":      "armor",
        "slot":          "armor",
        "allowed_groups": ["Mage Path", "Acolyte Path"],
        "sell_price":    27_000,
        "two_handed":    False,
        "description":   "Woven with mana-conductive thread. Useless to brutes.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "ninja_suit": {
        "item_id":       "ninja_suit",
        "name":          "Ninja Suit",
        "category":      "armor",
        "slot":          "armor",
        "allowed_groups": ["Thief Path"],
        "sell_price":    32_000,
        "two_handed":    False,
        "description":   "Flexible, dark, silent. Built for those who move without sound.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "padded_armor": {
        "item_id":       "padded_armor",
        "name":          "Padded Armor",
        "category":      "armor",
        "slot":          "armor",
        "allowed_groups": ["Swordsman Path", "Archer Path", "Thief Path", "Merchant Path"],
        "sell_price":    24_000,
        "two_handed":    False,
        "description":   "Layered leather and cloth. Practical protection for active fighters.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "tights": {
        "item_id":       "tights",
        "name":          "Tights",
        "category":      "armor",
        "slot":          "armor",
        "allowed_groups": ["Archer Path", "Thief Path"],
        "sell_price":    35_500,
        "two_handed":    False,
        "description":   "Form-fitting, light, and surprisingly protective for agile classes.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "chain_mail": {
        "item_id":       "chain_mail",
        "name":          "Chain Mail",
        "category":      "armor",
        "slot":          "armor",
        "allowed_groups": ["Swordsman Path", "Merchant Path", "Acolyte Path"],
        "sell_price":    32_500,
        "two_handed":    False,
        "description":   "Interlocking rings of steel. Dependable, if heavy.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "full_plate_armor": {
        "item_id":       "full_plate_armor",
        "name":          "Full Plate Armor",
        "category":      "armor",
        "slot":          "armor",
        "allowed_groups": ["Swordsman Path", "Merchant Path"],
        "sell_price":    40_000,
        "two_handed":    False,
        "description":   "Head to toe in forged steel. Only the truly strong wear this.",
        "rarity":        "rare",
        "tier":          3,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },

    # ── SHIELDS ──────────────────────────────────────────────────────────────

    "guard": {
        "item_id":       "guard",
        "name":          "Guard",
        "category":      "shield",
        "slot":          "shield",
        "allowed_groups": ["All Except Novice"],
        "sell_price":    250,
        "two_handed":    False,
        "description":   "A small round shield. Basic, but better than nothing.",
        "rarity":        "common",
        "tier":          1,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    False,
    },
    "buckler": {
        "item_id":       "buckler",
        "name":          "Buckler",
        "category":      "shield",
        "slot":          "shield",
        "allowed_groups": ["Swordsman Path", "Merchant Path", "Thief Path",
                           "Archer Path", "Acolyte Path"],
        "sell_price":    7_000,
        "two_handed":    False,
        "description":   "A medium shield favoured by warriors who still need mobility.",
        "rarity":        "common",
        "tier":          1,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "shield": {
        "item_id":       "shield",
        "name":          "Shield",
        "category":      "shield",
        "slot":          "shield",
        "allowed_groups": ["Swordsman Path", "Knight Path", "Crusader Path"],
        "sell_price":    20_000,
        "two_handed":    False,
        "description":   "A full tower shield. Heavy, immovable, and proud.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },

    # ── GARMENTS ─────────────────────────────────────────────────────────────

    "hood": {
        "item_id":       "hood",
        "name":          "Hood",
        "category":      "garment",
        "slot":          "garment",
        "allowed_groups": ["All"],
        "sell_price":    500,
        "two_handed":    False,
        "description":   "A simple cloth hood. Keeps the wind off.",
        "rarity":        "common",
        "tier":          0,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    False,
    },
    "muffler": {
        "item_id":       "muffler",
        "name":          "Muffler",
        "category":      "garment",
        "slot":          "garment",
        "allowed_groups": ["All Except Novice"],
        "sell_price":    2_500,
        "two_handed":    False,
        "description":   "A warm wrap that offers modest protection.",
        "rarity":        "common",
        "tier":          1,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "manteau": {
        "item_id":       "manteau",
        "name":          "Manteau",
        "category":      "garment",
        "slot":          "garment",
        "allowed_groups": ["Swordsman Path", "Merchant Path", "Thief Path"],
        "sell_price":    16_000,
        "two_handed":    False,
        "description":   "A heavy cloak worn by those who fight in the thick of it.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },

    # ── SHOES ────────────────────────────────────────────────────────────────

    "sandals": {
        "item_id":       "sandals",
        "name":          "Sandals",
        "category":      "shoes",
        "slot":          "shoes",
        "allowed_groups": ["All"],
        "sell_price":    200,
        "two_handed":    False,
        "description":   "Simple leather sandals. They've carried many a Novice.",
        "rarity":        "common",
        "tier":          0,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    False,
    },
    "shoes": {
        "item_id":       "shoes",
        "name":          "Shoes",
        "category":      "shoes",
        "slot":          "shoes",
        "allowed_groups": ["All Except Novice"],
        "sell_price":    1_750,
        "two_handed":    False,
        "description":   "Proper footwear. A small upgrade with real meaning.",
        "rarity":        "common",
        "tier":          1,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "boots": {
        "item_id":       "boots",
        "name":          "Boots",
        "category":      "shoes",
        "slot":          "shoes",
        "allowed_groups": ["Swordsman Path", "Merchant Path", "Thief Path", "Archer Path"],
        "sell_price":    9_000,
        "two_handed":    False,
        "description":   "Heavy-duty boots built for long hauls and hard fights.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },

    # ── WEAPONS ──────────────────────────────────────────────────────────────

    "falchion": {
        "item_id":       "falchion",
        "name":          "Falchion",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Novice", "Swordsman Path", "Merchant Path", "Thief Path"],
        "sell_price":    600,
        "two_handed":    False,
        "description":   "A simple curved sword. The first blade of many adventurers.",
        "rarity":        "common",
        "tier":          0,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    False,
    },
    "broadsword": {
        "item_id":       "broadsword",
        "name":          "Broadsword",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Swordsman Path", "Knight Path", "Crusader Path"],
        "sell_price":    32_500,
        "two_handed":    False,
        "description":   "A wide, heavy blade suited for knights who hit hard.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "claymore": {
        "item_id":       "claymore",
        "name":          "Claymore",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Swordsman Path", "Knight Path", "Crusader Path"],
        "sell_price":    37_000,
        "two_handed":    True,
        "description":   "A massive two-handed greatsword. Power at the cost of defence.",
        "rarity":        "rare",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "stiletto": {
        "item_id":       "stiletto",
        "name":          "Stiletto",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Swordsman Path", "Mage Path", "Archer Path",
                           "Thief Path", "Merchant Path"],
        "sell_price":    9_750,
        "two_handed":    False,
        "description":   "A long thin blade. Quick, precise, versatile.",
        "rarity":        "common",
        "tier":          1,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    True,
    },
    "gladius": {
        "item_id":       "gladius",
        "name":          "Gladius",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Swordsman Path", "Mage Path", "Archer Path",
                           "Thief Path", "Merchant Path"],
        "sell_price":    21_500,
        "two_handed":    False,
        "description":   "A short, double-edged sword of exceptional balance.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "jur": {
        "item_id":       "jur",
        "name":          "Jur",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Assassin Path"],
        "sell_price":    14_000,
        "two_handed":    False,
        "description":   "Three blades fused into one. Only Assassins know how to wield it.",
        "rarity":        "rare",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "mace": {
        "item_id":       "mace",
        "name":          "Mace",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Acolyte Path", "Merchant Path"],
        "sell_price":    1_500,
        "two_handed":    False,
        "description":   "A heavy blunt weapon blessed for holy warriors.",
        "rarity":        "common",
        "tier":          1,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    False,
    },
    "chain": {
        "item_id":       "chain",
        "name":          "Chain",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Acolyte Path", "Merchant Path"],
        "sell_price":    11_500,
        "two_handed":    False,
        "description":   "A flail-like weapon with reach. Favoured by devoted fighters.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "two_handed_axe": {
        "item_id":       "two_handed_axe",
        "name":          "Two-Handed Axe",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Swordsman Path", "Merchant Path"],
        "sell_price":    27_500,
        "two_handed":    True,
        "description":   "A massive axe that demands both hands and full commitment.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "crossbow": {
        "item_id":       "crossbow",
        "name":          "Crossbow",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Archer Path", "Thief Path"],
        "sell_price":    8_500,
        "two_handed":    True,
        "description":   "A mechanical bow for quick-loading bolts. Two hands required.",
        "rarity":        "common",
        "tier":          1,
        "stat_bonuses":  None,
        "slots":         0,
        "refineable":    True,
    },
    "gakkung_bow": {
        "item_id":       "gakkung_bow",
        "name":          "Gakkung Bow",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Archer Path", "Rogue Path"],
        "sell_price":    21_000,
        "two_handed":    True,
        "description":   "A powerful recurve bow with exceptional range.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
    "arc_wand": {
        "item_id":       "arc_wand",
        "name":          "Arc Wand",
        "category":      "weapon",
        "slot":          "weapon",
        "allowed_groups": ["Mage Path", "Acolyte Path"],
        "sell_price":    22_500,
        "two_handed":    False,
        "description":   "A curved staff crackling with contained magical energy.",
        "rarity":        "uncommon",
        "tier":          2,
        "stat_bonuses":  None,
        "slots":         1,
        "refineable":    True,
    },
}


# ─────────────────────────────────────────────────────────────────────────────
#  LAZY-FILL SENTINEL GROUPS
#
#  "All" and "All Except Novice" are filled after the class DB is available.
#  We resolve them on first use rather than at import time to avoid circulars.
# ─────────────────────────────────────────────────────────────────────────────

_sentinel_groups_filled = False


def _ensure_sentinels() -> None:
    global _sentinel_groups_filled
    if _sentinel_groups_filled:
        return
    from data.constants import CLASS_DB
    all_classes = set(CLASS_DB.keys())
    CLASS_GROUPS["All"] = all_classes
    CLASS_GROUPS["All Except Novice"] = all_classes - {"Novice"}
    _sentinel_groups_filled = True


# ─────────────────────────────────────────────────────────────────────────────
#  LOOKUP HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_item(item_id: str) -> dict | None:
    """Return item dict by id, or None."""
    return ITEM_DB.get(item_id)


def get_item_by_name(name: str) -> dict | None:
    """Return item dict by display name (case-insensitive), or None."""
    name_lower = name.lower()
    for item in ITEM_DB.values():
        if item["name"].lower() == name_lower:
            return item
    return None


def items_by_slot(slot: str) -> list[dict]:
    """All items for a given equipment slot."""
    return [i for i in ITEM_DB.values() if i["slot"] == slot]


def all_items_sorted() -> list[dict]:
    """All items sorted by tier, then name."""
    return sorted(ITEM_DB.values(), key=lambda i: (i["tier"], i["name"]))


# ─────────────────────────────────────────────────────────────────────────────
#  EQUIP VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

class EquipResult:
    def __init__(self, ok: bool, reason: str = ""):
        self.ok     = ok
        self.reason = reason

    def __bool__(self) -> bool:
        return self.ok


def _class_allowed(item: dict, char_class: str) -> bool:
    """Check if char_class is in any of the item's allowed_groups."""
    _ensure_sentinels()
    for group_name in item["allowed_groups"]:
        group = CLASS_GROUPS.get(group_name)
        if group is None:
            # Literal class name
            if char_class == group_name:
                return True
        else:
            if char_class in group:
                return True
    return False


def can_equip(item: dict, char_class: str, equipped: dict) -> EquipResult:
    """
    Validate whether a character can equip `item`.

    equipped : current equipment dict  {slot: item_id | None}

    Returns EquipResult(ok, reason).
    """
    # Class restriction
    if not _class_allowed(item, char_class):
        # Build a human-readable list of allowed paths
        allowed_display = _allowed_paths_text(item)
        return EquipResult(
            False,
            f"Cannot equip: {item['name']}\n"
            f"Requires: {allowed_display}"
        )

    # Two-handed weapon blocks shield
    if item["slot"] == "weapon" and item.get("two_handed"):
        shield_id = equipped.get("shield")
        if shield_id:
            shield = get_item(shield_id)
            shield_name = shield["name"] if shield else "Shield"
            return EquipResult(
                False,
                f"{item['name']} is two-handed.\n"
                f"Remove your {shield_name} first."
            )

    # Equipping a shield while wielding a two-handed weapon
    if item["slot"] == "shield":
        weapon_id = equipped.get("weapon")
        if weapon_id:
            weapon = get_item(weapon_id)
            if weapon and weapon.get("two_handed"):
                return EquipResult(
                    False,
                    f"Cannot equip shield while wielding {weapon['name']}.\n"
                    f"{weapon['name']} is two-handed."
                )

    return EquipResult(True)


def _allowed_paths_text(item: dict) -> str:
    """Return comma-separated human-readable restriction list."""
    groups = item["allowed_groups"]
    if "All" in groups:
        return "All Classes"
    if "All Except Novice" in groups:
        return "All Classes (except Novice)"
    return ", ".join(groups)


# ─────────────────────────────────────────────────────────────────────────────
#  STARTER LOADOUT
# ─────────────────────────────────────────────────────────────────────────────

STARTER_EQUIPMENT: dict[str, str | None] = {
    "weapon":  "falchion",
    "armor":   "novice_suit",
    "shield":  None,
    "garment": "hood",
    "shoes":   "sandals",
}

STARTER_INVENTORY: list[str] = [
    "cotton_shirt",
]

STARTER_ZENY: int = 500
