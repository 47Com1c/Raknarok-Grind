"""
RAGNAROK GRIND — Game Constants
All class trees, zone data, EXP formulas, titles, prestige cosmetics.

Class tree follows official Ragnarok Online progression:
  Novice → 1st Job → 2nd Job → [Rebirth] → High Novice →
  High 1st → Transcendent 2nd → 3rd Job
"""

import random


# ─────────────────────────────────────────────
#  EXP FORMULA CONSTANTS
# ─────────────────────────────────────────────

def base_exp_to_level(level: int) -> int:
    if level <= 1:
        return 0
    return int((level ** 2.8) * 12)


def job_exp_to_level(level: int, class_tier: int = 1) -> int:
    if level <= 1:
        return 0
    multiplier = {0: 5, 1: 8, 2: 14, 3: 20, 4: 28}
    return int((level ** 2.5) * multiplier.get(class_tier, 8))


SESSION_EXP = {
    "base": {
        5:  {"base": 18,  "job": 12},
        10: {"base": 42,  "job": 28},
        15: {"base": 72,  "job": 48},
        20: {"base": 110, "job": 72},
        25: {"base": 155, "job": 100},
        30: {"base": 210, "job": 138},
        45: {"base": 340, "job": 220},
        60: {"base": 480, "job": 310},
        90: {"base": 720, "job": 460},
    }
}


def get_session_exp(minutes: int, zone_multiplier: float = 1.0, transcendent: bool = False) -> dict:
    brackets = sorted(SESSION_EXP["base"].keys())
    bracket = brackets[0]
    for b in brackets:
        if minutes >= b:
            bracket = b
    base = SESSION_EXP["base"][bracket]
    trans_bonus = 1.3 if transcendent else 1.0
    CHEAT_MULT = 10
    return {
        "base_exp": int(base["base"] * zone_multiplier * trans_bonus * CHEAT_MULT),
        "job_exp":  int(base["job"]  * zone_multiplier * trans_bonus * CHEAT_MULT),
        "minutes":  minutes,
        "zone_mult": zone_multiplier,
    }


# ─────────────────────────────────────────────
#  CLASS DATABASE
# ─────────────────────────────────────────────

