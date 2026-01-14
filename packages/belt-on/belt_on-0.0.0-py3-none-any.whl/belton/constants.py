# src/belton/constants.py

from pathlib import Path


# ---------
# constants
# ---------

PROG_TITLE = "Belt-On"
PROG_NAME = "belt-on"
SETTINGS_FILENAME = "settings.toml"
DEFAULT_LANG = "en-US"
DEFAULT_CLEAN_CACHE = True

# Directory containing TOML data files
GAME_DATA_DIR = Path(__file__).parent / "game_data"
