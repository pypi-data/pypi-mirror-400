""" """

import os


CONFIG_DIR = os.path.expanduser("~/.config/totp/")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.py")
HASH_FILE = os.path.join(CONFIG_DIR, "data.json")
SITES_TABLE = os.path.join(CONFIG_DIR, "totp.db")

LOG_DIR = os.path.expanduser("~/.local/share/totp/logs/")
LOG_LEVEL = "INFO"

BLANK_DEF = " "
NICK_DEF = "#"
SLIDER_DEF = ["█", "◣", " "]
SITE_DEF = "https://www.github.com/"
DEFAULT_FG = "white"
FANCY_SLIDER = False

ENTRY_SCHEMA = {
    "line1": [
        {"type": "nick", "width": 10, "alignment": "left", "space_after": 10},
        {
            "type": "slider",
            "width": 30,
            "alignment": "right",
        },
    ],
    "line2": [
        {"type": "site", "width": 20, "alignment": "left", "space_after": 0},
        {"type": "token", "alignment": "right", "space_before": 10},
        # {
        #     "type": "time",
        #     "precision": 0,
        #     "alignment": "right",
        #     "space_before": 1
        # },
    ],
}

STATUSLINE_SCHEMA = {
    "line1": [
        {"type": "time", "format": "%H:%M:%S", "alignment": "left"},
        {"type": "slider", "width": 10, "alignment": "right", "space_after": 2},
    ],
}
