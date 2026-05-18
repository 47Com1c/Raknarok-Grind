"""
RAGNAROK GRIND — Terminal UI
All display panels, menus, and interactive screens.
Nostalgic MMORPG terminal aesthetics via Rich.
"""

import time
import random
from rich.console import Console
from rich.text import Text
from rich.prompt import Prompt, Confirm

from data.constants import (
    ZONES, ALL_CLASSES, TITLES, RARITY_COLORS,
    get_available_zones, REBIRTH_REQ,
    CLASS_TREE, get_class,
    TRANSCENDENCE_BONUSES,
)
from core.character import Character, save_character

console = Console()

BORDER      = "dim"
ACCENT      = "bright_yellow"
TITLE_STYLE = "bold bright_yellow"
SEPARATOR   = "  " + "─" * 50

BOOT_LOGO = r"""
  ██████╗  █████╗  ██████╗ ███╗   ██╗ █████╗ ██████╗  ██████╗ ██╗  ██╗
  ██╔══██╗██╔══██╗██╔════╝ ████╗  ██║██╔══██╗██╔══██╗██╔═══██╗██║ ██╔╝
  ██████╔╝███████║██║  ███╗██╔██╗ ██║███████║██████╔╝██║   ██║█████╔╝
  ██╔══██╗██╔══██║██║   ██║██║╚██╗██║██╔══██║██╔══██╗██║   ██║██╔═██╗
  ██║  ██║██║  ██║╚██████╔╝██║ ╚████║██║  ██║██║  ██║╚██████╔╝██║  ██╗
  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
                           G  R  I  N  D
"""

TAGLINE_POOL = [
    "Productivity is the grind. The grind is everything.",
    "Every focus session is a monster slain.",
    "Your discipline is your character.",
    "The bar doesn't fill itself.",
    "Return to the grind. The EXP awaits.",
    "Rebirth is earned, never given.",
]


# ─────────────────────────────────────────────
#  SPLASH
# ─────────────────────────────────────────────

def show_splash() -> None:
    console.clear()
    console.print(BOOT_LOGO, style="bold bright_cyan")
    console.print(f"  {random.choice(TAGLINE_POOL)}\n", style="italic dim")
    console.print("  " + "─" * 68, style="dim")
    console.print()


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _exp_bar(progress: float, width: int = 32, color: str = "cyan") -> Text:
    filled = int(progress * width)
    bar = "█" * filled + "░" * (width - filled)
    pct = f"{int(progress * 100):3d}%"
    t = Text()
    t.append(bar, style=color)
    t.append(f" {pct}", style="dim")
    return t


def _tier_name(tier: int) -> str:
    return {0: "Novice", 1: "First Class", 2: "Second Class",
            3: "Transcendent", 4: "Third Class"}.get(tier, "Unknown")


# ─────────────────────────────────────────────
#  STATUS SCREEN
# ─────────────────────────────────────────────

def show_status(char: Character) -> None:
    console.clear()
    c = console

    cls         = char.class_data
    class_color = cls.get("color", "white")
    sprite      = cls.get("ascii_sprite", ["[o]", "???"])
    aura        = char.aura
    tier        = char.class_tier

    c.print()
    c.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
    c.print("  ║   CHARACTER STATUS                                    ║", style="bold")
    c.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
    c.print()

    if aura:
        c.print(f"  {aura}", style="bright_yellow")
    c.print(f"  {sprite[0]}", style=f"bold {class_color}")
    c.print(f"  {sprite[1]}", style=f"dim {class_color}")
    c.print()

    gender_icon = "♂" if char.gender == "male" else "♀"
    c.print(f"  Name:    [bold white]{char.name}[/]  [{class_color}]{gender_icon}[/]")
    c.print(f"  Class:   [bold {class_color}]{char.display_class}[/]")
    c.print(f"  Tier:    [dim]{_tier_name(tier)}[/]")

    if char.active_title:
        c.print(f"  Title:   [bright_magenta]⟨ {char.active_title} ⟩[/]")

    if char.rebirth_count > 0:
        stars = "★" * char.rebirth_count
        c.print(f"  Rebirths: [bold bright_yellow]{stars} ({char.rebirth_count}×)[/]")

    # Class path
    c.print()
    c.print("  ──── Class Path ─────────────────────────────────────", style="dim")
    path_str = char.class_path_display
    # Wrap long paths
    if len(path_str) > 54:
        parts = char.job_history
        mid   = len(parts) // 2
        line1 = " → ".join(parts[:mid])
        line2 = " → ".join(parts[mid:])
        c.print(f"  [dim]{line1}[/]")
        c.print(f"  [dim]  → {line2}[/]")
    else:
        c.print(f"  [dim]{path_str}[/]")

    c.print()
    c.print("  ──── Levels ─────────────────────────────────────────", style="dim")

    c.print(f"\n  Base Level  [bold cyan]{char.base_level:3d}[/] / {char.base_max}")
    base_bar = _exp_bar(char.base_exp_progress, 34, "bright_cyan")
    c.print(f"  EXP  ", end="")
    c.print(base_bar)
    c.print(f"       [dim]{char.base_exp:,}[/] / [dim]{char.base_exp_to_next:,}[/]")

    c.print(f"\n  Job  Level  [bold yellow]{char.job_level:3d}[/] / {char.job_max}")
    job_bar = _exp_bar(char.job_exp_progress, 34, "bright_yellow")
    c.print(f"  EXP  ", end="")
    c.print(job_bar)
    c.print(f"       [dim]{char.job_exp:,}[/] / [dim]{char.job_exp_to_next:,}[/]")

    if char.exp_bonus > 0:
        c.print(f"\n  [bright_yellow]+{int(char.exp_bonus * 100)}% EXP bonus (Rebirth)[/]")

    # Next step hint
    hint = char.next_advancement_hint
    if hint:
        c.print(f"\n  [bright_green]▶ {hint}[/]")

    c.print()
    c.print("  ──── Equipment ──────────────────────────────────────", style="dim")

    from data.items import EQUIPMENT_SLOTS, SLOT_DISPLAY, get_item
    from data.refinement import refine_display_name, get_atk_bonus, get_def_bonus

    any_equipped = False
    for slot in EQUIPMENT_SLOTS:
        item_id = char.equipment.get(slot)
        if not item_id:
            continue
        item = get_item(item_id)
        if not item:
            continue
        any_equipped = True
        refine_lvl = char.get_refine_level(item_id)
        display    = refine_display_name(item["name"], refine_lvl)
        rcolor     = _rarity_color(item["rarity"])
        bonus_str  = ""
        if refine_lvl > 0:
            if slot == "weapon":
                bonus_str = f"  [dim bright_green](+{get_atk_bonus(refine_lvl)} ATK)[/]"
            else:
                bonus_str = f"  [dim bright_green](+{get_def_bonus(refine_lvl)} DEF)[/]"
        c.print(f"  {SLOT_DISPLAY[slot]:<8} [{rcolor}]{display}[/]{bonus_str}")

    if not any_equipped:
        c.print("  [dim]No equipment.[/]")

    # Materials
    ori = char.get_material_count("Oridecon")
    elu = char.get_material_count("Elunium")
    if ori > 0 or elu > 0:
        c.print()
        parts = []
        if ori > 0:
            parts.append(f"[bright_cyan]Oridecon ×{ori}[/]")
        if elu > 0:
            parts.append(f"[bright_blue]Elunium ×{elu}[/]")
        c.print(f"  Materials: {' · '.join(parts)}")

    c.print()
    c.print("  ──── Grind Stats ────────────────────────────────────", style="dim")
    c.print(f"\n  Sessions:   [bold]{char.total_sessions}[/]")
    c.print(f"  Total Time: [bold]{char.total_minutes // 60}h {char.total_minutes % 60}m[/]")

    streak_style = "bold bright_yellow" if char.streak >= 7 else "white"
    c.print(f"  Streak:     [{streak_style}]{char.streak} day(s)[/]")

    if char.session_log:
        last = char.session_log[0]
        c.print(f"  Last:       [dim]{last['date']} — {last['minutes']}min[/]")

    c.print()
    c.print("  ──── Titles ─────────────────────────────────────────", style="dim")

    if char.titles:
        c.print()
        for title in char.titles[-10:]:
            rarity = TITLES.get(title, {}).get("rarity", "common")
            color  = RARITY_COLORS.get(rarity, "white")
            marker = "★" if rarity == "legendary" else "·"
            c.print(f"  {marker} [{color}]{title}[/]")
    else:
        c.print("\n  [dim]No titles yet. Complete sessions to earn them.[/]")

    c.print()
    if char.can_rebirth:
        c.print("  ╔══════════════════════════════════════════════════════╗", style="bright_magenta")
        c.print("  ║  ★ REBIRTH AVAILABLE — You are ready to be Reborn    ║", style="bold bright_magenta")
        c.print("  ╚══════════════════════════════════════════════════════╝", style="bright_magenta")
        c.print()

    if char.available_branches:
        c.print(f"  [bright_green]▶ Class change available! ({', '.join(char.available_branches)})[/]")
        c.print()


