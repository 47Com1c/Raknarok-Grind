"""
RAGNAROK GRIND — Main Game Loop
Entry point. Ties together all systems.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console

from core.character import (
    Character, save_character, load_character,
    list_characters, character_exists
)
from core.session import run_session, display_session_results
from ui.screens import (
    show_splash, show_main_menu, show_status,
    show_zone_select, show_class_change,
    show_transcendence, show_title_select,
    show_session_history, show_inventory,
    show_character_creation, show_character_select,
    _play_rebirth_ceremony, show_equipment,
    show_refine_screen,
)
from data.constants import ALL_CLASSES

console = Console()


# ─────────────────────────────────────────────
#  GAME BOOT
# ─────────────────────────────────────────────

def boot() -> Character | None:
    show_splash()
    characters = list_characters()

    if not characters:
        console.print("  No adventurers found. Create your character.\n", style="dim")
        time.sleep(1)
        result = show_character_creation()
        if not result:
            return None
        name, gender = result
        char = Character(name=name, gender=gender)
        char.give_starter_equipment()
        save_character(char)
        console.print(f"\n  [bright_green]Character created: {name}[/]\n")
        time.sleep(1)
        return char

    choice = show_character_select(characters)

    if choice is None:
        return None

    if choice == "new":
        result = show_character_creation()
        if not result:
            return boot()
        name, gender = result
        if character_exists(name):
            console.print(f"\n  [red]Name '{name}' is taken.[/]\n")
            time.sleep(1.5)
            return boot()
        char = Character(name=name, gender=gender)
        char.give_starter_equipment()
        save_character(char)
        console.print(f"\n  [bright_green]Character created: {name}[/]\n")
        time.sleep(1)
        return char

    char = load_character(choice)
    if not char:
        console.print("\n  [red]Failed to load character.[/]\n")
        time.sleep(1)
        return None

    return char


# ─────────────────────────────────────────────
#  GRIND FLOW
# ─────────────────────────────────────────────

def do_grind(char: Character) -> None:
    zone_id, minutes = show_zone_select(char)
    if zone_id is None:
        return

    console.clear()
    console.print()
    console.print("  Preparing session...", style="dim")
    time.sleep(0.8)

    result = run_session(char, zone_id, minutes)

    if result is None:
        console.print("\n  [dim]Returned from the zone without EXP.[/]\n")
        time.sleep(1.5)
        return

    display_session_results(result, char)

    # Check for milestone titles
    new_titles = char.check_milestone_titles()
    if new_titles:
        console.print()
        for t in new_titles:
            console.print(f"  [bright_yellow]★ Title unlocked: {t}[/]")
        save_character(char)

    input("\n  Press ENTER to continue...\n")


# ─────────────────────────────────────────────
#  CLASS CHANGE FLOW
# ─────────────────────────────────────────────

def do_class_change(char: Character) -> None:
    chosen = show_class_change(char)

    if not chosen:
        return

    success = char.change_class(chosen)

    if success:
        save_character(char)
        # Ceremony is already played inside show_class_change
        # Award title for first class change
        if char.class_tier == 1:
            if char.award_title("Novice No More"):
                console.print("\n  [bright_yellow]★ Title unlocked: Novice No More[/]")
                save_character(char)
        elif char.class_tier == 2:
            if char.award_title("Path Chosen"):
                console.print("\n  [bright_yellow]★ Title unlocked: Path Chosen[/]")
                save_character(char)
        elif char.class_tier == 3 and char.class_data.get("transcendent"):
            if char.award_title("Transcendent"):
                console.print("\n  [bright_yellow]★ Title unlocked: Transcendent[/]")
                save_character(char)
        elif char.class_tier >= 4:
            if char.award_title("Lord of the Grind"):
                console.print("\n  [bright_yellow]★ Title unlocked: Lord of the Grind[/]")
                save_character(char)
        time.sleep(1.5)
    else:
        console.print("\n  [red dim]Class change failed.[/]\n")
        time.sleep(1.5)


# ─────────────────────────────────────────────
#  REBIRTH / TRANSCENDENCE FLOW
# ─────────────────────────────────────────────

def do_transcendence(char: Character) -> None:
    confirmed = show_transcendence(char)

    if not confirmed:
        console.print("\n  [dim]You turn away from Rebirth. For now.[/]\n")
        time.sleep(1.5)
        return

    success = char.perform_rebirth()

    if success:
        save_character(char)
        _play_rebirth_ceremony(char)
    else:
        console.print("\n  [red]Rebirth failed. Check requirements.[/]\n")
        time.sleep(1.5)


# ─────────────────────────────────────────────
#  MAIN GAME LOOP
# ─────────────────────────────────────────────

def game_loop(char: Character) -> None:
    while True:
        choice = show_main_menu(char)

        if choice == "G":
            do_grind(char)

        elif choice == "S":
            show_status(char)
            input("\n  Press ENTER to continue...\n")

        elif choice == "C":
            do_class_change(char)

        elif choice == "T":
            do_transcendence(char)

        elif choice == "H":
            show_session_history(char)
            input("\n  Press ENTER to continue...\n")

        elif choice == "I":
            show_inventory(char)
            input("\n  Press ENTER to continue...\n")

        elif choice == "W":
            show_equipment(char)

        elif choice == "R":
            show_refine_screen(char)

        elif choice == "E":
            show_title_select(char)

        elif choice == "Q":
            console.print()
            console.print("  [dim]The grind is paused. Your progress is saved.[/]")
            console.print("  [dim]Return when you are ready.[/]")
            console.print()
            break

        else:
            console.print(f"\n  [dim]Unknown command: {choice}[/]\n")
            time.sleep(0.5)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def main():
    try:
        char = boot()
        if char is None:
            console.print("\n  [dim]Farewell, adventurer.[/]\n")
            sys.exit(0)
        game_loop(char)
    except KeyboardInterrupt:
        console.print("\n\n  [dim]Session interrupted. Progress saved.[/]\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
