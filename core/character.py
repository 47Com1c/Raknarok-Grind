"""
RAGNAROK GRIND — Character & Save System
SQLite-backed character persistence. Full class/level/equipment state.

Save format v3: adds zeny, equipment slots, item_inventory.
Includes migration from v1/v2 saves.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from data.constants import (
    get_class, get_class_tier, get_available_branches,
    base_exp_to_level, job_exp_to_level,
    REBIRTH_REQ, TRANSCENDENCE_BONUSES,
    ALL_CLASSES, get_aura_frame,
    REBIRTH_CLASS_MAP,
)

SAVES_DIR = Path(__file__).parent.parent / "saves"
SAVES_DIR.mkdir(exist_ok=True)
DB_PATH   = SAVES_DIR / "ragnarok_grind.db"

SAVE_VERSION = 4


# ─────────────────────────────────────────────
#  CHARACTER DATACLASS
# ─────────────────────────────────────────────

@dataclass
class Character:
    name: str
    char_class: str = "Novice"

    # Gender — affects Bard/Dancer/Clown/Gypsy/Maestro/Wanderer branches
    gender: str = "male"   # "male" | "female"

    # Core levels
    base_level: int = 1
    base_exp:   int = 0
    job_level:  int = 1
    job_exp:    int = 0

    # Rebirth / Transcendence
    rebirth_count:   int  = 0
    is_transcendent: bool = False

    # Job path history
    job_history: list = field(default_factory=lambda: ["Novice"])

    # ── Economy ──────────────────────────────────────────────────────────────
    zeny: int = 0   # set to STARTER_ZENY on new character creation

    # ── Equipment slots ───────────────────────────────────────────────────────
    # Each value is an item_id string or None
    equipment: dict = field(default_factory=lambda: {
        "weapon":  None,
        "armor":   None,
        "shield":  None,
        "garment": None,
        "shoes":   None,
    })

    # ── Item inventory (equipment items, not cosmetic drops) ──────────────────
    # List of item_id strings; duplicates allowed (stack qty not tracked yet)
    item_inventory: list = field(default_factory=list)

    # ── Refinement ────────────────────────────────────────────────────────────
    # Maps item_id → refine level (int 0..10).
    # Only items that have been refined appear here; absent == +0.
    refine_levels: dict = field(default_factory=dict)

    # ── Refinement materials ──────────────────────────────────────────────────
    # {"Oridecon": n, "Elunium": n}
    materials: dict = field(default_factory=lambda: {
        "Oridecon": 0,
        "Elunium":  0,
    })

    # Session stats
    total_sessions:    int = 0
    total_minutes:     int = 0
    streak:            int = 0
    last_session_date: Optional[str] = None

    # Cosmetic drops (legacy field — kept separate from item_inventory)
    titles:       list = field(default_factory=list)
    active_title: str  = ""
    inventory:    list = field(default_factory=list)   # cosmetic drops
    session_log:  list = field(default_factory=list)

    # Meta
    created_at:             str = field(default_factory=lambda: datetime.now().isoformat())
    total_playtime_seconds: int = 0

    # ── Legacy compat ────────────────────────────────────────────────────────
    @property
    def transcendence_count(self) -> int:
        return self.rebirth_count

    # ── Derived properties ───────────────────────────────────────────────────

    @property
    def class_data(self) -> dict:
        return get_class(self.char_class)

    @property
    def class_tier(self) -> int:
        return get_class_tier(self.char_class)

    @property
    def base_exp_to_next(self) -> int:
        return base_exp_to_level(self.base_level + 1)

    @property
    def job_exp_to_next(self) -> int:
        return job_exp_to_level(self.job_level + 1, self.class_tier)

    @property
    def base_exp_progress(self) -> float:
        needed = self.base_exp_to_next
        return 1.0 if needed == 0 else min(1.0, self.base_exp / needed)

    @property
    def job_exp_progress(self) -> float:
        needed = self.job_exp_to_next
        return 1.0 if needed == 0 else min(1.0, self.job_exp / needed)

    @property
    def job_max(self) -> int:
        return self.class_data.get("job_max", 50)

    @property
    def base_max(self) -> int:
        return self.class_data.get("base_max", 99)

    @property
    def exp_bonus(self) -> float:
        count = min(self.rebirth_count, 3)
        return 0.0 if count == 0 else TRANSCENDENCE_BONUSES[count]["exp_bonus"]

    @property
    def aura(self) -> str:
        tier = self.class_tier
        if self.is_transcendent:
            tier = max(tier, 3)
        return get_aura_frame(tier, self.base_level)

    @property
    def display_class(self) -> str:
        if self.rebirth_count > 0:
            return f"{self.char_class} {'★' * min(self.rebirth_count, 3)}"
        return self.char_class

    @property
    def available_branches(self) -> list:
        return get_available_branches(
            self.char_class, self.base_level, self.job_level,
            self.rebirth_count, self.gender,
        )

    @property
    def can_transcend(self) -> bool:
        return self.can_rebirth

    @property
    def can_rebirth(self) -> bool:
        from core.progression import can_rebirth
        return can_rebirth(
            self.char_class, self.base_level, self.job_level, self.rebirth_count
        ).eligible

    @property
    def next_advancement_hint(self) -> str:
        from core.progression import get_next_advancement_hint
        return get_next_advancement_hint(
            self.char_class, self.base_level, self.job_level,
            self.rebirth_count, self.gender,
        )

    @property
    def class_path_display(self) -> str:
        from core.progression import build_class_path
        return build_class_path(self.job_history)

    # ── Equipment helpers ────────────────────────────────────────────────────

    def equipped_item(self, slot: str) -> dict | None:
        """Return the item dict in a given slot, or None."""
        from data.items import get_item
        item_id = self.equipment.get(slot)
        return get_item(item_id) if item_id else None

    def equip_item(self, item_id: str) -> tuple[bool, str]:
        """
        Attempt to equip an item from item_inventory.
        Returns (success, message).
        The previously equipped item is moved back to item_inventory.
        """
        from data.items import get_item, can_equip
        item = get_item(item_id)
        if not item:
            return False, f"Unknown item: {item_id}"

        if item_id not in self.item_inventory:
            return False, f"{item['name']} is not in your inventory."

        result = can_equip(item, self.char_class, self.equipment)
        if not result.ok:
            return False, result.reason

        slot = item["slot"]
        old_id = self.equipment.get(slot)
        if old_id:
            self.item_inventory.append(old_id)

        self.item_inventory.remove(item_id)
        self.equipment[slot] = item_id
        return True, f"Equipped: {item['name']}"

    def unequip_slot(self, slot: str) -> tuple[bool, str]:
        """Move equipped item in slot back to inventory."""
        item_id = self.equipment.get(slot)
        if not item_id:
            return False, f"Nothing equipped in {slot}."
        from data.items import get_item
        item = get_item(item_id)
        name = item["name"] if item else item_id
        self.equipment[slot] = None
        self.item_inventory.append(item_id)
        return True, f"Unequipped: {name}"

    def sell_item(self, item_id: str) -> tuple[bool, int, str]:
        """
        Sell an item from item_inventory to the NPC.
        Returns (success, zeny_gained, message).
        Equipped items cannot be sold.
        """
        from data.items import get_item
        if item_id not in self.item_inventory:
            # Check if it's equipped
            for slot, eid in self.equipment.items():
                if eid == item_id:
                    item = get_item(item_id)
                    name = item["name"] if item else item_id
                    return False, 0, f"{name} is currently equipped. Unequip it first."
            return False, 0, "Item not in inventory."

        item = get_item(item_id)
        if not item:
            return False, 0, f"Unknown item: {item_id}"

        price = item["sell_price"]
        self.item_inventory.remove(item_id)
        self.zeny += price
        return True, price, f"Sold {item['name']} for {price:,}z"

    def add_item(self, item_id: str) -> None:
        """Add an item to item_inventory (e.g. from starter kit or future drops)."""
        self.item_inventory.append(item_id)

    # ── Refinement helpers ───────────────────────────────────────────────────

    def get_refine_level(self, item_id: str) -> int:
        """Return the current refinement level for an item (default 0)."""
        return self.refine_levels.get(item_id, 0)

    def set_refine_level(self, item_id: str, level: int) -> None:
        """Update refinement level for an item."""
        if level <= 0:
            self.refine_levels.pop(item_id, None)
        else:
            self.refine_levels[item_id] = level

    def add_material(self, material: str, qty: int = 1) -> None:
        """Add refinement material to the character's stock."""
        if material not in self.materials:
            self.materials[material] = 0
        self.materials[material] += qty

    def get_material_count(self, material: str) -> int:
        """Return the character's stock of a refinement material."""
        return self.materials.get(material, 0)

    def give_starter_equipment(self) -> None:
        """Give a new character their starting gear and Zeny."""
        from data.items import STARTER_EQUIPMENT, STARTER_INVENTORY, STARTER_ZENY
        self.zeny = STARTER_ZENY
        for slot, item_id in STARTER_EQUIPMENT.items():
            if item_id:
                self.equipment[slot] = item_id
        for item_id in STARTER_INVENTORY:
            self.item_inventory.append(item_id)

    # ── EXP / levelling ─────────────────────────────────────────────────────

    def add_exp(self, base_exp: int, job_exp: int) -> dict:
        events = {
            "base_levels_gained": [],
            "job_levels_gained":  [],
            "base_exp_added":     base_exp,
            "job_exp_added":      job_exp,
        }
        bonus    = self.exp_bonus
        base_exp = int(base_exp * (1 + bonus))
        job_exp  = int(job_exp  * (1 + bonus))

        self.base_exp += base_exp
        while self.base_level < self.base_max:
            needed = base_exp_to_level(self.base_level + 1)
            if self.base_exp >= needed:
                self.base_exp  -= needed
                self.base_level += 1
                events["base_levels_gained"].append(self.base_level)
            else:
                break

        self.job_exp += job_exp
        while self.job_level < self.job_max:
            needed = job_exp_to_level(self.job_level + 1, self.class_tier)
            if self.job_exp >= needed:
                self.job_exp  -= needed
                self.job_level += 1
                events["job_levels_gained"].append(self.job_level)
            else:
                break

        return events

    # ── Class change / rebirth ───────────────────────────────────────────────

    def change_class(self, new_class: str) -> bool:
        from core.progression import can_advance_to
        result = can_advance_to(
            new_class, self.char_class,
            self.base_level, self.job_level,
            self.rebirth_count, self.gender,
        )
        if not result:
            return False
        self.char_class = new_class
        self.job_level  = 1
        self.job_exp    = 0
        if new_class not in self.job_history:
            self.job_history.append(new_class)
        return True

    def perform_rebirth(self) -> bool:
        from core.progression import can_rebirth
        if not can_rebirth(
            self.char_class, self.base_level, self.job_level, self.rebirth_count
        ).eligible:
            return False
        self.job_history.append("High Novice")
        self.char_class      = "High Novice"
        self.base_level      = 1
        self.base_exp        = 0
        self.job_level       = 1
        self.job_exp         = 0
        self.rebirth_count  += 1
        self.is_transcendent = True
        if "Reborn" not in self.titles:
            self.titles.append("Reborn")
        if self.rebirth_count >= 2 and "Twice Reborn" not in self.titles:
            self.titles.append("Twice Reborn")
        return True

    def transcend(self) -> bool:
        return self.perform_rebirth()

    # ── Session recording ────────────────────────────────────────────────────

    def record_session(self, minutes: int, zone_id: str,
                       base_exp: int, job_exp: int, drops: list) -> None:
        self.total_sessions += 1
        self.total_minutes  += minutes
        entry = {
            "date":     datetime.now().isoformat()[:16],
            "minutes":  minutes,
            "zone":     zone_id,
            "base_exp": base_exp,
            "job_exp":  job_exp,
            "drops":    drops,
        }
        self.session_log.insert(0, entry)
        self.session_log = self.session_log[:20]

        today = datetime.now().date().isoformat()
        if self.last_session_date:
            from datetime import date
            last = date.fromisoformat(self.last_session_date)
            diff = (date.today() - last).days
            if diff == 1:
                self.streak += 1
            elif diff > 1:
                self.streak = 1
        else:
            self.streak = 1
        self.last_session_date = today

    def award_title(self, title: str) -> bool:
        if title not in self.titles:
            self.titles.append(title)
            return True
        return False

    def check_milestone_titles(self) -> list:
        earned = []
        milestones = {
            "The Grind Begins":  self.total_sessions >= 10,
            "Seasoned Farmer":   self.total_sessions >= 50,
            "True Grinder":      self.total_sessions >= 100,
            "Endless Devotion":  self.total_sessions >= 365,
            "The Awakened":      self.base_level >= 50,
            "Century Knight":    self.base_level >= 99,
            "Lord of the Grind": self.class_tier >= 4,
            "The Devoted":       self.streak >= 7,
            "Unbroken":          self.streak >= 30,
            "Eternal":           self.streak >= 100,
            "Novice No More":    self.class_tier >= 1,
            "Path Chosen":       self.class_tier >= 2,
            "Transcendent":      self.class_tier >= 3 and self.is_transcendent,
        }
        for title, condition in milestones.items():
            if condition and self.award_title(title):
                earned.append(title)
        return earned


