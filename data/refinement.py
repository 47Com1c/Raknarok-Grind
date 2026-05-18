"""
RAGNAROK GRIND — Refinement System
Classic Ragnarok-style weapon and equipment refinement.

Design:
  +0 → +10 refinement levels
  Weapons use Oridecon, armor/shield/garment/shoes use Elunium
  +1 to +4: guaranteed success
  +5 to +6: high success rate
  +7 to +8: medium success rate
  +9 to +10: low success rate
  Failure consumes materials but does NOT destroy or downgrade the item (MVP rule)
"""

from __future__ import annotations

import random
from dataclasses import dataclass


# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

REFINE_MAX = 10

# Materials
MATERIAL_WEAPON    = "Oridecon"
MATERIAL_EQUIPMENT = "Elunium"

# Slots that use Elunium (wearable equipment)
EQUIPMENT_SLOTS = {"armor", "shield", "garment", "shoes"}

# Success rate table — key is the TARGET level you're refining TO
# e.g. refining +4 → +5 uses REFINE_RATES[5]
REFINE_RATES: dict[int, float] = {
    1:  1.00,   # guaranteed
    2:  1.00,   # guaranteed
    3:  1.00,   # guaranteed
    4:  1.00,   # guaranteed
    5:  0.80,   # high
    6:  0.72,   # high
    7:  0.52,   # medium
    8:  0.40,   # medium
    9:  0.25,   # low
    10: 0.16,   # low / legendary
}

# Stat bonus per refine level (flat, per level)
# Weapons: ATK bonus
# Equipment: DEF bonus
REFINE_ATK_PER_LEVEL = 1   # +1 ATK per refine level
REFINE_DEF_PER_LEVEL = 1   # +1 DEF per refine level

# Material cost per refine attempt (always 1 for MVP simplicity)
MATERIAL_COST = 1


# ─────────────────────────────────────────────────────────────────────────────
#  RESULT DATACLASS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RefineResult:
    success:      bool
    new_level:    int
    old_level:    int
    item_name:    str
    material:     str
    rate:         float
    message:      str


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_material_for_slot(slot: str) -> str:
    """Return the refinement material required for a given equipment slot."""
    if slot == "weapon":
        return MATERIAL_WEAPON
    return MATERIAL_EQUIPMENT


def get_refine_rate(target_level: int) -> float:
    """Return the success probability for refining to target_level."""
    return REFINE_RATES.get(target_level, 0.0)


def get_atk_bonus(refine_level: int) -> int:
    """Total ATK bonus granted by this refinement level."""
    return refine_level * REFINE_ATK_PER_LEVEL


def get_def_bonus(refine_level: int) -> int:
    """Total DEF bonus granted by this refinement level."""
    return refine_level * REFINE_DEF_PER_LEVEL


def refine_display_name(item_name: str, refine_level: int) -> str:
    """
    Return the display name with refine prefix.
    e.g. 'Claymore' at +5 → '+5 Claymore'
         'Claymore' at +0 → 'Claymore'
    """
    if refine_level <= 0:
        return item_name
    return f"+{refine_level} {item_name}"


def can_refine(item: dict, current_level: int) -> tuple[bool, str]:
    """
    Validate whether an item can be refined further.
    Returns (ok, reason_string).
    """
    if not item.get("refineable", False):
        return False, f"{item['name']} cannot be refined."

    if current_level >= REFINE_MAX:
        return False, f"{refine_display_name(item['name'], current_level)} has reached the maximum refinement level (+{REFINE_MAX})."

    return True, ""


def attempt_refine(
    item: dict,
    slot: str,
    current_level: int,
    char_materials: dict,
) -> tuple[RefineResult | None, str]:
    """
    Attempt to refine an item by one level.

    Parameters:
        item           — the item dict from ITEM_DB
        slot           — equipment slot string ("weapon", "armor", etc.)
        current_level  — current refine level (0..9)
        char_materials — character's materials dict {"Oridecon": n, "Elunium": n}

    Returns:
        (RefineResult, "")         on valid attempt (success or failure)
        (None,         error_msg)  if preconditions not met
    """
    # Validate refineable
    ok, reason = can_refine(item, current_level)
    if not ok:
        return None, reason

    target_level = current_level + 1
    material = get_material_for_slot(slot)
    rate     = get_refine_rate(target_level)

    # Check material inventory
    owned = char_materials.get(material, 0)
    if owned < MATERIAL_COST:
        return None, (
            f"Not enough {material}.\n"
            f"Required: {MATERIAL_COST}  |  You have: {owned}"
        )

    # Consume material
    char_materials[material] = owned - MATERIAL_COST

    # Roll for success
    rolled   = random.random()
    success  = rolled < rate
    new_lvl  = target_level if success else current_level

    item_display = refine_display_name(item["name"], current_level)

    if success:
        msg = (
            f"SUCCESS!\n"
            f"{item['name']}\n"
            f"+{current_level} → +{new_lvl}"
        )
    else:
        msg = (
            f"Refinement Failed.\n"
            f"Materials consumed.\n"
            f"Refinement unchanged."
        )

    return RefineResult(
        success=success,
        new_level=new_lvl,
        old_level=current_level,
        item_name=item["name"],
        material=material,
        rate=rate,
        message=msg,
    ), ""
