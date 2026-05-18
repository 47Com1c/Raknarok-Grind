"""
RAGNAROK GRIND — Focus Session Engine
Stable Non-Flicker Version
"""

import sys
import time
import tty
import termios
import select
import random
import shutil
import threading

from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live

from data.constants import (
    get_session_exp,
    roll_drops,
    roll_material_drops,
    roll_equip_drop,
    roll_zeny_drop,
    ZONES,
    SESSION_START_MSGS,
)

from core.character import Character, save_character


# ─────────────────────────────────────────────
#  CONSOLE
# ─────────────────────────────────────────────

console = Console(force_terminal=True)


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────

class SessionState:

    def __init__(
        self,
        char: Character,
        zone_id: str,
        duration_minutes: int
    ):

        self.char = char
        self.zone_id = zone_id

        self.zone = next(
            (
                z for z in ZONES.values()
                if z["id"] == zone_id
            ),
            None
        )

        self.zone_name = next(
            (
                n for n, z in ZONES.items()
                if z["id"] == zone_id
            ),
            "Unknown Zone"
        )

        self.duration_seconds = duration_minutes * 60

        self.start_time = time.time()

        self.paused = False
        self.pause_start = None
        self.paused_total = 0

        self.cancelled = False
        self.finished = False

        self.combat_log = []
        self.monster_kills = 0

    @property
    def elapsed_real(self):

        if self.paused and self.pause_start:

            return (
                self.pause_start
                - self.start_time
                - self.paused_total
            )

        return (
            time.time()
            - self.start_time
            - self.paused_total
        )

    @property
    def remaining(self):

        return max(
            0,
            self.duration_seconds
            - self.elapsed_real
        )

    @property
    def progress(self):

        return min(
            1.0,
            self.elapsed_real
            / self.duration_seconds
        )

    def toggle_pause(self):

        if self.paused:

            self.paused_total += (
                time.time()
                - self.pause_start
            )

            self.pause_start = None

            self.paused = False

            self.add_log(
                ">> Resumed. Focus restored."
            )

        else:

            self.pause_start = time.time()

            self.paused = True

            self.add_log(
                "|| Paused. Session on hold."
            )

    def add_log(self, msg: str):

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        self.combat_log.append(
            f"[{timestamp}] {msg}"
        )

        if len(self.combat_log) > 12:
            self.combat_log.pop(0)

    def tick_combat(self):

        if not self.zone:
            return

        monsters = self.zone.get(
            "monsters",
            ["Unknown Monster"]
        )

        monster = random.choice(monsters)

        kills = random.randint(3, 12)

        self.monster_kills += kills

        messages = [

            f"Defeated {kills}x {monster}.",

            f"{monster} approaches. "
            f"Repelled by your focus.",

            f"EXP trickles in from "
            f"{kills} {monster}s.",

            f"Zone densely packed "
            f"with {monster}s.",

            f"Your concentration "
            f"deals massive damage.",

            f"{kills} {monster}s "
            f"fall before your will.",
        ]

        self.add_log(
            random.choice(messages)
        )


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def _fmt_time(seconds: float):

    s = int(seconds)

    m, s = divmod(s, 60)

    h, m = divmod(m, 60)

    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"

    return f"{m:02d}:{s:02d}"


def _bar(
    val: float,
    width: int = 30,
    filled: str = "■",
    empty: str = "·"
):

    filled_count = int(val * width)

    empty_count = width - filled_count

    return (
        filled * filled_count
        + empty * empty_count
    )


# ─────────────────────────────────────────────
#  DRAW
# ─────────────────────────────────────────────

