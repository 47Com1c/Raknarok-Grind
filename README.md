# Ragnarok Grind
### A terminal-based MMORPG productivity simulator

> *Productivity is the grind. The grind is everything.*

---

## What is this?

Ragnarok Grind transforms your focus sessions into a Ragnarok Online-style progression system. Every minute of real disciplined work earns EXP, advances your class, and builds toward Transcendence.

This is **not** a task manager. There are no to-do lists. No dashboards.  
This is a **grinding simulator**. You choose a zone, set a timer, and work. That's the game.

---

## Features

- **Dual Level System** — Base Level (lifetime) + Job Level (class mastery)
- **Full Class Tree** — Novice → First Class → Second Class → Transcendent → Third Class  
  (29 classes total: Knight, Wizard, Hunter, Priest, Monk, Bard, and their evolved forms)
- **Transcendence/Rebirth** — Reset your levels for permanent EXP bonuses and prestige classes
- **Grinding Zones** — Prontera Fields, Payon Forest, Geffen Dungeon, Orc Dungeon, Clock Tower, Glast Heim, Niflheim
- **Live Terminal UI** — ASCII combat log, real-time EXP bars, zone atmosphere
- **Cosmetic Loot** — Items, titles, and auras earned through sessions
- **Streak System** — Maintain daily grind streaks for bonus prestige
- **SQLite Persistence** — Multiple characters, saved locally

---

## Quick Start

```bash
git clone https://github.com/47Com1c/Raknarok-Grind.git
cd Raknarok-Grind/

# Requirements: Python 3.11+ and Rich
pip install rich

# Run
python3 main.py
```

---

## Gameplay Loop

```
Boot → Select/Create Character
  ↓
Main Menu
  ↓
Select Zone (Grinding Map)
  ↓
Set Session Duration (5–90 min)
  ↓
GRIND (real focus session, live timer)
  ↓
Session Complete → EXP + Drops + Level-ups
  ↓
Check Class Change / Transcendence
  ↓
Repeat
```

---

## Class Progression

```
Novice (Job Lv. 10)
  ├── Swordsman → Knight / Crusader → Lord Knight / Paladin → Rune Knight / Royal Guard
  ├── Mage     → Wizard / Sage     → High Wizard / Professor → Warlock / Sorcerer
  ├── Archer   → Hunter / Bard     → Sniper / Clown          → Ranger / Maestro
  └── Acolyte  → Priest / Monk     → High Priest / Champion  → Arch Bishop / Sura
```

**Transcendence** requires Base Lv. 99 + Job Lv. 50 at Second Class.  
After rebirth: levels reset, class upgrades, permanent EXP bonus unlocked.

---

## EXP Formula

Session EXP scales with:
1. **Duration** — longer sessions = more EXP (non-linear brackets)
2. **Zone multiplier** — harder zones grant more EXP
3. **Transcendence bonus** — permanent +10/20/30% per rebirth

```
Base EXP to next level = (level ^ 2.8) × 12
Job  EXP to next level = (level ^ 2.5) × tier_multiplier
```

---

## Project Structure

```
ragnarok_grind/
├── main.py              # Entry point, game loop
├── core/
│   ├── character.py     # Character dataclass + SQLite save/load
│   └── session.py       # Focus session engine (live timer + combat log)
├── ui/
│   └── screens.py       # All terminal UI panels and menus
├── data/
│   └── constants.py     # Class trees, zones, EXP formulas, loot tables
└── saves/
    └── ragnarok_grind.db  # SQLite save file (auto-created)
```

---

## Controls

**During a session:**
- `P` — Pause / Resume
- `Q` — Abandon session (no EXP awarded)

**Main menu:**
- `G` — Grind (enter a zone)
- `S` — Status screen
- `C` — Class change
- `T` — Transcendence
- `H` — Session history
- `I` — Inventory
- `E` — Equip title
- `Q` — Quit

---

## Philosophy

The emotional design mirrors Ragnarok Online's addictive loop:

| RO Mechanic | Ragnarok Grind |
|---|---|
| Monster grinding | Focus sessions |
| EXP farming | Real work time |
| Level bars filling | Visible daily progress |
| Class change ceremony | Milestone achievement |
| Rebirth/Transcendence | Seasonal productivity resets |
| Loot drops | Cosmetic item rewards |
| Zone difficulty | Session length |
| Permanent class identity | Long-term character investment |

You are not "gamifying" productivity.  
You are training your character through real-life discipline.