# ─────────────────────────────────────────────
#  ZONE SELECTION
# ─────────────────────────────────────────────

def show_zone_select(char: Character) -> tuple:
    available = get_available_zones(char.base_level, char.is_transcendent)

    console.clear()
    console.print()
    console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
    console.print("  ║   SELECT GRINDING ZONE                               ║", style="bold")
    console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
    console.print()

    zone_list = list(available.items())
    for i, (name, zone) in enumerate(zone_list, 1):
        color = zone.get("color", "white")
        mult  = zone.get("exp_multiplier", 1.0)
        rec   = zone.get("recommended_minutes", 20)
        min_l = zone.get("min_level", 1)
        atmo  = zone.get("atmosphere", "")
        trans = " [bright_magenta][TRANSCENDENT][/]" if zone.get("transcendent_only") else ""
        console.print(f"  [{i}] [{color}]{name}[/]{trans}")
        console.print(f"       EXP ×{mult:.1f}  |  Rec: {rec}min  |  Min Lv: {min_l}")
        console.print(f"       [dim italic]{atmo}[/]")
        console.print()

    console.print("  [0] ← Back to menu")
    console.print()

    try:
        choice = Prompt.ask("  Select zone", default="0")
        if choice == "0":
            return None, None
        idx = int(choice) - 1
        if not (0 <= idx < len(zone_list)):
            console.print("  [dim red]Invalid selection.[/]")
            return None, None
    except (ValueError, EOFError):
        return None, None

    zone_name, zone_data = zone_list[idx]
    zone_id = zone_data["id"]
    rec = zone_data.get("recommended_minutes", 25)

    console.print()
    console.print(f"  Zone: [bold]{zone_name}[/]")
    console.print(f"  Recommended session: {rec} minutes")
    console.print()
    console.print("  Common durations:")
    durations = [5, 10, 15, 20, 25, 30, 45, 60, 90]
    dur_str = "  " + "  ".join(f"[dim][{i+1}] {d}m[/]" for i, d in enumerate(durations))
    console.print(dur_str)
    console.print()

    try:
        dur_input = Prompt.ask("  Session duration (minutes)", default=str(rec))
        minutes = int(dur_input)
        if minutes < 1:
            console.print("  [dim red]Too short. Minimum 1 minute.[/]")
            return None, None
    except (ValueError, EOFError):
        return None, None

    console.print()
    console.print(f"  Entering [bold]{zone_name}[/] for [bold]{minutes} minutes[/].")
    console.print("  Clear your workspace. Close your distractions.")
    console.print("  This is the grind.")
    console.print()

    try:
        ok = Confirm.ask("  Begin session?", default=True)
    except EOFError:
        ok = True

    if not ok:
        return None, None
    return zone_id, minutes


# ─────────────────────────────────────────────
#  CLASS CHANGE SCREEN
# ─────────────────────────────────────────────

