"""
D&D 5e Core - Gold Rewards System
Treasure rewards based on encounter level from DMG
"""

# Encounter gold rewards table (DMG p.133)
# Based on "Treasure per Encounter" by level
ENCOUNTER_GOLD_TABLE = {
    1: 300,
    2: 600,
    3: 900,
    4: 1200,
    5: 1600,
    6: 2000,
    7: 2600,
    8: 3400,
    9: 4500,
    10: 5800,
    11: 7500,
    12: 9800,
    13: 13000,
    14: 17000,
    15: 22000,
    16: 28000,
    17: 36000,
    18: 47000,
    19: 61000,
    20: 80000,
}


def get_encounter_gold(encounter_level: int) -> int:
    """
    Get gold reward for an encounter based on level.

    Args:
        encounter_level: Encounter difficulty level (1-20)

    Returns:
        Gold pieces for this encounter level
    """
    encounter_level = max(1, min(20, encounter_level))
    return ENCOUNTER_GOLD_TABLE.get(encounter_level, 0)


def calculate_treasure_hoard(level: int, multiplier: float = 1.0) -> int:
    """
    Calculate treasure hoard for a given level.

    Args:
        level: Character/encounter level
        multiplier: Multiplier for difficulty (easy=0.5, medium=1.0, hard=1.5, deadly=2.0)

    Returns:
        Total gold pieces
    """
    base_gold = get_encounter_gold(level)
    return int(base_gold * multiplier)


__all__ = [
    'ENCOUNTER_GOLD_TABLE',
    'get_encounter_gold',
    'calculate_treasure_hoard',
]

