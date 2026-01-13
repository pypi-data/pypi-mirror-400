# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-01-05

### Added
- **Complete Implementation of All Empty Classes** - All previously empty or incomplete classes have been fully implemented:
  
  **Equipment System**:
  - `Inventory` class for managing equipment with quantities
  
  **Spell System**:
  - `SpellSlots` class for managing spell slot usage and recovery
  - `get_spell_slots_by_level()` function for spell slot progression
  - Complete cantrip system with damage scaling by character level
  - `DAMAGE_CANTRIPS` and `UTILITY_CANTRIPS` dictionaries
  - Functions: `is_cantrip()`, `get_cantrip_damage_scaling()`, `get_cantrip_damage()`, etc.
  
  **Abilities System**:
  - `SkillType` enum with all 18 D&D 5e skills
  - `Skill` class for skill proficiency and expertise
  - `get_all_skills()` function to retrieve all skills
  - `SavingThrowType` enum for all 6 saving throws
  - `SavingThrow` class for saving throw mechanics
  - `make_saving_throw()` helper function with advantage/disadvantage support
  
  **Experience & Leveling**:
  - Complete `XP_LEVELS` table for levels 1-20
  - Experience functions: `get_level_from_xp()`, `get_xp_for_level()`, `get_xp_to_next_level()`, etc.
  - `calculate_proficiency_bonus()` by level
  - `get_cr_xp()` for monster XP rewards
  - `LevelUpResult` class for level up results
  - Level up system: `calculate_hp_gain()`, `perform_level_up()`, etc.
  - Ability Score Improvement (ASI) level tracking
  
  **Challenge Rating & Encounters**:
  - `ChallengeRating` class for monster difficulty
  - `EncounterDifficulty` class for encounter balance
  - `get_xp_thresholds_for_level()` for encounter difficulty by party level
  - `calculate_encounter_difficulty()` for multi-monster encounters
  - `get_appropriate_cr_range()` for balanced encounters
  
  **Multiclassing**:
  - `MulticlassRequirements` class
  - `MULTICLASS_PREREQUISITES` dictionary with all prerequisites
  - `can_multiclass_into()` and `can_multiclass_from()` functions
  - `calculate_spell_slots_multiclass()` for combined spellcaster levels
  - `get_multiclass_proficiencies()` for gained proficiencies
  - `calculate_hit_points_multiclass()` for multiclass HP
  
  **Utility Functions** (26+ new functions):
  - Dice rolling: `roll_dice()`, `roll_with_advantage()`, `roll_with_disadvantage()`
  - Modifiers: `calculate_modifier()`, `format_modifier()`
  - Combat: `calculate_ac()`, `calculate_attack_bonus()`, `calculate_save_dc()`
  - Criticals: `is_critical_hit()`, `is_critical_fail()`
  - Damage: `apply_resistance()`, `apply_vulnerability()`
  - Spell mechanics: `calculate_spell_attack_bonus()`
  - Character creation: `get_random_ability_scores()`, `get_standard_array()`
  - Physical mechanics: `calculate_carrying_capacity()`, `calculate_jump_distance()`
  
  **Game Constants**:
  - Complete `constants.py` module with 200+ game constants
  - Ability score limits, level ranges, movement speeds
  - Conditions, damage types, spell schools
  - Armor classes, weapon properties, equipment categories
  - Languages, skills, classes, races, alignments
  - Currency conversions, creature sizes, proficiency bonuses
  
  **Data Access**:
  - `DndApiClient` class for D&D 5e API access with caching
  - Methods for all resource types (monsters, spells, classes, equipment, etc.)
  - Search functionality with filters
  - `get_default_client()` and `set_default_client()` global client management
  
  **Serialization**:
  - `DndJSONEncoder` custom JSON encoder for D&D objects
  - `to_json()` and `from_json()` conversion functions
  - `save_to_file()` and `load_from_file()` for generic data
  - Character serialization: `serialize_character()`, `save_character()`, `load_character()`
  - Monster serialization: `serialize_monster()`
  - Party management: `save_party()`, `load_party()`
  - `create_backup()` for file backups

### Changed
- Updated all module `__init__.py` files to export new classes and functions
- Enhanced main package `__init__.py` with documentation comments for submodules
- Separated UI concerns from business logic classes
- Message format standardized: methods return `(messages: List[str], result)` tuples

### Documentation
- Added `docs/IMPLEMENTED_CLASSES.md` - Complete class implementation guide
- Added `docs/IMPLEMENTATION_SUMMARY.md` - Migration summary and statistics
- Created `test_new_classes.py` - Validation script for all new features
- Updated README examples with new functionality