def show_class_change(char: Character) -> str | None:
    from core.progression import (
        get_available_advancements, get_advancement_requirement_text,
        can_advance_to,
    )

    branches = char.available_branches

    if not branches:
        from data.constants import get_class_tier
        tier = get_class_tier(char.char_class)

        console.clear()
        console.print()
        console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
        console.print("  ║   CLASS CHANGE                                       ║", style="bold bright_green")
        console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
        console.print()
        console.print(f"  Current path: [dim]{char.class_path_display}[/]")
        console.print(f"  Current class: [bold]{char.char_class}[/]  "
                      f"(Base Lv.{char.base_level} / Job Lv.{char.job_level})")
        console.print()

        # === REBIRTH IS THE NEXT STEP ===
        if char.can_rebirth:
            console.print("  ╔══════════════════════════════════════════════════════╗", style="bright_magenta")
            console.print("  ║  ★  REBIRTH IS YOUR NEXT STEP                        ║", style="bold bright_magenta")
            console.print("  ╚══════════════════════════════════════════════════════╝", style="bright_magenta")
            console.print()
            console.print("  You cannot advance to the next class directly from here.")
            console.print()
            console.print("  To reach Transcendent classes and eventually the Third Job,")
            console.print("  you must first perform [bold bright_magenta]Rebirth[/bold bright_magenta].")
            console.print()
            console.print("  ── The path forward: ───────────────────────────────────", style="dim")
            console.print(f"  {char.char_class} (current)")
            console.print(f"    ↓  [bright_magenta]Rebirth[/]  (press [T] from main menu)")
            console.print(f"  High Novice  →  High 1st Job  →  Transcendent 2nd Job")
            console.print(f"    →  [bold bright_yellow]3rd Job[/]")
            console.print()
            console.print("  [bright_magenta]Use [T] Rebirth from the main menu to proceed.[/]")

        # === LEVEL LOCKED (not ready yet) ===
        elif tier == 2 and char.rebirth_count == 0:
            req = {"base_level": 99, "job_level": 50}
            miss_base = max(0, req["base_level"] - char.base_level)
            miss_job  = max(0, req["job_level"]  - char.job_level)
            console.print("  [dim]You need Rebirth to advance further, but you're not ready yet.[/]")
            console.print()
            console.print("  ── Requirements for Rebirth: ───────────────────────────", style="dim")
            b_icon = "[bright_green]✓[/]" if miss_base == 0 else "[dim red]✗[/]"
            j_icon = "[bright_green]✓[/]" if miss_job  == 0 else "[dim red]✗[/]"
            console.print(f"  {b_icon} Base Level 99   "
                          f"(current: {char.base_level}"
                          f"{f', need {miss_base} more' if miss_base else ' ✓'})")
            console.print(f"  {j_icon} Job Level 50    "
                          f"(current: {char.job_level}"
                          f"{f', need {miss_job} more'  if miss_job  else ' ✓'})")
            console.print()
            console.print("  Keep grinding. The Rebirth awaits.")

        else:
            # Show what's coming and why it's locked
            locked = get_advancement_requirement_text(char.char_class, char.gender)
            if locked:
                console.print("  ── Next class options: ─────────────────────────────────", style="dim")
                console.print()
                for cls_name, req_text in locked:
                    check = can_advance_to(
                        cls_name, char.char_class,
                        char.base_level, char.job_level,
                        char.rebirth_count, char.gender,
                    )
                    lock_icon = "[bright_green]✓[/]" if check.eligible else "[dim red]✗[/]"
                    console.print(f"  {lock_icon} [bold]{cls_name}[/] — {req_text}")
                    if not check.eligible and check.reason:
                        console.print(f"      [dim]{check.reason}[/]")
            else:
                console.print("  [dim]No further advancement available from this class.[/]")
                console.print("  [dim]You may have reached the end of your path.[/]")

        console.print()
        input("  Press ENTER to return...\n")
        return None

    console.clear()
    console.print()
    console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
    console.print("  ║   CLASS CHANGE                                       ║", style="bold bright_green")
    console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
    console.print()

    # Show current path
    console.print(f"  Current path: [dim]{char.class_path_display}[/]")
    console.print(f"  Current class: [bold]{char.char_class}[/]  (Base Lv.{char.base_level}, Job Lv.{char.job_level})")
    console.print()
    console.print("  Your mastery has earned you a choice.")
    console.print("  Choose carefully — your path will define you.")
    console.print()

    for i, branch in enumerate(branches, 1):
        cls_data  = ALL_CLASSES.get(branch, {})
        color     = cls_data.get("color", "white")
        desc      = cls_data.get("description", "")
        aura_s    = cls_data.get("aura", "")
        sprite    = cls_data.get("ascii_sprite", ["[o]", "???"])
        tier      = cls_data.get("tier", 1)
        job_max   = cls_data.get("job_max", 50)
        gender_lk = cls_data.get("gender_lock")

        tier_str    = _tier_name(tier)
        gender_str  = f"  [dim][{'♂' if gender_lk == 'male' else '♀'}][/]" if gender_lk else ""

        console.print(f"  [{i}] [{color}]{branch}[/]{gender_str}  {aura_s}")
        console.print(f"       {sprite[0]}")
        console.print(f"       [dim]{tier_str}  |  Job Max: {job_max}[/]")
        console.print(f"       [italic dim]{desc}[/]")
        console.print()

    console.print("  [0] ← Cancel")
    console.print()

    try:
        choice = Prompt.ask("  Choose your path", default="0")
        if choice == "0":
            return None
        idx = int(choice) - 1
        if not (0 <= idx < len(branches)):
            console.print("  [red dim]Invalid choice.[/]")
            return None
    except (ValueError, EOFError):
        return None

    chosen   = branches[idx]
    cls_data = ALL_CLASSES.get(chosen, {})
    color    = cls_data.get("color", "white")

    console.print()
    console.print(f"  You have chosen: [{color}]{chosen}[/]")
    console.print(f"  [dim]{cls_data.get('description', '')}[/]")
    console.print()

    try:
        ok = Confirm.ask("  Confirm class change?", default=True)
    except EOFError:
        ok = True

    if not ok:
        return None

    # ── Advancement ceremony ─────────────────────────────────────────────────
    _play_advancement_ceremony(char.char_class, chosen)
    return chosen


def _play_advancement_ceremony(old_class: str, new_class: str) -> None:
    """Display a dramatic class advancement ceremony."""
    cls_data  = ALL_CLASSES.get(new_class, {})
    color     = cls_data.get("color", "white")
    tier      = cls_data.get("tier", 1)
    aura      = cls_data.get("aura", "")
    sprite    = cls_data.get("ascii_sprite", ["[◉]", ""])
    desc      = cls_data.get("description", "")

    from data.constants import CLASS_CHANGE_FLAVOR
    if tier >= 4:
        flavor_key = "third"
    else:
        flavor_key = "default"
    flavor = random.choice(CLASS_CHANGE_FLAVOR.get(flavor_key, [""]))

    console.clear()
    console.print()
    console.print("  " + "═" * 52, style=f"bold {color}")
    console.print()
    console.print("       ✦  CLASS CHANGE COMPLETE  ✦", style=f"bold {color}")
    console.print()
    console.print("  " + "═" * 52, style=f"bold {color}")
    console.print()
    console.print(f"       {old_class}", style="dim")
    console.print(f"           ↓", style="dim")
    console.print(f"       [{color}]{new_class}[/]", style="bold")
    console.print()

    if aura:
        console.print(f"       {aura}", style=f"bright_yellow")
    console.print(f"       {sprite[0]}", style=f"bold {color}")
    console.print(f"       {sprite[1]}", style=f"dim {color}")
    console.print()

    if flavor:
        console.print(f"  [italic dim]\"{flavor}\"[/]")
        console.print()

    console.print(f"  [dim]{desc}[/]")
    console.print()
    console.print("  [dim]Job Level has reset to 1. A new path begins.[/]")
    console.print()
    console.print("  " + "═" * 52, style=f"bold {color}")
    console.print()
    time.sleep(2.0)