# ─────────────────────────────────────────────
#  SAVE / LOAD (SQLite)
# ─────────────────────────────────────────────

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                name        TEXT PRIMARY KEY,
                data        TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            )
        """)
        conn.commit()


def _serialize(char: Character) -> dict:
    return {
        "_save_version":        SAVE_VERSION,
        "name":                 char.name,
        "gender":               char.gender,
        "char_class":           char.char_class,
        "base_level":           char.base_level,
        "base_exp":             char.base_exp,
        "job_level":            char.job_level,
        "job_exp":              char.job_exp,
        "rebirth_count":        char.rebirth_count,
        "is_transcendent":      char.is_transcendent,
        "job_history":          char.job_history,
        "zeny":                 char.zeny,
        "equipment":            char.equipment,
        "item_inventory":       char.item_inventory,
        "refine_levels":        char.refine_levels,
        "materials":            char.materials,
        "total_sessions":       char.total_sessions,
        "total_minutes":        char.total_minutes,
        "streak":               char.streak,
        "last_session_date":    char.last_session_date,
        "titles":               char.titles,
        "active_title":         char.active_title,
        "inventory":            char.inventory,
        "session_log":          char.session_log,
        "created_at":           char.created_at,
        "total_playtime_seconds": char.total_playtime_seconds,
    }


def _migrate(d: dict) -> dict:
    """Migrate save data from any old version to current."""
    version = d.get("_save_version", 1)

    # v1 → v2: rename transcendence_count, add gender / job_history
    if version < 2:
        d["rebirth_count"] = d.pop("transcendence_count", 0)
        d["gender"]        = "male"
        cls = d.get("char_class", "Novice")
        d["job_history"]   = ["Novice", cls] if cls != "Novice" else ["Novice"]
        version = 2

    # v2 → v3: add zeny, equipment, item_inventory
    if version < 3:
        d["zeny"]           = 0
        d["equipment"]      = {
            "weapon": None, "armor": None, "shield": None,
            "garment": None, "shoes": None,
        }
        d["item_inventory"] = []
        version = 3

    # v3 → v4: add refine_levels, materials
    if version < 4:
        d["refine_levels"] = {}
        d["materials"]     = {"Oridecon": 0, "Elunium": 0}
        version = 4

    d["_save_version"] = SAVE_VERSION
    return d


def _deserialize(d: dict) -> Character:
    d = _migrate(d)
    char = Character(name=d["name"])
    fields = [
        "gender", "char_class", "base_level", "base_exp", "job_level", "job_exp",
        "rebirth_count", "is_transcendent", "job_history",
        "zeny", "equipment", "item_inventory",
        "refine_levels", "materials",
        "total_sessions", "total_minutes", "streak", "last_session_date",
        "titles", "active_title", "inventory", "session_log",
        "created_at", "total_playtime_seconds",
    ]
    for k in fields:
        if k in d:
            setattr(char, k, d[k])
    return char


def save_character(char: Character) -> None:
    init_db()
    with _get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO characters (name, data, updated_at) VALUES (?, ?, ?)",
            (char.name, json.dumps(_serialize(char)), datetime.now().isoformat())
        )
        conn.commit()


def load_character(name: str) -> Optional[Character]:
    init_db()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT data FROM characters WHERE name = ?", (name,)
        ).fetchone()
    if not row:
        return None
    return _deserialize(json.loads(row["data"]))


def list_characters() -> list:
    init_db()
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT name, data, updated_at FROM characters ORDER BY updated_at DESC"
        ).fetchall()
    result = []
    for row in rows:
        d = json.loads(row["data"])
        result.append({
            "name":       d["name"],
            "class":      d["char_class"],
            "base_level": d["base_level"],
            "gender":     d.get("gender", "male"),
            "updated_at": row["updated_at"][:16],
        })
    return result


def delete_character(name: str) -> bool:
    init_db()
    with _get_connection() as conn:
        cur = conn.execute("DELETE FROM characters WHERE name = ?", (name,))
        conn.commit()
    return cur.rowcount > 0


def character_exists(name: str) -> bool:
    init_db()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM characters WHERE name = ?", (name,)
        ).fetchone()
    return row is not None