def _draw(state: SessionState):

    char = state.char

    zone = state.zone or {}

    width = min(
        shutil.get_terminal_size().columns,
        100
    )

    progress_bar = _bar(state.progress)

    base_bar = _bar(
        char.base_exp_progress
    )

    job_bar = _bar(
        char.job_exp_progress
    )

    status = "[bold green]GRINDING[/]"

    if state.paused:
        status = "[bold yellow]PAUSED[/]"

    table = Table.grid(expand=True)

    table.add_column(justify="left")

    # HEADER

    table.add_row(
        f"[bold bright_yellow]"
        f"RAGNAROK GRIND[/] "
        f"| [green]{state.zone_name}[/]"
    )

    atmosphere = zone.get(
        "atmosphere",
        ""
    )

    if atmosphere:

        table.add_row(
            f"[dim]{atmosphere}[/]"
        )

    table.add_row("")

    # SESSION

    table.add_row(
        f"{status}   "
        f"Elapsed: "
        f"[bold]{_fmt_time(state.elapsed_real)}[/]   "
        f"Remaining: "
        f"[bold]{_fmt_time(state.remaining)}[/]"
    )

    table.add_row(
        f"Progress "
        f"[cyan]{progress_bar}[/] "
        f"{int(state.progress * 100)}%"
    )

    table.add_row("")

    # CHARACTER

    table.add_row(
        f"[bold]{char.name}[/] "
        f"| [bright_cyan]"
        f"{char.display_class}[/]"
    )

    table.add_row(
        f"Base Lv.{char.base_level:<3} "
        f"[cyan]{base_bar}[/] "
        f"{int(char.base_exp_progress * 100)}%"
    )

    table.add_row(
        f"Job  Lv.{char.job_level:<3} "
        f"[yellow]{job_bar}[/] "
        f"{int(char.job_exp_progress * 100)}%"
    )

    if char.active_title:

        table.add_row(
            f"[bright_magenta]"
            f"Title: {char.active_title}"
            f"[/]"
        )

    table.add_row("")

    # COMBAT LOG

    table.add_row("[dim]Combat Log[/]")

    logs = state.combat_log[-5:]

    while len(logs) < 5:
        logs.append("")

    for log in logs:

        trimmed = log[: width - 15]

        table.add_row(
            f"[green]{trimmed}[/]"
        )

    table.add_row("")

    table.add_row(
        "[dim][P][/dim] Pause/Resume    "
        "[dim][Q][/dim] Abandon"
    )

    panel = Panel(
        table,
        border_style="dim",
        padding=(1, 2),
        width=width,
    )

    return Align.center(panel)


# ─────────────────────────────────────────────
#  SESSION RUNNER
# ─────────────────────────────────────────────

def run_session(
    char: Character,
    zone_id: str,
    duration_minutes: int,
    on_complete=None
):

    state = SessionState(
        char,
        zone_id,
        duration_minutes
    )

    state.add_log(
        random.choice(
            SESSION_START_MSGS
        )
    )

    state.add_log(
        f"Target: "
        f"{duration_minutes} minutes "
        f"in {state.zone_name}."
    )

    stop_event = threading.Event()

    # COMBAT THREAD

    def _combat_ticker():

        while not stop_event.is_set():

            time.sleep(
                random.uniform(25, 45)
            )

            if (
                not state.paused
                and not state.finished
                and not state.cancelled
            ):
                state.tick_combat()

    combat_thread = threading.Thread(
        target=_combat_ticker,
        daemon=True
    )

    combat_thread.start()

    # INPUT THREAD

    def _input_listener():

        if not sys.stdin.isatty():
            return

        old = termios.tcgetattr(
            sys.stdin
        )

        try:

            tty.setraw(
                sys.stdin.fileno()
            )

            while (
                not state.finished
                and not state.cancelled
            ):

                ready, _, _ = select.select(
                    [sys.stdin],
                    [],
                    [],
                    0.1
                )

                if ready:

                    ch = sys.stdin.read(1).lower()

                    if ch == "p":

                        state.toggle_pause()

                    elif ch == "q":

                        state.cancelled = True
                        break

        except Exception:
            pass

        finally:

            try:

                termios.tcsetattr(
                    sys.stdin,
                    termios.TCSADRAIN,
                    old
                )

            except Exception:
                pass

    input_thread = threading.Thread(
        target=_input_listener,
        daemon=True
    )

    input_thread.start()

    # LIVE UI

    try:

        with Live(
            _draw(state),
            refresh_per_second=20,
            transient=False,
            auto_refresh=True,
        ) as live:

            while not state.cancelled:

                live.update(
                    _draw(state)
                )

                if state.remaining <= 0:

                    state.finished = True
                    break

                time.sleep(0.05)

    except KeyboardInterrupt:

        state.cancelled = True

    stop_event.set()

    # CANCELLED

    if state.cancelled:

        console.print()

        console.print(
            "[bold yellow]"
            "Session abandoned. "
            "No EXP awarded."
            "[/]"
        )

        console.print()

        return None

    # RESULTS

    actual_minutes = max(
        int(state.elapsed_real / 60),
        1
    )

    zone_mult = (

        state.zone.get(
            "exp_multiplier",
            1.0
        )

        if state.zone
        else 1.0
    )

    exp_result = get_session_exp(
        actual_minutes,
        zone_mult,
        char.is_transcendent
    )

    drops = roll_drops(zone_id, actual_minutes)
    material_drops = roll_material_drops(zone_id, actual_minutes)
    equip_drop = roll_equip_drop(zone_id, actual_minutes)
    zeny_earned = roll_zeny_drop(zone_id, actual_minutes)

    char.record_session(
        actual_minutes, zone_id,
        exp_result["base_exp"], exp_result["job_exp"], drops
    )

    for item in drops:
        if item not in char.inventory:
            char.inventory.append(item)

    # Refinement materials
    for mat, qty in material_drops.items():
        char.add_material(mat, qty)

    # Equipment drop → item_inventory
    if equip_drop:
        char.item_inventory.append(equip_drop)

    # Zeny from monsters
    if zeny_earned > 0:
        char.zeny += zeny_earned

    events = char.add_exp(
        exp_result["base_exp"],
        exp_result["job_exp"]
    )

    save_character(char)

    return {
        "base_exp":       exp_result["base_exp"],
        "job_exp":        exp_result["job_exp"],
        "minutes":        actual_minutes,
        "drops":          drops,
        "material_drops": material_drops,
        "equip_drop":     equip_drop,
        "zeny_earned":    zeny_earned,
        "base_levels":    events["base_levels_gained"],
        "job_levels":     events["job_levels_gained"],
        "monster_kills":  state.monster_kills,
        "zone_name":      state.zone_name,
    }