# ─────────────────────────────────────────────
#  REBIRTH / TRANSCENDENCE SCREEN
# ─────────────────────────────────────────────

def show_transcendence(char: Character) -> bool:
    """Display the Rebirth ritual. Returns True if confirmed."""
    from core.progression import can_rebirth

    result = can_rebirth(char.char_class, char.base_level, char.job_level, char.rebirth_count)

    if not result.eligible:
        console.print()
        console.print(f"  [dim]Rebirth requires Base Lv.[cyan]{REBIRTH_REQ['base_level']}[/] "
                      f"and Job Lv.[yellow]{REBIRTH_REQ['job_level']}[/] "
                      f"at a Second Class.[/]")
        console.print(f"  Current: Base Lv.[cyan]{char.base_level}[/], "
                      f"Job Lv.[yellow]{char.job_level}[/], "
                      f"Class: [bold]{char.char_class}[/] ({_tier_name(char.class_tier)})")
        console.print()
        console.print(f"  [dim]{result.reason}[/]")
        console.print()
        return False

    console.clear()
    console.print()
    console.print("  " + "═" * 54, style="bright_magenta")
    console.print()
    console.print("         ★  R E B I R T H  ★", style="bold bright_magenta")
    console.print()
    console.print("  " + "═" * 54, style="bright_magenta")
    console.print()

    for line in REBIRTH_REQ["message"]:
        if line:
            console.print(f"  {line}", style="italic dim")
        else:
            console.print()

    console.print()
    console.print("  ── What you gain: ──────────────────────────────────", style="dim")

    count      = char.rebirth_count + 1
    bonus_info = TRANSCENDENCE_BONUSES.get(min(count, 3), {})
    bonus_pct  = int(bonus_info.get("exp_bonus", 0) * 100)

    console.print(f"\n  Class:       [dim]{char.char_class}[/] → [bold bright_magenta]High Novice[/]")
    console.print(f"  EXP Bonus:   [bold bright_yellow]+{bonus_pct}% permanent[/]")
    console.print(f"  Aura:        [bright_yellow]Upgraded[/]")
    console.print(f"  Title:       [bright_magenta]Reborn[/]")
    console.print(f"  Path:        Reborn path unlocked (High 1st → Transcendent 2nd → 3rd Job)")
    console.print()
    console.print("  ── What you lose: ──────────────────────────────────", style="dim")
    console.print(f"\n  Base Level: [cyan]{char.base_level}[/] → [dim]1[/]  (reset)")
    console.print(f"  Job  Level: [yellow]{char.job_level}[/] → [dim]1[/]  (reset)")
    console.print()
    console.print("  [dim]All titles, items, and grind history are preserved.[/]")
    console.print("  [dim]Current class path is preserved in your history.[/]")
    console.print()
    console.print("  " + "═" * 54, style="bright_magenta")
    console.print()

    try:
        ok = Confirm.ask(
            "  [bold bright_magenta]Will you be Reborn?[/]",
            default=False
        )
    except EOFError:
        ok = False

    return ok


def _play_rebirth_ceremony(char: Character) -> None:
    """Play the dramatic rebirth ceremony after confirmation."""
    console.clear()
    console.print()

    # Dramatic countdown
    for symbol in ["★", "★ ★", "★ ★ ★"]:
        console.print(f"\n          {symbol}", style="bold bright_magenta")
        time.sleep(0.4)

    console.clear()
    console.print()
    console.print("  " + "★" * 54, style="bright_magenta")
    console.print()
    console.print("              R E B O R N", style="bold bright_magenta")
    console.print()
    console.print("  " + "★" * 54, style="bright_magenta")
    console.print()
    console.print(f"  You have been reborn as: [bold bright_magenta]High Novice[/]")
    console.print(f"  Rebirth count: [bold bright_yellow]{'★' * char.rebirth_count}[/]")
    console.print()
    console.print("  Base Level reset to 1.")
    console.print("  Job Level reset to 1.")
    console.print(f"  EXP Bonus: [bold bright_yellow]+{int(char.exp_bonus * 100)}%[/] (permanent)")
    console.print()
    console.print("  The grind continues. But you are stronger now.", style="dim italic")
    console.print()
    console.print("  Advance to a High 1st job, then a Transcendent 2nd,", style="dim")
    console.print("  and finally — the Third Job awaits.", style="dim")
    console.print()
    time.sleep(2.5)
    input("  Press ENTER to continue...\n")


# ─────────────────────────────────────────────
#  TITLE SCREEN
# ─────────────────────────────────────────────

def show_title_select(char: Character) -> None:
    if not char.titles:
        console.print("\n  [dim]No titles earned yet.[/]\n")
        return

    console.clear()
    console.print()
    console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
    console.print("  ║   TITLES                                             ║", style="bold")
    console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
    console.print()
    console.print(f"  Active: [bright_magenta]⟨ {char.active_title or 'None'} ⟩[/]\n")

    for i, title in enumerate(char.titles, 1):
        rarity = TITLES.get(title, {}).get("rarity", "common")
        color  = RARITY_COLORS.get(rarity, "white")
        desc   = TITLES.get(title, {}).get("desc", "")
        active = " ◄" if title == char.active_title else ""
        console.print(f"  [{i:2d}] [{color}]{title}[/]{active}")
        console.print(f"        [dim]{desc}[/]")

    console.print("\n  [0] ← Back")
    console.print()

    try:
        choice = Prompt.ask("  Equip title #", default="0")
        if choice == "0":
            return
        idx = int(choice) - 1
        if 0 <= idx < len(char.titles):
            char.active_title = char.titles[idx]
            save_character(char)
            console.print(f"\n  [bright_magenta]Title set: ⟨ {char.active_title} ⟩[/]\n")
    except (ValueError, EOFError):
        pass


