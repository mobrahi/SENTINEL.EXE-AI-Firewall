import pygame

# --- Window Settings ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TILE_SIZE = 40  # Everything in the game will be on a 40x40 grid

# --- Cyber-Security Color Palette ---
# Using HEX codes for that "Terminal" look
BG_COLOR = (10, 15, 20)          # Deep Midnight
GRID_COLOR = (20, 30, 40)        # Subtle Grid lines
TEXT_COLOR = (0, 255, 150)       # Terminal Green
ACCENT_COLOR = (0, 229, 255)     # Cyber Cyan

# --- Entity Colors (Temporary until we use AI for sprites) ---
CORE_COLOR = (255, 0, 100)       # Magenta (The Core you protect)
ENEMY_COLOR = (255, 50, 50)      # Virus Red
TOWER_COLOR = (0, 150, 255)      # Protocol Blue

# --- Game Balance ---
STARTING_RESOURCES = 100         # "CPU Cycles" (Your currency)
CORE_HEALTH = 20                 # "Integrity %"

# --- Fallback Lore (Responsible AI Robustness) ---
LOCAL_LORE_BACKUP = [
    "LOCAL_INTEL: Segmented logic bombs detected in Sector 7G.",
    "ERROR 404_INTEL: Virus signature obscured. Deploying standard protocols.",
    "SYSTEM_LOG: Breach detected. Integrity subroutines failing.",
    "CORE_ALERT: Sentient malware attempting to bypass encryption.",
    "PROTOCOL_ALPHA: Security cycles low. Expect heavy packet loss."
]