### Statistics
- 10 new implementation files (~2,400 lines of code)
- 6 updated `__init__.py` files (~150 lines)
- 3 documentation files (~1,000 lines)
- **Total: ~3,550 lines of production code**
- **All 28 classes from dao_classes.py successfully migrated**
- **100% test success rate**

## [0.1.3] - 2026-01-05

### Fixed
- Fixed package data inclusion: monster data files (bestiary-sublist-data.json) now correctly included in distributed package
- Updated MANIFEST.in to properly include dnd_5e_core/data directory in builds

### Changed
- Excluded monster token images from PyPI distribution to meet size limits (1.3 MB vs 107 MB)
- Token images can still be downloaded separately using the token_downloader utility

## [0.1.2] - 2026-01-05

### Added
- **Publication Guides**: Complete documentation for PyPI and GitHub publication
  - `SUMMARY_SOLUTIONS.md` - Comprehensive FAQ and solutions
  - `PUBLICATION_CHECKLIST.md` - Step-by-step publication checklist
  - `PUBLICATION_EXPLAINED.md` - Detailed publication guide
  - `GITHUB_ABOUT_SETUP.md` - GitHub configuration guide
  - `ABOUT.md` - Project "About" section content
  - `INDEX.md` - Documentation navigation guide
  - `QUICK_COMMANDS.md` - Quick reference commands

### Changed
- Updated `pyproject.toml` readme format with explicit content-type
- Improved PyPI metadata for better sidebar display

### Fixed
- Fixed TypeError in test examples by adding null checks
- Clarified egg-info directory usage (not needed for publication)

## [0.1.1] - 2026-01-03

### Added
- **PyPI Metadata**: Complete metadata for PyPI publication
  - Authors and maintainers with contact emails
  - 11 keywords for better discoverability
  - 17 detailed classifiers
  - 8 project URLs (Homepage, Documentation, Issues, Changelog, etc.)
  - Proper license format for PyPI
- **GitHub Configuration**: Files for GitHub "About" section
  - `.github/ABOUT.md` - Complete project description
  - `.github/DESCRIPTION.txt` - Short description for sidebar
  - `.github/TOPICS.md` - Recommended topics/tags
  - `.github/GITHUB_ABOUT_SETUP.md` - Setup instructions
- **Documentation**: Enhanced publication documentation
  - `METADATA_SUMMARY.md` - Complete metadata overview
  - Updated `PUBLISHING.md` with PyPI and GitHub instructions

### Changed
- Updated `pyproject.toml` with complete PyPI metadata
- Improved project discoverability on PyPI

## [0.1.0] - 2025-12-24

### Added
- **MAJOR**: Integrated D&D 5e API Collections directory (26 index files)
  - All collection indexes from DnD-5th-Edition-API migrated to dnd-5e-core
  - New `dnd_5e_core.data.collections` module for managing collections
  - Auto-detection of collections directory (no manual configuration needed)
  - Compatible `populate()` function for backward compatibility
  - Convenience functions: `get_monsters_list()`, `get_spells_list()`, etc.
  - Collections README with documentation and examples
- **MAJOR**: Integrated D&D 5e JSON data directory (8.7 MB, 2000+ files)
  - All monster, spell, weapon, armor, class, and race data now included in package
  - Auto-detection of data directory (no manual configuration needed)
  - 27 categories of D&D 5e content (monsters, spells, weapons, etc.)
- Initial package structure
- Entity system (Monster, Character, Sprite)
- Race and SubRace system
- Class system with proficiencies
- Equipment system (Weapon, Armor, Potion)
- Spellcasting system with spell slots
- Combat system with actions and special abilities
- Abilities and saving throws
- Dice mechanics
- Data loader from local JSON files (migrated from API)
- JSON serialization

### Changed
- **BREAKING**: Data loader now auto-detects `dnd-5e-core/data` directory
- **IMPROVED**: `set_data_directory()` is now optional (auto-detection first)
- **IMPROVED**: Collections loader auto-detects `dnd-5e-core/collections` directory
- Data loader priority: 1) dnd-5e-core/data, 2) DnD-5th-Edition-API/data (fallback), 3) ./data
- Collections loader priority: 1) dnd-5e-core/collections, 2) DnD-5th-Edition-API/collections (fallback), 3) ./collections

### Migration Notes
- See `DATA_MIGRATION_COMPLETE.md` for full migration documentation
- All v2 game files updated to use auto-detection
- Backward compatibility maintained with fallback to old data location

## [0.1.0] - 2025-01-XX

### Added
- First alpha release
- Core D&D 5e mechanics implementation