# ─────────────────────────────────────────────
#  SESSION HISTORY
# ─────────────────────────────────────────────

def show_session_history(char: Character) -> None:
    console.clear()
    console.print()
    console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
    console.print("  ║   GRIND HISTORY                                      ║", style="bold")
    console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
    console.print()

    if not char.session_log:
        console.print("  [dim]No sessions recorded yet. Enter the grind.[/]\n")
        return

    console.print(f"  {'Date':<17} {'Zone':<22} {'Dur':>5} {'Base':>7} {'Job':>7} {'Drops'}")
    console.print("  " + "─" * 65, style="dim")

    for s in char.session_log:
        zone_name = s.get("zone", "?")
        zone_display = next(
            (n for n, z in ZONES.items() if z["id"] == zone_name), zone_name
        )
        drops_str = ", ".join(s.get("drops", [])[:2]) or "—"
        console.print(
            f"  {s['date']:<17} {zone_display:<22} {s['minutes']:>4}m "
            f"[cyan]{s['base_exp']:>7,}[/] [yellow]{s['job_exp']:>7,}[/]  [dim]{drops_str}[/]"
        )

    console.print()
    console.print(
        f"  Total: [bold]{char.total_sessions}[/] sessions  |  "
        f"[bold]{char.total_minutes // 60}h {char.total_minutes % 60}m[/] grinded"
    )
    console.print()


# ─────────────────────────────────────────────
#  INVENTORY
# ─────────────────────────────────────────────

def show_inventory(char: Character) -> None:
    from data.constants import DROPS
    console.clear()
    console.print()
    console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
    console.print("  ║   INVENTORY  (Cosmetic Items)                        ║", style="bold")
    console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
    console.print()

    if not char.inventory:
        console.print("  [dim]Empty. Complete sessions to earn items.[/]\n")
        return

    for item in sorted(char.inventory):
        drop_data = DROPS.get(item, {})
        color     = drop_data.get("color", "white")
        desc      = drop_data.get("desc", "")
        rarity    = drop_data.get("rarity", 1.0)
        marker    = "★" if rarity <= 0.05 else ("◆" if rarity <= 0.2 else "·")
        console.print(f"  {marker} [{color}]{item:<20}[/]  [dim]{desc}[/]")

    console.print(f"\n  {len(char.inventory)} item(s) collected.\n")


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

def show_main_menu(char: Character) -> str:
    console.clear()
    c = console

    c.print()
    c.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
    c.print("  ║  RAGNAROK GRIND                                      ║", style=TITLE_STYLE)
    c.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
    c.print()

    cls   = char.class_data
    color = cls.get("color", "white")
    aura  = char.aura

    aura_str = f"{aura} " if aura else ""
    gender_icon = "♂" if char.gender == "male" else "♀"
    c.print(f"  {aura_str}[bold white]{char.name}[/] [{color}]{gender_icon}[/]  ·  [{color}]{char.display_class}[/]")

    if char.active_title:
        c.print(f"  [dim bright_magenta]⟨ {char.active_title} ⟩[/]")

    c.print(
        f"  Base Lv.[cyan]{char.base_level}[/] ({int(char.base_exp_progress * 100)}%)  "
        f"Job Lv.[yellow]{char.job_level}[/] ({int(char.job_exp_progress * 100)}%)  "
        f"Streak:[bright_yellow]{char.streak}d[/]"
    )

    if char.rebirth_count > 0:
        c.print(f"  [dim bright_magenta]Rebirths: {'★' * char.rebirth_count}[/]")

    c.print()
    c.print("  " + "─" * 50, style="dim")
    c.print()

    menu_items = [
        ("G", "Grind — Enter a Zone (Focus Session)", "bright_green"),
        ("S", "Status — View Character Sheet",         "cyan"),
        ("C", "Class — Change / Advance Class",        "bright_blue"),
        ("T", "Rebirth — Transcendence System",        "bright_magenta"),
        ("W", "Equipment — Gear & NPC Shop",           "bright_yellow"),
        ("R", "Refine — Weapon & Armor Refinement",    "bright_cyan"),
        ("H", "History — Session Log",                 "dim"),
        ("I", "Drops — Cosmetic Item Collection",      "dim"),
        ("E", "Equip Title",                           "bright_magenta"),
        ("Q", "Quit",                                  "dim red"),
    ]

    for key, label, color_s in menu_items:
        marker = ""
        if key == "C" and char.available_branches:
            marker = "  [bright_green]▶ AVAILABLE[/]"
        elif key == "T" and char.can_rebirth:
            marker = "  [bright_magenta]★ READY[/]"
        c.print(f"  [bold {color_s}][{key}][/]  {label}{marker}")

    c.print()
    c.print(f"  [dim]Zeny: [bright_yellow]{char.zeny:,}z[/][/]")

    ori = char.get_material_count("Oridecon")
    elu = char.get_material_count("Elunium")
    if ori > 0 or elu > 0:
        parts = []
        if ori > 0:
            parts.append(f"[bright_cyan]Oridecon ×{ori}[/]")
        if elu > 0:
            parts.append(f"[bright_blue]Elunium ×{elu}[/]")
        c.print(f"  [dim]Materials: {' · '.join(parts)}[/]")
    c.print()

    try:
        choice = Prompt.ask("  Command", default="G").strip().upper()
    except EOFError:
        choice = "Q"

    return choice


# ─────────────────────────────────────────────
#  CHARACTER CREATION
# ─────────────────────────────────────────────

