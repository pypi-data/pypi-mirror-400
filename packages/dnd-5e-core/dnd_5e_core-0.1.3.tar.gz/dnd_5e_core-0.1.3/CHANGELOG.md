# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-01-05

### Fixed
- Fixed package data inclusion: monster data files (bestiary-sublist-data.json) now correctly included in distributed package
- Updated MANIFEST.in to properly include dnd_5e_core/data directory in builds

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