# ─────────────────────────────────────────────
#  RESULTS SCREEN
# ─────────────────────────────────────────────

def display_session_results(
    result: dict,
    char: Character
):

    console.print()

    console.print(
        "╔══════════════════════════════════════╗",
        style="dim"
    )

    console.print(
        "║      SESSION COMPLETE — RESULTS     ║",
        style="bold bright_yellow"
    )

    console.print(
        "╚══════════════════════════════════════╝",
        style="dim"
    )

    console.print()

    console.print(
        f"Zone: "
        f"[bold]{result['zone_name']}[/]"
    )

    console.print(
        f"Duration: "
        f"[bold]{result['minutes']} minutes[/]"
    )

    console.print(
        f"Monsters: "
        f"[green]{result['monster_kills']} defeated[/]"
    )

    console.print()

    console.print(
        f"Base EXP: "
        f"+[bold bright_cyan]"
        f"{result['base_exp']:,}"
        f"[/]"
    )

    console.print(
        f"Job EXP: "
        f"+[bold bright_yellow]"
        f"{result['job_exp']:,}"
        f"[/]"
    )

    console.print()

    for lv in result["base_levels"]:

        console.print(
            f"[bold bright_green]"
            f"★ BASE LEVEL UP! "
            f"-> Lv. {lv}"
            f"[/]"
        )

    for lv in result["job_levels"]:

        console.print(
            f"[bold bright_yellow]"
            f">> JOB LEVEL UP! "
            f"-> Job Lv. {lv}"
            f"[/]"
        )

    if result["drops"]:

        console.print()

        console.print(
            "[dim]-- Item Drops --[/]"
        )

        for item in result["drops"]:

            console.print(
                f" • [white]{item}[/]"
            )

    if result.get("material_drops"):

        console.print()

        console.print(
            "[dim]-- Refinement Materials --[/]"
        )

        for mat, qty in result["material_drops"].items():

            color = "bright_cyan" if mat == "Oridecon" else "bright_blue"

            console.print(
                f" ◆ [{color}]{mat} ×{qty}[/]"
            )

    if result.get("equip_drop"):

        from data.items import get_item as _get_item
        _eq = _get_item(result["equip_drop"])
        _name = _eq["name"] if _eq else result["equip_drop"]
        _rarity = _eq.get("rarity", "common") if _eq else "common"
        _color  = {
            "common": "white", "uncommon": "bright_green",
            "rare": "bright_blue", "legendary": "bright_yellow",
        }.get(_rarity, "white")

        console.print()
        console.print("[dim]-- Equipment Drop --[/]")
        console.print(f" ★ [{_color}]{_name}[/] [dim](added to inventory)[/]")

    if result.get("zeny_earned", 0) > 0:

        console.print()
        console.print(
            f" [bright_yellow]Zeny: +{result['zeny_earned']:,}z[/]"
        )

    console.print()

    console.print(
        f"Now at "
        f"Base Lv."
        f"[cyan]{char.base_level}[/] "
        f"({int(char.base_exp_progress * 100)}%)"
    )

    console.print(
        f"Job Lv."
        f"[yellow]{char.job_level}[/] "
        f"({int(char.job_exp_progress * 100)}%)"
    )

    console.print()

    console.print(
        "─" * 50,
        style="dim"
    )