def show_character_creation() -> tuple | None:
    """
    New character creation screen.
    Returns (name, gender) tuple, or None if cancelled.
    """
    console.clear()
    console.print()
    console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
    console.print("  ║   NEW CHARACTER                                      ║", style="bold bright_green")
    console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
    console.print()
    console.print("  You begin as a Novice.")
    console.print("  Through real-world focus sessions, you will grow.")
    console.print("  Every minute of discipline earns EXP.")
    console.print("  Your class will emerge from your choices.")
    console.print()
    console.print("  [dim]Note: Gender affects Bard/Dancer and Clown/Gypsy class paths.[/]")
    console.print()
    console.print("  ─────────────────────────────────────────────────────", style="dim")
    console.print()

    try:
        name = Prompt.ask("  Enter your name (adventurer)").strip()
    except EOFError:
        return None

    if not name or len(name) > 24:
        console.print("  [red]Invalid name (1–24 characters).[/]")
        return None

    console.print()
    console.print("  ── Choose your gender: ─────────────────────────────", style="dim")
    console.print("  [1] [blue]♂ Male[/]   — Unlocks: Bard → Clown → Maestro")
    console.print("  [2] [bright_magenta]♀ Female[/] — Unlocks: Dancer → Gypsy → Wanderer")
    console.print()

    try:
        g_choice = Prompt.ask("  Gender", choices=["1", "2"], default="1")
    except EOFError:
        g_choice = "1"

    gender      = "male" if g_choice == "1" else "female"
    gender_str  = "♂ Male" if gender == "male" else "♀ Female"
    gender_color = "blue" if gender == "male" else "bright_magenta"

    console.print()
    console.print(f"  Welcome, [bold white]{name}[/] the [{gender_color}]{gender_str}[/].")
    console.print(f"  Your journey begins as a [dim]Novice[/].")
    console.print(f"  The grind awaits.")
    console.print()

    try:
        ok = Confirm.ask("  Begin?", default=True)
    except EOFError:
        ok = True

    return (name, gender) if ok else None


# ─────────────────────────────────────────────
#  CHARACTER SELECT
# ─────────────────────────────────────────────

def show_character_select(characters: list) -> str | None:
    console.clear()
    console.print()
    console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
    console.print("  ║   SELECT CHARACTER                                   ║", style=TITLE_STYLE)
    console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
    console.print()

    for i, char in enumerate(characters, 1):
        gender_icon = "♂" if char.get("gender", "male") == "male" else "♀"
        console.print(
            f"  [{i}] [bold]{char['name']}[/] [{gender_icon}]  —  "
            f"{char['class']}  (Base Lv. {char['base_level']})"
        )
        console.print(f"       [dim]Last: {char['updated_at']}[/]")
        console.print()

    console.print("  [N] New Character")
    console.print("  [Q] Quit")
    console.print()

    try:
        choice = Prompt.ask("  Select", default="1").strip().upper()
    except EOFError:
        return None

    if choice == "Q":
        return None
    if choice == "N":
        return "new"

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(characters):
            return characters[idx]["name"]
    except ValueError:
        pass

    return None


# ─────────────────────────────────────────────
#  EQUIPMENT SCREEN
# ─────────────────────────────────────────────

def show_equipment(char: "Character") -> None:
    """
    Main equipment management screen.
    Shows current equipped gear, item inventory, and Zeny.
    Player can equip, unequip, or go to NPC sell screen.
    """
    from data.items import EQUIPMENT_SLOTS, SLOT_DISPLAY, get_item, can_equip, ITEM_DB

    while True:
        console.clear()
        console.print()
        console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
        console.print("  ║   EQUIPMENT                                          ║", style="bold bright_yellow")
        console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
        console.print()

        # ── Equipped gear panel ──────────────────────────────────────────────
        console.print("  ── Equipped ────────────────────────────────────────────", style="dim")
        console.print()
        for slot in EQUIPMENT_SLOTS:
            label    = SLOT_DISPLAY[slot]
            item_id  = char.equipment.get(slot)
            item     = get_item(item_id) if item_id else None
            if item:
                refine_lvl = char.get_refine_level(item_id)
                refine_pfx = f"[bold bright_cyan]+{refine_lvl}[/] " if refine_lvl > 0 else ""
                two_h  = " [dim][2H][/]" if item.get("two_handed") else ""
                rcolor = _rarity_color(item["rarity"])
                console.print(f"  {label:<8} {refine_pfx}[{rcolor}]{item['name']}[/]{two_h}")
            else:
                console.print(f"  {label:<8} [dim]—[/]")

        console.print()
        console.print(f"  Zeny: [bold bright_yellow]{char.zeny:,}z[/]")
        console.print()

        # ── Item inventory panel ──────────────────────────────────────────────
        console.print("  ── Inventory ───────────────────────────────────────────", style="dim")
        console.print()

        inv_items = [(idx, iid) for idx, iid in enumerate(char.item_inventory)]
        if not inv_items:
            console.print("  [dim]Empty — no items in bag.[/]")
        else:
            for idx, item_id in inv_items:
                item   = get_item(item_id)
                if not item:
                    console.print(f"  [{idx + 1:2d}] [dim]{item_id}[/]")
                    continue
                rcolor = _rarity_color(item["rarity"])
                two_h  = " [dim][2H][/]" if item.get("two_handed") else ""
                check  = can_equip(item, char.char_class, char.equipment)
                eq_ok  = "[bright_green]✓[/]" if check.ok else "[dim red]✗[/]"
                console.print(
                    f"  [{idx + 1:2d}] {eq_ok} [{rcolor}]{item['name']:<22}[/]"
                    f"  {item['category']:<7}  {item['sell_price']:>7,}z{two_h}"
                )

        console.print()
        console.print("  ── Actions ─────────────────────────────────────────────", style="dim")
        console.print("  [E] Equip item      [U] Unequip slot")
        console.print("  [R] Refine          [S] Sell to NPC     [0] Back to menu")
        console.print()

        try:
            choice = Prompt.ask("  Action", default="0").strip().upper()
        except EOFError:
            break

        if choice == "0":
            break

        elif choice == "E":
            _do_equip(char)

        elif choice == "U":
            _do_unequip(char)

        elif choice == "R":
            show_refine_screen(char)

        elif choice == "S":
            show_npc_sell(char)

        else:
            console.print("  [dim]Unknown action.[/]")
            time.sleep(0.5)


def _rarity_color(rarity: str) -> str:
    return {
        "common":    "white",
        "uncommon":  "bright_green",
        "rare":      "bright_cyan",
        "legendary": "bright_yellow",
    }.get(rarity, "white")


def _do_equip(char: "Character") -> None:
    if not char.item_inventory:
        console.print("\n  [dim]Nothing in inventory to equip.[/]")
        time.sleep(1)
        return
    console.print()
    try:
        raw = Prompt.ask("  Equip item # (or 0 to cancel)", default="0")
        if raw == "0":
            return
        idx = int(raw) - 1
        if not (0 <= idx < len(char.item_inventory)):
            console.print("  [red]Invalid number.[/]")
            time.sleep(0.8)
            return
    except (ValueError, EOFError):
        return

    item_id = char.item_inventory[idx]
    success, msg = char.equip_item(item_id)

    if success:
        console.print(f"\n  [bright_green]{msg}[/]")
    else:
        # Format multi-line reason nicely
        lines = msg.split("\n")
        console.print()
        console.print("  ╔══════════════════════════════════════════╗", style="dim red")
        for line in lines:
            console.print(f"  [dim red]{line}[/]")
        console.print("  ╚══════════════════════════════════════════╝", style="dim red")

    from core.character import save_character
    save_character(char)
    time.sleep(1.2)


