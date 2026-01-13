"""
D&D 5e Core - Character and Monster Loading
Provides utilities to load characters and monsters from the D&D 5e API
"""
from typing import List, Dict, Optional, Tuple
from random import choice, randint
import requests


API_BASE_URL = "https://www.dnd5eapi.co/api"


def populate(collection_name: str, key_name: str = "results") -> List[str]:
    """
    Get a list of items from a collection in the D&D 5e API.

    Args:
        collection_name: Name of the collection (e.g., "monsters", "spells")
        key_name: Key to extract from response (default: "results")

    Returns:
        List of item indices
    """
    try:
        response = requests.get(f"{API_BASE_URL}/{collection_name}")
        response.raise_for_status()
        data = response.json()

        if key_name in data:
            return [item['index'] for item in data[key_name]]
        return []
    except Exception as e:
        print(f"Error loading {collection_name}: {e}")
        return []


def request_monster(index: str):
    """
    Load a monster from the D&D 5e API.

    Args:
        index: Monster index (e.g., "goblin", "adult-red-dragon")

    Returns:
        Monster instance or None if not found
    """
    try:
        # Import here to avoid circular dependencies
        from .loader import load_monster
        return load_monster(index)
    except Exception as e:
        print(f"Error loading monster {index}: {e}")
        return None


def load_monsters_database():
    """
    Load all available monsters from the D&D 5e API.

    Returns:
        List of Monster instances
    """
    print("Loading monsters database...")
    monster_indices = populate("monsters", "results")
    monsters = []

    for index in monster_indices:
        monster = request_monster(index)
        if monster:
            monsters.append(monster)

    print(f"Loaded {len(monsters)} monsters")
    return monsters


def simple_character_generator(
    level: int = 1,
    race_name: Optional[str] = None,
    class_name: Optional[str] = None,
    name: Optional[str] = None
):
    """
    Generate a simple character with basic attributes.

    This is a simplified version that doesn't require loading full collections.
    For more advanced character generation, use the full API.

    Args:
        level: Character level (default: 1)
        race_name: Race name (optional, random if not provided)
        class_name: Class name (optional, random if not provided)
        name: Character name (optional, random if not provided)

    Returns:
        Character instance
    """
    # Import here to avoid circular dependencies
    from ..entities import Character
    from ..races import Race
    from ..classes import ClassType
    from ..abilities import Abilities

    # Default races
    if not race_name:
        race_name = choice(["human", "elf", "dwarf", "halfling"])

    # Default classes
    if not class_name:
        class_name = choice(["fighter", "wizard", "rogue", "cleric"])

    # Create simple race
    race = Race(
        index=race_name,
        name=race_name.capitalize(),
        speed=30,
        ability_bonuses={},
        alignment="Any",
        age="Varies",
        size="Medium",
        size_description="Medium size",
        starting_proficiencies=[],
        starting_proficiency_options=[],
        languages=[],
        language_desc="Common",
        traits=[],
        subraces=[]
    )

    # Create simple class
    hit_dice = {"fighter": 10, "wizard": 6, "rogue": 8, "cleric": 8}
    class_type = ClassType(
        index=class_name,
        name=class_name.capitalize(),
        hit_die=hit_dice.get(class_name, 8),
        proficiency_choices=[],
        proficiencies=[],
        saving_throws=[],
        starting_equipment=[],
        starting_equipment_options=[],
        class_levels=[],
        multi_classing=[],
        can_cast=class_name in ["wizard", "cleric"],
        spellcasting_ability="int" if class_name == "wizard" else "wis"
    )

    # Generate abilities
    def roll_ability():
        rolls = sorted([randint(1, 6) for _ in range(4)])
        return sum(rolls[1:])  # Drop lowest

    strength = roll_ability()
    dexterity = roll_ability()
    constitution = roll_ability()
    intelligence = roll_ability()
    wisdom = roll_ability()
    charisma = roll_ability()

    abilities = Abilities(strength, dexterity, constitution, intelligence, wisdom, charisma)

    mod = lambda x: (x - 10) // 2
    ability_modifiers = Abilities(
        mod(strength), mod(dexterity), mod(constitution),
        mod(intelligence), mod(wisdom), mod(charisma)
    )

    # Generate name
    if not name:
        prefixes = ["Ara", "Eld", "Gim", "Tho", "Bil", "Fro"]
        suffixes = ["dor", "rin", "li", "rgrim", "bo", "do"]
        name = choice(prefixes) + choice(suffixes)

    # Calculate HP
    hit_points = class_type.hit_die + ability_modifiers.con
    for _ in range(level - 1):
        hit_points += randint(1, class_type.hit_die) + ability_modifiers.con

    return Character(
        race=race,
        subrace=None,
        class_type=class_type,
        proficiencies=[],
        abilities=abilities,
        ability_modifiers=ability_modifiers,
        gender=choice(["male", "female"]),
        name=name,
        ethnic=None,
        height=66 + randint(-6, 6),
        weight=150 + randint(-30, 30),
        inventory=[None] * 20,
        hit_points=hit_points,
        max_hit_points=hit_points,
        xp=0,
        level=level,
        age=18 * 52 + randint(0, 299),
        gold=90 + randint(0, 99),
        sc=None,
        conditions=[],
        speed=race.speed,
        haste_timer=0,
        hasted=False,
        st_advantages=[]
    )


__all__ = [
    'populate',
    'request_monster',
    'load_monsters_database',
    'simple_character_generator',
]

