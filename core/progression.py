"""
RAGNAROK GRIND — Progression Engine
Data-driven class advancement validator and resolver.

All advancement rules live here. No if/else spaghetti elsewhere.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.character import Character


# ─────────────────────────────────────────────────────────────────────────────
#  ADVANCEMENT REQUIREMENTS
#
#  Each class entry defines what it needs to unlock AS A DESTINATION.
#  The engine checks these when evaluating if a character can change class.
#
#  Fields:
#    from_class   : the class the character must currently be
#    base_req     : minimum base level required
#    job_req      : minimum job level required
#    rebirth_req  : must have rebirths >= this value (0 = any)
#    gender_lock  : "male" | "female" | None (no restriction)
#    is_rebirth   : True means this IS the rebirth destination (High Novice)
# ─────────────────────────────────────────────────────────────────────────────

ADVANCEMENT_RULES: dict[str, dict] = {

    # ── FIRST JOBS (from Novice, Job 10) ─────────────────────────────────────
    "Swordsman": {
        "from_class":  "Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Mage": {
        "from_class":  "Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Archer": {
        "from_class":  "Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Acolyte": {
        "from_class":  "Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Thief": {
        "from_class":  "Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Merchant": {
        "from_class":  "Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },

    # ── SECOND JOBS (from 1st job, Base 1+ / Job 40+) ────────────────────────
    # RO allows 2nd job from Base 1, Job 40 (before trans path).
    # We keep base_req=1 for the non-rebirth path.
    "Knight": {
        "from_class":  "Swordsman",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Crusader": {
        "from_class":  "Swordsman",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Wizard": {
        "from_class":  "Mage",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Sage": {
        "from_class":  "Mage",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Hunter": {
        "from_class":  "Archer",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Bard": {
        "from_class":  "Archer",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": "male",
        "is_rebirth":  False,
    },
    "Dancer": {
        "from_class":  "Archer",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": "female",
        "is_rebirth":  False,
    },
    "Priest": {
        "from_class":  "Acolyte",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Monk": {
        "from_class":  "Acolyte",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Assassin": {
        "from_class":  "Thief",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Rogue": {
        "from_class":  "Thief",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Blacksmith": {
        "from_class":  "Merchant",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Alchemist": {
        "from_class":  "Merchant",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  False,
    },

    # ── REBIRTH (from 2nd job, Base 99 + Job 50) → High Novice ───────────────
    # This is handled specially by the rebirth flow, not class change.
    # Kept here for documentation and validation purposes.
    "High Novice": {
        "from_class":  None,   # any 2nd-job class
        "base_req":    99,
        "job_req":     50,
        "rebirth_req": 0,
        "gender_lock": None,
        "is_rebirth":  True,
    },

    # ── HIGH FIRST JOBS (from High Novice, Job 10) ───────────────────────────
    "High Swordsman": {
        "from_class":  "High Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "High Mage": {
        "from_class":  "High Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "High Archer": {
        "from_class":  "High Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "High Acolyte": {
        "from_class":  "High Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "High Thief": {
        "from_class":  "High Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "High Merchant": {
        "from_class":  "High Novice",
        "base_req":    1,
        "job_req":     10,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },

    # ── TRANSCENDENT 2ND JOBS (from High 1st, Base 1+ / Job 40+) ─────────────
    "Lord Knight": {
        "from_class":  "High Swordsman",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Paladin": {
        "from_class":  "High Swordsman",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "High Wizard": {
        "from_class":  "High Mage",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Professor": {
        "from_class":  "High Mage",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Sniper": {
        "from_class":  "High Archer",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Clown": {
        "from_class":  "High Archer",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": "male",
        "is_rebirth":  False,
    },
    "Gypsy": {
        "from_class":  "High Archer",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": "female",
        "is_rebirth":  False,
    },
    "High Priest": {
        "from_class":  "High Acolyte",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Champion": {
        "from_class":  "High Acolyte",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Assassin Cross": {
        "from_class":  "High Thief",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Stalker": {
        "from_class":  "High Thief",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Whitesmith": {
        "from_class":  "High Merchant",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Biochemist": {
        "from_class":  "High Merchant",
        "base_req":    1,
        "job_req":     40,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },

    # ── THIRD JOBS (from Transcendent 2nd, Base 99 + Job 70) ─────────────────
    "Rune Knight": {
        "from_class":  "Lord Knight",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Royal Guard": {
        "from_class":  "Paladin",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Warlock": {
        "from_class":  "High Wizard",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Sorcerer": {
        "from_class":  "Professor",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Ranger": {
        "from_class":  "Sniper",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Maestro": {
        "from_class":  "Clown",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Wanderer": {
        "from_class":  "Gypsy",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Arch Bishop": {
        "from_class":  "High Priest",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Sura": {
        "from_class":  "Champion",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Guillotine Cross": {
        "from_class":  "Assassin Cross",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Shadow Chaser": {
        "from_class":  "Stalker",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Mechanic": {
        "from_class":  "Whitesmith",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
    "Geneticist": {
        "from_class":  "Biochemist",
        "base_req":    99,
        "job_req":     70,
        "rebirth_req": 1,
        "gender_lock": None,
        "is_rebirth":  False,
    },
}


# ── Reverse map: class → list of classes it can advance to ───────────────────
def _build_branch_map() -> dict[str, list[str]]:
    """Build a map of class → available next classes."""
    branches: dict[str, list[str]] = {}
    for dest, rule in ADVANCEMENT_RULES.items():
        if rule["is_rebirth"]:
            continue  # rebirth handled separately
        src = rule["from_class"]
        if src is not None:
            branches.setdefault(src, []).append(dest)
    return branches


BRANCH_MAP: dict[str, list[str]] = _build_branch_map()


# ─────────────────────────────────────────────────────────────────────────────
#  VALIDATION RESULT
# ─────────────────────────────────────────────────────────────────────────────

class AdvancementResult:
    def __init__(
        self,
        eligible: bool,
        reason: str = "",
        missing_base: int = 0,
        missing_job: int = 0,
    ):
        self.eligible    = eligible
        self.reason      = reason
        self.missing_base = missing_base
        self.missing_job  = missing_job

    def __bool__(self) -> bool:
        return self.eligible


# ─────────────────────────────────────────────────────────────────────────────
#  CORE VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────

def can_advance_to(
    target_class: str,
    current_class: str,
    base_level: int,
    job_level: int,
    rebirth_count: int,
    gender: str,             # "male" | "female"
) -> AdvancementResult:
    """
    Check if a character can advance to `target_class`.
    Returns an AdvancementResult with eligibility and reason.
    """
    rule = ADVANCEMENT_RULES.get(target_class)
    if rule is None:
        return AdvancementResult(False, f"Unknown class: {target_class}")

    # From-class check
    if rule["from_class"] is not None and current_class != rule["from_class"]:
        return AdvancementResult(
            False,
            f"Must be {rule['from_class']} (currently {current_class})"
        )

    # Rebirth count check
    if rebirth_count < rule["rebirth_req"]:
        return AdvancementResult(
            False,
            f"Requires {rule['rebirth_req']} rebirth(s)"
        )

    # Gender lock
    if rule["gender_lock"] and gender != rule["gender_lock"]:
        gender_name = rule["gender_lock"].capitalize()
        return AdvancementResult(
            False,
            f"{target_class} is {gender_name}-only"
        )

    # Level requirements
    missing_base = max(0, rule["base_req"] - base_level)
    missing_job  = max(0, rule["job_req"]  - job_level)

    if missing_base > 0 or missing_job > 0:
        parts = []
        if missing_base:
            parts.append(f"Base Lv.{rule['base_req']} ({missing_base} more)")
        if missing_job:
            parts.append(f"Job Lv.{rule['job_req']} ({missing_job} more)")
        return AdvancementResult(
            False,
            "Requires: " + " and ".join(parts),
            missing_base=missing_base,
            missing_job=missing_job,
        )

    return AdvancementResult(True, "Eligible")


def get_available_advancements(
    current_class: str,
    base_level: int,
    job_level: int,
    rebirth_count: int,
    gender: str,
) -> list[str]:
    """
    Return list of class names this character can currently advance to.
    Filters by all requirements including gender.
    """
    candidates = BRANCH_MAP.get(current_class, [])
    result = []
    for cls_name in candidates:
        check = can_advance_to(
            cls_name, current_class,
            base_level, job_level, rebirth_count, gender
        )
        if check.eligible:
            result.append(cls_name)
    return result


def can_rebirth(
    current_class: str,
    base_level: int,
    job_level: int,
    rebirth_count: int,
) -> AdvancementResult:
    """
    Check if a character can perform Rebirth (become High Novice).
    Must be at a 2nd-job class (tier 2) and NOT already reborn/transcendent.
    """
    from data.constants import get_class_tier

    tier = get_class_tier(current_class)

    if tier != 2:
        return AdvancementResult(
            False,
            f"Rebirth requires a Second Class (currently Tier {tier})"
        )

    rule = ADVANCEMENT_RULES["High Novice"]
    missing_base = max(0, rule["base_req"] - base_level)
    missing_job  = max(0, rule["job_req"]  - job_level)

    if missing_base or missing_job:
        parts = []
        if missing_base:
            parts.append(f"Base Lv.99 ({missing_base} more)")
        if missing_job:
            parts.append(f"Job Lv.50 ({missing_job} more)")
        return AdvancementResult(
            False,
            "Rebirth requires: " + " and ".join(parts),
            missing_base=missing_base,
            missing_job=missing_job,
        )

    return AdvancementResult(True, "Ready for Rebirth")


def get_advancement_requirement_text(
    current_class: str,
    gender: str,
) -> list[tuple[str, str]]:
    """
    Return a list of (class_name, requirement_summary) for display
    of what's needed to advance, even if not yet eligible.
    """
    candidates = BRANCH_MAP.get(current_class, [])
    result = []
    for cls_name in candidates:
        rule = ADVANCEMENT_RULES.get(cls_name, {})
        gender_lock = rule.get("gender_lock")
        if gender_lock and gender_lock != gender:
            continue  # skip gender-locked options the player can never reach
        base_req = rule.get("base_req", 0)
        job_req  = rule.get("job_req", 0)
        req_text = f"Base Lv.{base_req} + Job Lv.{job_req}"
        result.append((cls_name, req_text))
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  PATH RECONSTRUCTION
# ─────────────────────────────────────────────────────────────────────────────

def build_class_path(job_history: list[str]) -> str:
    """
    Given a list of classes in order (job_history), return a display string.
    Example: "Novice → Swordsman → Knight → Lord Knight → Rune Knight"
    """
    if not job_history:
        return "Novice"
    return " → ".join(job_history)


def get_next_advancement_hint(
    current_class: str,
    base_level: int,
    job_level: int,
    rebirth_count: int,
    gender: str,
) -> str:
    """
    Returns a human-readable hint about what the next advancement step is.
    """
    from data.constants import get_class_tier

    tier = get_class_tier(current_class)

    # Check if rebirth is the next step (2nd job class, not yet reborn)
    if tier == 2 and rebirth_count == 0:
        check = can_rebirth(current_class, base_level, job_level, rebirth_count)
        if check.eligible:
            return "Ready for Rebirth → High Novice"
        return f"Rebirth: need Base Lv.99, Job Lv.50"

    candidates = BRANCH_MAP.get(current_class, [])
    if not candidates:
        return "You have reached the pinnacle of this path."

    # Filter for gender
    reachable = []
    for cls_name in candidates:
        rule = ADVANCEMENT_RULES.get(cls_name, {})
        if rule.get("gender_lock") and rule["gender_lock"] != gender:
            continue
        reachable.append(cls_name)

    if not reachable:
        return "No available advancements."

    # Check which are available now vs still locked
    available_now = get_available_advancements(
        current_class, base_level, job_level, rebirth_count, gender
    )

    if available_now:
        return "Class change available: " + ", ".join(available_now)

    # Show nearest requirement
    hints = []
    for cls_name in reachable:
        rule = ADVANCEMENT_RULES.get(cls_name, {})
        base_req = rule.get("base_req", 0)
        job_req  = rule.get("job_req", 0)
        hints.append(f"{cls_name} (Base {base_req} / Job {job_req})")

    return "Next: " + " | ".join(hints)