CLASS_DB: dict = {
    # Tier 0 – Novice
    "Novice": {
        "tier": 0, "description": "Your journey begins. Every master was once here.",
        "aura": "", "color": "white", "ascii_sprite": ["( ˶ˆᗜˆ˵ )", "  Novice  "],
        "job_max": 10, "base_max": 99, "transcendent": False,
    },
    # Tier 0 – High Novice (post-rebirth)
    "High Novice": {
        "tier": 0, "description": "Reborn from sacrifice. The second beginning.",
        "aura": "★", "color": "bright_magenta", "ascii_sprite": ["★( ˶ˆᗜˆ˵ )★", "High Novice"],
        "job_max": 10, "base_max": 99, "transcendent": True,
    },
    # Tier 1 – First jobs
    "Swordsman": {
        "tier": 1, "description": "Steel body, iron will. The path of discipline.",
        "aura": "", "color": "blue", "ascii_sprite": ["  o/|\\  ", " Sword.  "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Mage": {
        "tier": 1, "description": "Power born from study. Knowledge is your spell.",
        "aura": "", "color": "cyan", "ascii_sprite": ["  \\o/  ", "  Mage  "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Archer": {
        "tier": 1, "description": "Precision and patience. One shot, one kill.",
        "aura": "", "color": "yellow", "ascii_sprite": ["  o)=>  ", " Archer  "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Acolyte": {
        "tier": 1, "description": "Faith fuels the grind. Devotion is your power.",
        "aura": "", "color": "bright_magenta", "ascii_sprite": ["  +o+  ", " Acoly. "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Thief": {
        "tier": 1, "description": "Speed and cunning. Strike before they notice.",
        "aura": "", "color": "bright_red", "ascii_sprite": ["  ¿o¿  ", "  Thief  "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Merchant": {
        "tier": 1, "description": "Wealth through effort. Every resource invested.",
        "aura": "", "color": "bright_yellow", "ascii_sprite": ["  $o$  ", "Merchant "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    # Tier 1 – High first jobs (post-rebirth)
    "High Swordsman": {
        "tier": 1, "description": "A warrior reborn, sharper in every way.",
        "aura": "★", "color": "bright_blue", "ascii_sprite": ["★o/|\\  ", "H.Sword. "],
        "job_max": 50, "base_max": 99, "transcendent": True,
    },
    "High Mage": {
        "tier": 1, "description": "Magic refined through sacrifice and rebirth.",
        "aura": "★", "color": "bright_cyan", "ascii_sprite": ["★\\o/  ", " H.Mage  "],
        "job_max": 50, "base_max": 99, "transcendent": True,
    },
    "High Archer": {
        "tier": 1, "description": "Aim perfected. Every arrow carries legend.",
        "aura": "★", "color": "bright_yellow", "ascii_sprite": ["★o)=>  ", "H.Archer "],
        "job_max": 50, "base_max": 99, "transcendent": True,
    },
    "High Acolyte": {
        "tier": 1, "description": "Faith tempered and reforged in rebirth.",
        "aura": "★", "color": "magenta", "ascii_sprite": ["★+o+  ", "H.Acoly. "],
        "job_max": 50, "base_max": 99, "transcendent": True,
    },
    "High Thief": {
        "tier": 1, "description": "Shadow and speed, reborn and relentless.",
        "aura": "★", "color": "red", "ascii_sprite": ["★¿o¿  ", "H.Thief  "],
        "job_max": 50, "base_max": 99, "transcendent": True,
    },
    "High Merchant": {
        "tier": 1, "description": "Every sacrifice becomes compound interest.",
        "aura": "★", "color": "yellow", "ascii_sprite": ["★$o$  ", "H.Merch. "],
        "job_max": 50, "base_max": 99, "transcendent": True,
    },
    # Tier 2 – Second jobs
    "Knight": {
        "tier": 2, "description": "A mounted warrior of unwavering resolve.",
        "aura": "⚔", "color": "blue", "ascii_sprite": ["  [o]  ", " Knight "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Crusader": {
        "tier": 2, "description": "Holy blade, divine purpose.",
        "aura": "✝", "color": "bright_blue", "ascii_sprite": [" ✝[o]  ", "Crusader"],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Wizard": {
        "tier": 2, "description": "Reality bends to your formulas.",
        "aura": "★", "color": "cyan", "ascii_sprite": ["  ~o~  ", " Wizard "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Sage": {
        "tier": 2, "description": "Ancient knowledge, patient mastery.",
        "aura": "∞", "color": "bright_cyan", "ascii_sprite": ["  *o*  ", "  Sage  "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Hunter": {
        "tier": 2, "description": "The wilderness is your classroom.",
        "aura": "◎", "color": "yellow", "ascii_sprite": ["  o)>~  ", " Hunter "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Bard": {
        "tier": 2, "description": "Your craft inspires greatness. [♂ Male only]",
        "aura": "♪", "color": "bright_yellow", "ascii_sprite": ["  ♪o♪  ", "  Bard  "],
        "job_max": 50, "base_max": 99, "transcendent": False, "gender_lock": "male",
    },
    "Dancer": {
        "tier": 2, "description": "Grace is power. Movement is your weapon. [♀ Female only]",
        "aura": "♫", "color": "bright_magenta", "ascii_sprite": ["  ♫o♫  ", " Dancer "],
        "job_max": 50, "base_max": 99, "transcendent": False, "gender_lock": "female",
    },
    "Priest": {
        "tier": 2, "description": "Sustaining others, transcending self.",
        "aura": "✦", "color": "bright_magenta", "ascii_sprite": ["  +o+  ", " Priest "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Monk": {
        "tier": 2, "description": "Body as temple. Every rep is a prayer.",
        "aura": "◆", "color": "magenta", "ascii_sprite": ["  *O*  ", "  Monk  "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Assassin": {
        "tier": 2, "description": "Silent. Precise. The perfect focus.",
        "aura": "†", "color": "bright_red", "ascii_sprite": ["  †o†  ", "Assassin"],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Rogue": {
        "tier": 2, "description": "Adaptable. Opportunistic. Every situation, an edge.",
        "aura": "⌖", "color": "red", "ascii_sprite": ["  ⌖o⌖  ", "  Rogue "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Blacksmith": {
        "tier": 2, "description": "Craft as discipline. Every hammer strike, intentional.",
        "aura": "⚒", "color": "bright_yellow", "ascii_sprite": ["  ⚒o⚒  ", "B.smith "],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    "Alchemist": {
        "tier": 2, "description": "Transmutation of effort into results.",
        "aura": "⚗", "color": "green", "ascii_sprite": ["  ⚗o⚗  ", "Alchemi."],
        "job_max": 50, "base_max": 99, "transcendent": False,
    },
    # Tier 3 – Transcendent second jobs
    "Lord Knight": {
        "tier": 3, "description": "Reborn in fire. The pinnacle of martial discipline.",
        "aura": "⚔★", "color": "bright_blue", "ascii_sprite": ["≡[◉]≡", " L.Knt  "],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "Paladin": {
        "tier": 3, "description": "Light and steel made incarnate.",
        "aura": "✝★", "color": "bright_white", "ascii_sprite": ["✝[◉]✝", "Paladin "],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "High Wizard": {
        "tier": 3, "description": "The arcane has no limit but your will.",
        "aura": "★★", "color": "bright_cyan", "ascii_sprite": ["~[◉]~", "H.Wiz. "],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "Professor": {
        "tier": 3, "description": "Every piece of knowledge compounds.",
        "aura": "∞★", "color": "cyan", "ascii_sprite": ["*[◉]*", "Prof.  "],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "Sniper": {
        "tier": 3, "description": "One session. Maximum impact.",
        "aura": "◎★", "color": "bright_yellow", "ascii_sprite": ["o)>=[◉]", "Sniper "],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "Clown": {
        "tier": 3, "description": "Mastery worn lightly; power runs deep. [♂]",
        "aura": "♪★", "color": "yellow", "ascii_sprite": ["♪[◉]♪", " Clown  "],
        "job_max": 70, "base_max": 99, "transcendent": True, "gender_lock": "male",
    },
    "Gypsy": {
        "tier": 3, "description": "Dance that breaks the world. [♀]",
        "aura": "♫★", "color": "bright_magenta", "ascii_sprite": ["♫[◉]♫", " Gypsy  "],
        "job_max": 70, "base_max": 99, "transcendent": True, "gender_lock": "female",
    },
    "High Priest": {
        "tier": 3, "description": "Discipline sanctified by rebirth.",
        "aura": "✦★", "color": "bright_magenta", "ascii_sprite": ["✦[◉]✦", "H.Pst. "],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "Champion": {
        "tier": 3, "description": "The spirit that never breaks.",
        "aura": "◆★", "color": "magenta", "ascii_sprite": ["◆[◉]◆", "Champ. "],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "Assassin Cross": {
        "tier": 3, "description": "Death perfected through rebirth.",
        "aura": "†★", "color": "bright_red", "ascii_sprite": ["†[◉]†", "A.Cross"],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "Stalker": {
        "tier": 3, "description": "Every shadow is your ally.",
        "aura": "⌖★", "color": "red", "ascii_sprite": ["⌖[◉]⌖", "Stalker"],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "Whitesmith": {
        "tier": 3, "description": "Craft elevated to transcendent art.",
        "aura": "⚒★", "color": "bright_yellow", "ascii_sprite": ["⚒[◉]⚒", "W.smith"],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    "Biochemist": {
        "tier": 3, "description": "Life itself, rewritten.",
        "aura": "⚗★", "color": "green", "ascii_sprite": ["⚗[◉]⚗", "Biochem."],
        "job_max": 70, "base_max": 99, "transcendent": True,
    },
    # Tier 4 – Third jobs
    "Rune Knight": {
        "tier": 4, "description": "Ancient runes etched upon unbreakable will.",
        "aura": "ᚱ⚔★", "color": "bright_blue", "ascii_sprite": ["ᚱ[◈]ᚱ", "R.Knt. "],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Royal Guard": {
        "tier": 4, "description": "The shield that never yields.",
        "aura": "✝◈★", "color": "bright_white", "ascii_sprite": ["✝[◈]✝", "R.Guard"],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Warlock": {
        "tier": 4, "description": "Reality is merely unfinished mathematics.",
        "aura": "☠★★", "color": "bright_cyan", "ascii_sprite": ["☠[◈]☠", "Warlock"],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Sorcerer": {
        "tier": 4, "description": "All elements answer to a single mind.",
        "aura": "∞◈★", "color": "cyan", "ascii_sprite": ["~[◈]~", "Sorc.  "],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Ranger": {
        "tier": 4, "description": "Every environment is your domain.",
        "aura": "◎◈★", "color": "bright_yellow", "ascii_sprite": ["≫[◈]≫", "Ranger "],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Maestro": {
        "tier": 4, "description": "The art of mastery made audible. [♂]",
        "aura": "♫◈★", "color": "yellow", "ascii_sprite": ["♫[◈]♫", "Maestro"],
        "job_max": 70, "base_max": 175, "transcendent": True, "gender_lock": "male",
    },
    "Wanderer": {
        "tier": 4, "description": "Dance without chains. Exist beyond limits. [♀]",
        "aura": "♩◈★", "color": "magenta", "ascii_sprite": ["♩[◈]♩", "Wanderer"],
        "job_max": 70, "base_max": 175, "transcendent": True, "gender_lock": "female",
    },
    "Arch Bishop": {
        "tier": 4, "description": "Beyond faith — certainty.",
        "aura": "✦◈★", "color": "bright_magenta", "ascii_sprite": ["✦[◈]✦", "Arch Bp"],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Sura": {
        "tier": 4, "description": "Fist and spirit — one weapon.",
        "aura": "◆◈★", "color": "magenta", "ascii_sprite": ["◆[◈]◆", " Sura  "],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Guillotine Cross": {
        "tier": 4, "description": "The shadow that ends all things.",
        "aura": "†◈★", "color": "bright_red", "ascii_sprite": ["†[◈]†", "G.Cross"],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Shadow Chaser": {
        "tier": 4, "description": "Identity is fluid. Your edge is absolute.",
        "aura": "⌖◈★", "color": "red", "ascii_sprite": ["⌖[◈]⌖", "Sh.Chas."],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Mechanic": {
        "tier": 4, "description": "Man and machine, transcended together.",
        "aura": "⚙◈★", "color": "bright_yellow", "ascii_sprite": ["⚙[◈]⚙", "Mechanic"],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
    "Geneticist": {
        "tier": 4, "description": "Life remade in the image of discipline.",
        "aura": "⚗◈★", "color": "green", "ascii_sprite": ["⚗[◈]⚗", "Genetic."],
        "job_max": 70, "base_max": 175, "transcendent": True,
    },
}

# ── Convenience aliases ───────────────────────────────────────────────────────
ALL_CLASSES: dict = CLASS_DB

CLASS_TREE: dict = {
    "novice":       {k: v for k, v in CLASS_DB.items() if v["tier"] == 0 and not v.get("transcendent")},
    "first":        {k: v for k, v in CLASS_DB.items() if v["tier"] == 1 and not v.get("transcendent")},
    "second":       {k: v for k, v in CLASS_DB.items() if v["tier"] == 2},
    "transcendent": {k: v for k, v in CLASS_DB.items() if v["tier"] == 3},
    "third":        {k: v for k, v in CLASS_DB.items() if v["tier"] == 4},
}


def get_class(class_id: str) -> dict:
    return CLASS_DB.get(class_id, CLASS_DB["Novice"])


def get_class_tier(class_id: str) -> int:
    return get_class(class_id).get("tier", 0)


def get_available_branches(class_id, base_level, job_level, rebirth_count=0, gender="male"):
    from core.progression import get_available_advancements
    return get_available_advancements(class_id, base_level, job_level, rebirth_count, gender)


def get_aura_frame(tier: int, base_level: int = 1) -> str:
    frames = {0: "", 1: "·", 2: "○", 3: "◎", 4: "✦◎✦", 99: "★✦◎✦★"}
    if base_level >= 99:
        return frames[99]
    return frames.get(tier, "")


# ─────────────────────────────────────────────
#  ZONES
# ─────────────────────────────────────────────

ZONES = {
    "Prontera Fields": {
        "id": "prontera_fields", "description": "Gentle rolling hills. A forgiving start.",
        "recommended_minutes": 10, "exp_multiplier": 0.8, "min_level": 1, "color": "green",
        "atmosphere": "Soft wind. Familiar ground.",
        "ascii_map": ["  ~~~Prontera Fields~~~  ", " . [Poring] . . [Poring]"],
        "monsters": ["Poring", "Fabre", "Lunatic"],
        "loot_table": ["Jellybean", "Apple", "Red Herb"],
        # Tier 0-1 gear, small zeny
        "equip_table": ["falchion", "cotton_shirt", "hood", "sandals", "guard", "mace"],
        "equip_chance": 0.20,
        "zeny_drop": (30, 150),
    },
    "Payon Forest": {
        "id": "payon_forest", "description": "Dense undergrowth, steady gains.",
        "recommended_minutes": 20, "exp_multiplier": 1.0, "min_level": 10, "color": "bright_green",
        "atmosphere": "Leaves rustle. Focus sharpens.",
        "ascii_map": ["  ~~~Payon Forest~~~  ", " T [Willow] T [Wolf] T"],
        "monsters": ["Willow", "Wolf", "Scorpion"],
        "loot_table": ["Twig", "Trunk", "Wolf Claw"],
        # Tier 1 gear
        "equip_table": ["stiletto", "muffler", "shoes", "buckler", "crossbow", "mace"],
        "equip_chance": 0.25,
        "zeny_drop": (100, 400),
    },
    "Geffen Dungeon": {
        "id": "geffen_dungeon", "description": "Dark corridors, high EXP density.",
        "recommended_minutes": 25, "exp_multiplier": 1.25, "min_level": 25, "color": "cyan",
        "atmosphere": "Eerie silence. Magic crackles in the air.",
        "ascii_map": ["  ~~~Geffen Dungeon~~~  ", " # [Zombie] # [Ghoul] #"],
        "monsters": ["Zombie", "Ghoul", "Skeleton"],
        "loot_table": ["Bone", "Fabric", "Brigan"],
        # Tier 1-2 gear
        "equip_table": ["stiletto", "gladius", "padded_armor", "muffler", "boots", "arc_wand", "chain"],
        "equip_chance": 0.28,
        "zeny_drop": (200, 800),
    },
    "Orc Dungeon": {
        "id": "orc_dungeon", "description": "Overwhelming numbers. The true grind begins.",
        "recommended_minutes": 30, "exp_multiplier": 1.4, "min_level": 40, "color": "yellow",
        "atmosphere": "Thunder of boots. Pure grinding zen.",
        "ascii_map": ["  ~~~Orc Dungeon~~~  ", " % [Orc] [Orc Warrior] %"],
        "monsters": ["Orc", "Orc Warrior", "Orc Lady"],
        "loot_table": ["Orcish Voucher", "Axe", "Zargon", "Elunium"],
        # Tier 2 gear
        "equip_table": ["broadsword", "two_handed_axe", "chain_mail", "padded_armor", "shield",
                        "manteau", "boots", "ninja_suit", "tights", "gakkung_bow"],
        "equip_chance": 0.30,
        "zeny_drop": (400, 1500),
    },
    "Clock Tower": {
        "id": "clock_tower", "description": "Each tick is a session. Each session is progress.",
        "recommended_minutes": 45, "exp_multiplier": 1.6, "min_level": 55, "color": "bright_yellow",
        "atmosphere": "Time itself becomes your ally.",
        "ascii_map": ["  ~~~Clock Tower~~~  ", " ⌚ [Alarms] [Clock] ⌚"],
        "monsters": ["Alarms", "Clock", "Punk"],
        "loot_table": ["Cogwheel", "Clock Hand", "Time Crystal", "Elunium", "Oridecon"],
        # Tier 2-3 gear
        "equip_table": ["claymore", "broadsword", "mage_coat", "chain_mail", "ninja_suit",
                        "arc_wand", "jur", "gakkung_bow", "manteau", "shield"],
        "equip_chance": 0.32,
        "zeny_drop": (800, 3000),
    },
    "Glast Heim": {
        "id": "glast_heim", "description": "The pinnacle of the grind. Only the committed survive.",
        "recommended_minutes": 60, "exp_multiplier": 2.0, "min_level": 70, "color": "bright_magenta",
        "atmosphere": "Ancient evil hums. The air is heavy with legacy.",
        "ascii_map": ["  ~~~Glast Heim~~~  ", " ☠ [Abysmal Knt] [Raydric] ☠"],
        "monsters": ["Abysmal Knight", "Raydric", "Wanderer"],
        "loot_table": ["Bradium", "Orideocon", "Cursed Fragment", "Oridecon", "Elunium"],
        # Tier 3 gear (rare)
        "equip_table": ["claymore", "full_plate_armor", "jur", "mage_coat", "ninja_suit",
                        "two_handed_axe", "gakkung_bow", "arc_wand", "manteau"],
        "equip_chance": 0.35,
        "zeny_drop": (2000, 7000),
    },
    "Niflheim": {
        "id": "niflheim", "description": "The land of the dead. For transcendent grinders only.",
        "recommended_minutes": 90, "exp_multiplier": 2.5, "min_level": 85, "color": "bright_red",
        "atmosphere": "Death is not an end. It is a level.",
        "ascii_map": ["  ~~~Niflheim~~~  ", " ✦ [Wight King] [Dullahan] ✦"],
        "monsters": ["Wight King", "Dullahan", "Dark Illusion"],
        "loot_table": ["Soul Shard", "Dark Crystal", "Void Essence", "Oridecon", "Elunium"],
        # Tier 3 gear (highest chance)
        "equip_table": ["claymore", "full_plate_armor", "jur", "mage_coat", "ninja_suit",
                        "two_handed_axe", "gakkung_bow", "arc_wand", "claymore", "full_plate_armor"],
        "equip_chance": 0.40,
        "zeny_drop": (5000, 15000),
        "transcendent_only": True,
    },
}


def get_available_zones(base_level: int, transcendent: bool = False) -> dict:
    available = {}
    for name, zone in ZONES.items():
        if base_level >= zone["min_level"]:
            if zone.get("transcendent_only") and not transcendent:
                continue
            available[name] = zone
    return available


# ─────────────────────────────────────────────
#  TITLES
# ─────────────────────────────────────────────

TITLES = {
    "First Steps":        {"desc": "Complete your first session",     "rarity": "common"},
    "The Grind Begins":   {"desc": "Complete 10 sessions",           "rarity": "common"},
    "Seasoned Farmer":    {"desc": "Complete 50 sessions",           "rarity": "uncommon"},
    "True Grinder":       {"desc": "Complete 100 sessions",          "rarity": "rare"},
    "Endless Devotion":   {"desc": "Complete 365 sessions",          "rarity": "legendary"},
    "Iron Will":          {"desc": "Complete a 60+ min session",     "rarity": "uncommon"},
    "Endurance":          {"desc": "Complete a 90+ min session",     "rarity": "rare"},
    "The Awakened":       {"desc": "Reach Base Level 50",            "rarity": "uncommon"},
    "Century Knight":     {"desc": "Reach Base Level 99",            "rarity": "rare"},
    "Reborn":             {"desc": "Complete Rebirth",               "rarity": "legendary"},
    "Twice Reborn":       {"desc": "Rebirth a second time",          "rarity": "legendary"},
    "Lord of the Grind":  {"desc": "Reach Third Class",              "rarity": "legendary"},
    "Novice No More":     {"desc": "Change first class",             "rarity": "common"},
    "Path Chosen":        {"desc": "Choose your second class",       "rarity": "uncommon"},
    "Transcendent":       {"desc": "Reach a Transcendent 2nd class", "rarity": "rare"},
    "The Devoted":        {"desc": "7-day grind streak",             "rarity": "uncommon"},
    "Unbroken":           {"desc": "30-day grind streak",            "rarity": "rare"},
    "Eternal":            {"desc": "100-day grind streak",           "rarity": "legendary"},
}

RARITY_COLORS = {
    "common": "white", "uncommon": "bright_green",
    "rare": "bright_cyan", "legendary": "bright_yellow",
}

AURA_FRAMES = {0: "", 1: "·", 2: "○", 3: "◎", 4: "✦◎✦", 99: "★✦◎✦★"}


# ─────────────────────────────────────────────
#  REBIRTH / TRANSCENDENCE
# ─────────────────────────────────────────────

REBIRTH_REQ = {
    "base_level": 99,
    "job_level": 50,
    "message": [
        "You have reached the limit of this life.",
        "The path forward is through rebirth.",
        "Will you sacrifice everything to become more?",
        "",
        "Base Level will reset. Job Level will reset.",
        "But your power grows. Your essence remains.",
        "Your titles remain. Your legend remains.",
        "",
        "This is Rebirth.",
    ],
}

TRANSCENDENCE_REQ = REBIRTH_REQ  # legacy alias

TRANSCENDENCE_BONUSES = {
    1: {"exp_bonus": 0.10, "label": "First Rebirth",  "aura_upgrade": True},
    2: {"exp_bonus": 0.20, "label": "Second Rebirth", "aura_upgrade": True},
    3: {"exp_bonus": 0.30, "label": "Third Rebirth",  "aura_upgrade": True},
}

# Which High 1st job corresponds to each 2nd job (used by rebirth system)
REBIRTH_CLASS_MAP: dict = {
    "Knight": "High Swordsman", "Crusader": "High Swordsman",
    "Wizard": "High Mage",      "Sage": "High Mage",
    "Hunter": "High Archer",    "Bard": "High Archer",   "Dancer": "High Archer",
    "Priest": "High Acolyte",   "Monk": "High Acolyte",
    "Assassin": "High Thief",   "Rogue": "High Thief",
    "Blacksmith": "High Merchant", "Alchemist": "High Merchant",
}


# ─────────────────────────────────────────────
#  DROPS
# ─────────────────────────────────────────────

DROPS = {
    "Jellybean":       {"rarity": 0.80, "desc": "Soft, colorful, completely useless.",  "color": "white"},
    "Apple":           {"rarity": 0.75, "desc": "A simple fruit from simpler times.",   "color": "red"},
    "Red Herb":        {"rarity": 0.70, "desc": "Smells faintly of effort.",            "color": "bright_red"},
    "Twig":            {"rarity": 0.70, "desc": "A thin branch. Still counts.",         "color": "yellow"},
    "Trunk":           {"rarity": 0.60, "desc": "Heavier than it looks.",               "color": "yellow"},
    "Wolf Claw":       {"rarity": 0.55, "desc": "Sharp. A worthy trophy.",              "color": "white"},
    "Bone":            {"rarity": 0.60, "desc": "The spoils of dedication.",            "color": "white"},
    "Fabric":          {"rarity": 0.50, "desc": "Still usable. Mostly.",               "color": "dim"},
    "Brigan":          {"rarity": 0.45, "desc": "Currency of the committed.",           "color": "bright_yellow"},
    "Orcish Voucher":  {"rarity": 0.35, "desc": "Proof of sustained effort.",          "color": "yellow"},
    "Axe":             {"rarity": 0.30, "desc": "Heavy. Earned.",                      "color": "blue"},
    "Zargon":          {"rarity": 0.30, "desc": "Strange ore. Stranger grinder.",       "color": "cyan"},
    "Clock Hand":      {"rarity": 0.25, "desc": "Time carved into metal.",             "color": "bright_white"},
    "Cogwheel":        {"rarity": 0.25, "desc": "Time itself rewarded you.",           "color": "bright_yellow"},
    "Cursed Fragment": {"rarity": 0.20, "desc": "Born from the darkest grind.",        "color": "bright_magenta"},
    "Bradium":         {"rarity": 0.15, "desc": "Ancient ore. Ancient discipline.",    "color": "bright_cyan"},
    "Orideocon":       {"rarity": 0.10, "desc": "Rare ore. A grinder's trophy.",       "color": "bright_cyan"},
    "Time Crystal":    {"rarity": 0.05, "desc": "Crystallized focus. Legendary.",      "color": "bright_yellow"},
    "Dark Crystal":    {"rarity": 0.04, "desc": "Forged in Niflheim's darkness.",      "color": "magenta"},
    "Void Essence":    {"rarity": 0.03, "desc": "Only Niflheim can grant this.",       "color": "bright_red"},
    "Soul Shard":      {"rarity": 0.02, "desc": "Fragment of a transcended soul.",     "color": "bright_magenta"},

    # ── Refinement Materials ──────────────────────────────────────────────────
    "Oridecon":        {"rarity": 0.08, "desc": "Weapon refinement ore. Hard-earned.", "color": "bright_cyan",  "material": True},
    "Elunium":         {"rarity": 0.10, "desc": "Armor refinement ore. Steady prize.", "color": "bright_blue",  "material": True},
}


REFINEMENT_MATERIALS = {"Oridecon", "Elunium"}


def roll_drops(zone_id: str, minutes: int) -> list:
    """Cosmetic drops. More rolls, higher base chance."""
    zone = next((z for z in ZONES.values() if z["id"] == zone_id), None)
    if not zone:
        return []
    loot_table = [i for i in zone.get("loot_table", []) if i not in REFINEMENT_MATERIALS]
    if not loot_table:
        return []
    results = []
    rolls = max(2, minutes // 5)       # 1 roll per 5 min, minimum 2
    for _ in range(rolls):
        if random.random() < 0.75:     # 75% chance per roll
            item = random.choice(loot_table)
            if item not in results:
                results.append(item)
    return results


def roll_material_drops(zone_id: str, minutes: int) -> dict:
    """
    Oridecon / Elunium drops. Always at least 1 roll even for short sessions.
    Only zones with materials in their loot_table can drop them.
    """
    zone = next((z for z in ZONES.values() if z["id"] == zone_id), None)
    if not zone:
        return {}
    material_pool = [i for i in zone.get("loot_table", []) if i in REFINEMENT_MATERIALS]
    if not material_pool:
        return {}
    result: dict[str, int] = {}
    base_chance = 0.35 * zone.get("exp_multiplier", 1.0)  # scales with zone difficulty
    base_chance = min(base_chance, 0.75)                   # cap at 75%
    rolls = max(1, minutes // 8)                           # 1 roll per 8 min, minimum 1
    for _ in range(rolls):
        if random.random() < base_chance:
            mat = random.choice(material_pool)
            result[mat] = result.get(mat, 0) + 1
    return result


def roll_equip_drop(zone_id: str, minutes: int) -> str | None:
    """
    Roll for an equipment item drop from the zone's equip_table.
    Returns an item_id string or None.
    Higher zones have better gear and slightly higher chance.
    """
    zone = next((z for z in ZONES.values() if z["id"] == zone_id), None)
    if not zone:
        return None
    equip_table = zone.get("equip_table", [])
    if not equip_table:
        return None
    base_chance = zone.get("equip_chance", 0.20)
    # Bonus chance for longer sessions (up to +15%)
    time_bonus = min(0.15, (minutes - 10) * 0.005) if minutes > 10 else 0.0
    final_chance = base_chance + time_bonus
    if random.random() < final_chance:
        return random.choice(equip_table)
    return None


def roll_zeny_drop(zone_id: str, minutes: int) -> int:
    """
    Roll for zeny earned from monsters. Scales with session length.
    Returns the zeny amount (0 if unlucky).
    """
    zone = next((z for z in ZONES.values() if z["id"] == zone_id), None)
    if not zone:
        return 0
    zeny_range = zone.get("zeny_drop", (0, 0))
    if not zeny_range or zeny_range[1] == 0:
        return 0
    # Always earn some zeny; scale by minutes
    scale = max(0.5, min(2.0, minutes / zone.get("recommended_minutes", 20)))
    low  = int(zeny_range[0] * scale)
    high = int(zeny_range[1] * scale)
    return random.randint(low, high)


# ─────────────────────────────────────────────
#  FLAVOR TEXT
# ─────────────────────────────────────────────

SESSION_START_MSGS = [
    "The grind begins. Stay focused.",
    "Your character enters the zone.",
    "Enemies sense your resolve. Let them.",
    "The EXP bar waits for no one.",
    "Every minute counts. Make them count.",
    "The zone is active. You are grinding.",
    "Focus sharpens. Time to farm.",
]

SESSION_END_MSGS = [
    "Session complete. The EXP has been claimed.",
    "You return from the grind victorious.",
    "The monsters fall. You grow stronger.",
    "Another session etched into your legend.",
    "EXP gained. The bar moves. Repeat.",
]

LEVEL_UP_MSGS = [
    "BASE LEVEL UP!", "The numbers don't lie — you've grown.",
    "Level gained through honest effort.", "One step closer to Transcendence.",
]

JOB_LEVEL_UP_MSGS = [
    "JOB LEVEL UP! Your mastery deepens.", "Job expertise increases.",
    "Your class path sharpens.", "Mastery of the craft grows.",
]

CLASS_CHANGE_FLAVOR: dict = {
    "default": [
        "The path reveals itself.", "A new identity forged.",
        "Your discipline earns this.", "The class is yours. Prove it.",
    ],
    "rebirth": [
        "You have sacrificed everything.", "Reborn from the ashes of Base 99.",
        "The second life begins here.", "Empty again. But not the same.",
    ],
    "third": [
        "You have reached a place most never see.",
        "Third job. The pinnacle of the grind.",
        "The world bends before your mastery.",
        "This is what all those sessions were for.",
    ],
}