def _do_unequip(char: "Character") -> None:
    from data.items import EQUIPMENT_SLOTS, SLOT_DISPLAY
    console.print()
    for i, slot in enumerate(EQUIPMENT_SLOTS, 1):
        item = char.equipped_item(slot)
        label = SLOT_DISPLAY[slot]
        name  = item["name"] if item else "—"
        console.print(f"  [{i}] {label:<8} {name}")
    console.print("  [0] Cancel")
    console.print()
    try:
        raw = Prompt.ask("  Unequip slot #", default="0")
        if raw == "0":
            return
        idx = int(raw) - 1
        if not (0 <= idx < len(EQUIPMENT_SLOTS)):
            return
        slot = EQUIPMENT_SLOTS[idx]
    except (ValueError, EOFError):
        return

    success, msg = char.unequip_slot(slot)
    color = "bright_green" if success else "dim red"
    console.print(f"\n  [{color}]{msg}[/]")
    from core.character import save_character
    save_character(char)
    time.sleep(1)


# ─────────────────────────────────────────────
#  NPC SELL SCREEN
# ─────────────────────────────────────────────

def show_npc_sell(char: "Character") -> None:
    """NPC item shop — sell items for exact Zeny prices."""
    from data.items import get_item

    while True:
        console.clear()
        console.print()
        console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
        console.print("  ║   NPC SHOP — SELL ITEMS                              ║", style="bold")
        console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
        console.print()
        console.print(f"  Your Zeny: [bold bright_yellow]{char.zeny:,}z[/]")
        console.print()

        if not char.item_inventory:
            console.print("  [dim]Nothing to sell. Your bag is empty.[/]")
            console.print()
            input("  Press ENTER to return...\n")
            return

        console.print("  ── Items for sale: ─────────────────────────────────────", style="dim")
        console.print()
        for idx, item_id in enumerate(char.item_inventory):
            item = get_item(item_id)
            if not item:
                console.print(f"  [{idx + 1:2d}] [dim]{item_id}[/]")
                continue
            rcolor = _rarity_color(item["rarity"])
            console.print(
                f"  [{idx + 1:2d}] [{rcolor}]{item['name']:<24}[/]  "
                f"→  [bright_yellow]{item['sell_price']:>8,}z[/]"
            )

        console.print()
        console.print("  [A] Sell ALL items    [0] Done")
        console.print()

        try:
            raw = Prompt.ask("  Sell item # (or A / 0)", default="0").strip().upper()
        except EOFError:
            break

        if raw == "0":
            break

        elif raw == "A":
            _sell_all(char)

        else:
            try:
                idx = int(raw) - 1
                if not (0 <= idx < len(char.item_inventory)):
                    console.print("  [red]Invalid number.[/]")
                    time.sleep(0.7)
                    continue
                item_id = char.item_inventory[idx]
                success, gained, msg = char.sell_item(item_id)
                color = "bright_yellow" if success else "dim red"
                console.print(f"\n  [{color}]{msg}[/]")
                from core.character import save_character
                save_character(char)
                time.sleep(0.8)
            except (ValueError, EOFError):
                pass


def _sell_all(char: "Character") -> None:
    """Sell every item in inventory."""
    from core.character import save_character
    if not char.item_inventory:
        return

    try:
        ok = Confirm.ask("  Sell ALL items in inventory?", default=False)
    except EOFError:
        ok = False
    if not ok:
        return

    total = 0
    sold  = []
    # iterate over a copy since sell_item mutates the list
    for item_id in list(char.item_inventory):
        success, gained, msg = char.sell_item(item_id)
        if success:
            total += gained
            sold.append(msg)

    console.print()
    for m in sold:
        console.print(f"  [dim]{m}[/]")
    console.print()
    console.print(f"  [bright_yellow]Total received: {total:,}z[/]")
    console.print(f"  [bright_yellow]Wallet: {char.zeny:,}z[/]")
    save_character(char)
    time.sleep(1.5)


# ─────────────────────────────────────────────
#  REFINEMENT SCREEN
# ─────────────────────────────────────────────

def show_refine_screen(char: "Character") -> None:
    """
    Main refinement screen.
    Players can refine equipped weapons and armor using Oridecon / Elunium.
    """
    from data.items import EQUIPMENT_SLOTS, SLOT_DISPLAY, get_item
    from data.refinement import (
        get_material_for_slot, get_refine_rate,
        can_refine, attempt_refine,
        refine_display_name, REFINE_MAX, MATERIAL_COST,
    )
    from core.character import save_character

    while True:
        console.clear()
        console.print()
        console.print("  ╔══════════════════════════════════════════════════════╗", style=BORDER)
        console.print("  ║   REFINEMENT                                         ║", style="bold bright_cyan")
        console.print("  ╚══════════════════════════════════════════════════════╝", style=BORDER)
        console.print()
        console.print("  [dim]Strengthen your equipment. Each attempt consumes materials.[/]")
        console.print("  [dim]Higher levels carry risk. The heart of Ragnarok refinement.[/]")
        console.print()

        # ── Materials panel ──────────────────────────────────────────────────
        ori = char.get_material_count("Oridecon")
        elu = char.get_material_count("Elunium")
        console.print("  ── Materials ───────────────────────────────────────────", style="dim")
        console.print(f"  [bright_cyan]Oridecon[/]  ×{ori:<4}  [dim](weapon refinement)[/]")
        console.print(f"  [bright_blue]Elunium[/]   ×{elu:<4}  [dim](armor refinement)[/]")
        console.print()

        # ── Refineable equipment panel ───────────────────────────────────────
        console.print("  ── Equipped Items ──────────────────────────────────────", style="dim")
        console.print()

        refine_options: list[tuple[int, str, dict, int]] = []  # (num, slot, item, refine_lvl)
        num = 0

        for slot in EQUIPMENT_SLOTS:
            item_id = char.equipment.get(slot)
            if not item_id:
                continue
            item = get_item(item_id)
            if not item:
                continue

            refine_lvl = char.get_refine_level(item_id)
            material   = get_material_for_slot(slot)
            refineable = item.get("refineable", False)
            rcolor     = _rarity_color(item["rarity"])

            display = refine_display_name(item["name"], refine_lvl)

            if not refineable:
                console.print(
                    f"  [dim]  —  {SLOT_DISPLAY[slot]:<8} {display:<28} (cannot refine)[/]"
                )
                continue

            if refine_lvl >= REFINE_MAX:
                cap_color = "bright_yellow"
                console.print(
                    f"  [dim]  —  {SLOT_DISPLAY[slot]:<8}[/] "
                    f"[{cap_color}]{display:<28}[/] [dim](MAX +{REFINE_MAX})[/]"
                )
                continue

            num += 1
            refine_options.append((num, slot, item, refine_lvl))

            target  = refine_lvl + 1
            rate    = get_refine_rate(target)
            mat_qty = char.get_material_count(material)
            has_mat = mat_qty >= MATERIAL_COST

            rate_str   = f"{int(rate * 100)}%"
            rate_color = (
                "bright_green"  if rate >= 0.75 else
                "bright_yellow" if rate >= 0.45 else
                "bright_red"
            )
            mat_color  = "bright_cyan" if material == "Oridecon" else "bright_blue"
            avail      = "" if has_mat else " [dim red](no materials)[/]"

            console.print(
                f"  [{num:2d}]  {SLOT_DISPLAY[slot]:<8} "
                f"[{rcolor}]{display:<28}[/]  "
                f"+{refine_lvl}→+{target}  "
                f"[{rate_color}]{rate_str}[/]  "
                f"[{mat_color}]{material} ×{MATERIAL_COST}[/]"
                f"{avail}"
            )

        if not refine_options:
            console.print("  [dim]No refineable items equipped.[/]")
            console.print()
            console.print("  Equip refineable items to use the refinery.")
            console.print()
            console.print("  [0] Back", style="dim")
            console.print()
            try:
                Prompt.ask("  Command", default="0")
            except EOFError:
                pass
            return

        console.print()
        console.print("  ── Controls ────────────────────────────────────────────", style="dim")
        console.print("  Enter item # to attempt refinement.  [0] Back to menu.")
        console.print()

        try:
            raw = Prompt.ask("  Select item to refine", default="0").strip()
        except EOFError:
            break

        if raw == "0":
            break

        try:
            choice_num = int(raw)
        except ValueError:
            console.print("  [dim red]Invalid input.[/]")
            time.sleep(0.6)
            continue

        match = next((o for o in refine_options if o[0] == choice_num), None)
        if not match:
            console.print("  [dim red]Invalid selection.[/]")
            time.sleep(0.6)
            continue

        _, slot, item, refine_lvl = match
        item_id  = char.equipment[slot]
        material = get_material_for_slot(slot)
        target   = refine_lvl + 1
        rate     = get_refine_rate(target)
        display  = refine_display_name(item["name"], refine_lvl)
        mat_qty  = char.get_material_count(material)
        mat_color = "bright_cyan" if material == "Oridecon" else "bright_blue"

        # ── Confirmation panel ───────────────────────────────────────────────
        console.print()
        console.print("  ╔══════════════════════════════════════════╗", style="dim bright_cyan")
        console.print("  ║   REFINE EQUIPMENT                       ║", style="bold bright_cyan")
        console.print("  ╚══════════════════════════════════════════╝", style="dim bright_cyan")
        console.print()
        console.print(f"  Selected:     [{_rarity_color(item['rarity'])}]{display}[/]")
        console.print(f"  Refining to:  +{target}")
        console.print(f"  Required:     [{mat_color}]{material} ×{MATERIAL_COST}[/]  (you have: {mat_qty})")

        rate_color = (
            "bright_green"  if rate >= 0.75 else
            "bright_yellow" if rate >= 0.45 else
            "bright_red"
        )
        console.print(f"  Success Rate: [{rate_color}]{int(rate * 100)}%[/]")

        if rate < 1.0:
            console.print()
            console.print("  [dim]Failure consumes materials. Item is NOT destroyed.[/]")

        console.print()

        try:
            ok = Confirm.ask("  Proceed?", default=False)
        except EOFError:
            ok = False

        if not ok:
            continue

        # ── Attempt ──────────────────────────────────────────────────────────
        result, error = attempt_refine(
            item, slot, refine_lvl, char.materials
        )

        if error:
            console.print(f"\n  [dim red]{error}[/]")
            time.sleep(1.2)
            continue

        # Apply new refine level
        if result.success:
            char.set_refine_level(item_id, result.new_level)

        # Save
        save_character(char)

        # ── Result display ────────────────────────────────────────────────────
        console.print()

        if result.success:
            new_display = refine_display_name(item["name"], result.new_level)
            console.print("  ╔══════════════════════════════════════════╗", style="bright_green")
            console.print("  ║            SUCCESS!                      ║", style="bold bright_green")
            console.print("  ╚══════════════════════════════════════════╝", style="bright_green")
            console.print()
            console.print(f"  [{_rarity_color(item['rarity'])}]{item['name']}[/]")
            console.print(
                f"  [dim]+{result.old_level}[/]  →  "
                f"[bold bright_green]+{result.new_level}[/]"
            )
            console.print()

            # Show bonus granted
            if slot == "weapon":
                from data.refinement import get_atk_bonus
                console.print(
                    f"  [dim]Total ATK Bonus: +{get_atk_bonus(result.new_level)}[/]"
                )
            else:
                from data.refinement import get_def_bonus
                console.print(
                    f"  [dim]Total DEF Bonus: +{get_def_bonus(result.new_level)}[/]"
                )

        else:
            console.print("  ╔══════════════════════════════════════════╗", style="dim red")
            console.print("  ║         Refinement Failed.               ║", style="bold dim red")
            console.print("  ╚══════════════════════════════════════════╝", style="dim red")
            console.print()
            console.print(f"  [dim]Materials consumed. Refinement unchanged.[/]")
            console.print(f"  [dim]{display} remains at +{result.old_level}.[/]")

        console.print()
        remaining_mat = char.get_material_count(material)
        mat_color     = "bright_cyan" if material == "Oridecon" else "bright_blue"
        console.print(f"  [{mat_color}]{material}[/] remaining: {remaining_mat}")
        console.print()

        try:
            input("  Press ENTER to continue...\n")
        except EOFError:
            pass
