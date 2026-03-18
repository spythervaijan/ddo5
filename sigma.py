#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTIMATE INSTAGRAM GROUP CHAT SPAMMER – RENAME AFTER 20 MESSAGES
- Every 20 messages (total across all tasks) → group name changes
- Superfast messaging (no delays between messages)
- Handles 10+ GCs simultaneously
"""

import asyncio
import logging
import random
import os
import sys
import subprocess
from itertools import count
from cfonts import render
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# ==================== AUTO INSTALL DEPENDENCIES ====================
def install_deps():
    try:
        import playwright
        from cfonts import render
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "python-cfonts", "pyfiglet"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

install_deps()

# ==================== COLORS & BANNER ====================
COLORS = {
    'red': '\033[1;31m',
    'green': '\033[1;32m',
    'yellow': '\033[1;33m',
    'cyan': '\033[36m',
    'blue': '\033[1;34m',
    'reset': '\033[0m',
}

BANNER_TEXT = "SAMM GODZZ"
TITLE_TEXT = "@politician.sam©"

def banner():
    os.system("cls" if os.name == "nt" else "clear")
    try:
        print(render(BANNER_TEXT, colors=["yellow", "blue"]))
    except:
        print(BANNER_TEXT)
    print(COLORS['blue'] + TITLE_TEXT + COLORS['reset'])
    print(COLORS['yellow'] + "𓆰⚚🎀࿐SAMM GODZZ PRESET『𓆩🦅𓆪』." + COLORS['reset'])


# ==================== YOUR ORIGINAL MESSAGE TEMPLATES (full) ====================
UFO_BASES = [
  "<HATER>»C»»H»»U»»D»»»»  𓆟𓆝 𓆟𓆝 𓆟 ”˜  𓆟𓆝 𓆟𓆝 𓆟 ˜”*𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟  𓆟𓆝 ⋆.•°*”˜  𓆟𓆝 𓆟𓆝 𓆟𓆟𓆝𓆟 ˜”*°•.𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟  𓆟𓆝 ⋆°࿐< HATER>»C»»H»»U»»D»»»»  𓆟𓆝 𓆟𓆝 𓆟 ",
  "<HATER>»C»»H»»U»»D»»»»  𓆟𓆝 𓆟𓆝 𓆟 ”˜  𓆟𓆝 𓆟𓆝 𓆟 ˜”*𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟  𓆟𓆝 ⋆.•°*”˜  𓆟𓆝 𓆟𓆝 𓆟𓆟𓆝𓆟 ˜”*°•.𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟𓆝𓆟  𓆟𓆝 ⋆°࿐< HATER>»C»»H»»U»»D»»»»  𓆟𓆝 𓆟𓆝 𓆟 "
]
REACTION_TEMPLATES = [
    "HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                       HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                         HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                         HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                         HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                         HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                         HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                         HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                         HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                         HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                       HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂                        HATER ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅɴᴇ ᴋᴇ ʙᴀᴀᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴇᴀᴄᴛɪᴏɴ ꧁⎝ 𓆩༺😳༻𓆪 ⎠꧂        " * 8,
    " < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ  👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐                   👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ < KING K H8R  > Tᴍᴋᴄ ᴘᴇ ɢᴜ 👻╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰╰࿐ "
]
HINDI_ABUSES = [
    "[HATER ] तेरी BHEN रंडी\n 🦢                              [HATER ] तेरी BHEN रंडी\n 🦢                              [HATER ] तेरी BHEN रंडी\n 🦢                              [HATER ] तेरा बाप छक्का \n 🦢                           [HATER ] तेरी माँ रंडी\n 🠠                                   [HATER ] तू हिजड़ा \n 🦢                                         [HATER ] तेरी माँ की चूत खा लू \n 🦢               [HATER ] तेरी बहन का लन्ड  \n 🦢                         [HATER ] तेरा बाप टकला  \n 🦢                             [HATER ] CVR KR ? \n                                                    NC SCRIPT BY SAM !! 🦢                                          [HATER ] तेरी BHEN रंडी\n 🦢                              [HATER ] तेरी BHEN रंडी\n 🦢                              [HATER ] तेरी BHEN रंडी\n 🦢                              [HATER ] तेरा बाप छक्का \n 🦢                           [HATER ] तेरी माँ रंडी\n 🠠                                   [HATER ] तू हिजड़ा \n 🦢                                         [HATER ] तेरी माँ की चूत खा लू \n 🦢               [HATER ] तेरी बहन का लन्ड  \n 🦢                         [HATER ] तेरा बाप टकला  \n 🦢                             [HATER ] CVR KR ? \n                                                    NC SCRIPT BY SAM !! 🦢", 
    # ... second abuse template
]
DRAKE_TEMPLATES = ["SAM H8R 𝙱𝙾𝙻𝙰𝙰 𝙺�________� 𝙿𝚁) �𝚆𝙰𝚄 SAM H8R �𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺� H8R 𝙱𝙾𝙻𝙴 𝚃𝙺𝙾 𝙼�___________________/ SAM�𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙷 (𝙻𝙾�𝚁𝙰 𝙺𝙰𝚁𝚆𝙰_/ 𝙺𝙾�8R 𝙱𝙾𝙼𝙰𝙰 𝙺_________________________/ SAM H�𝙷𝙴 𝙿𝙰𝚁?💤🀄__________________________/ SAM H�𝙷𝙴 𝙿𝙰𝚁?💤🀄__________________________/ SAM H�𝙷𝙴 𝙿𝙰𝚁?💤🀄__________________________/ SAM H�𝙷𝙴 𝙿𝙰𝚁?💤🀄__________________________/ SAM H�𝙷𝙴 𝙿𝙰𝚁?💤🀄__________________________/ SAM H�𝙷𝙴 𝙿𝙰𝚁?💤🀄__________________________/ SAM H�𝙷𝙴 𝙿𝙰𝚁?💤🀄__________________________/ SAM H�𝙷𝙴 𝙿𝙰𝚁?💤🀄__________________________/ SAM H�𝙷𝙴 𝙿𝙰𝚁?💤�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰_/ SAM H8R 𝙱𝙾�𝚁?💤🀄_________________ HATER � 𝙰𝚆𝙰𝙷𝙴 𝙿�𝙴 𝚃𝙾�_________𝙴 𝙿𝚁) HATER � 𝙰𝚆𝙰𝙷𝙴 𝙿𝙰𝚁?💤🀄_ (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 �𝚁?💤🀄_________𝙴 𝙿𝚁)�HATER � 𝙺𝙾𝚃� 𝙱𝙾𝙻𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰�𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰�𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰�𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰�𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰�𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰�𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰�𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁_____/ SAM H�𝙷𝙱𝙾𝙻𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴_______�_____/ SAM H8R 𝙱𝙾�𝙰𝚁� 𝙺𝙾 �___________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________", "SAM H8R 𝙱𝙾𝙻𝙴 𝚃𝙾𝙾 𝙼𝚄𝙹________HATER 𝚁� SAM H8R 𝙱𝙾𝙻𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁� SAM H8R 𝙱𝙾𝙻𝙴 𝚃𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 �________𝚁𝙰𝚆𝙰H8R 𝙱𝙾𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆ER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 𝙺𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 �𝙻𝙴 𝚃𝙾𝙷 (𝙻�𝙹𝚁𝙰 __𝙰𝚁𝚆 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙰𝙰 �_______𝙳𝙴_______________/ SAM H8R 𝙱𝙾𝙻𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HAT___/ SAM�𝚃  𝙱� 𝙼𝙰𝙰 𝙺𝙾 𝙼�𝙳𝙴 𝙿�𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿�𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁� SAM�𝙷𝙴 𝙿𝙰𝚁?💤�𝙷 (𝙻𝙾𝙳𝙴 𝙿�𝙰𝚁𝚆𝙰𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤�𝙾 𝙼𝚄𝙹𝚁𝙰 𝙺𝙰𝚁𝚆𝙰𝚄 𝙺𝙾�8R 𝙱𝙾𝙼𝙰 𝚃𝙾________________________𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄_________________________𝚄 𝙺𝚃𝙷𝙴 𝙿�𝙴 𝚃𝙾𝙷 (𝙻𝙾�𝚁𝙰 𝙺 HATER _�𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿𝚁) HATER 𝚁𝙰𝚆𝙰𝚃 𝙺𝙸 𝙼𝙴 𝚃𝙾𝙷 (𝙻𝙾𝙳𝙴 𝙿�_________/ SAM H8R 𝙱𝙾𝙻𝙴 𝚃𝙾_______�_______________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________�𝚄 𝙺𝙾𝚃𝙷𝙴 𝙿𝙰𝚁?💤🀄________________________"]  # all your drake templates
YUVRJ_TEMPLATES = ["¿HATER? बाप को     ¿HA_______/___________________________________बाप को फील कर चुदकड़😈____________________________बाप को फील कर चुदकड़😈____________________________बाप को फील कर चुदकड़😈____________________________बाप को फील कर चुदकड़😈______________________________/    ______________/        ¿________ चुदकड़�प को फील क______________फील कर चुदक_______________/        ¿HATER? बाप को फील कर चुदक_______________/        ¿HATER? बाप को फील कर चुदक_______________/        ¿HATER? बाप को फील कर चुदक_______________/        ¿HATER? बाप को फील कर चुदक_______________/        ¿HATER? बाप को फील कर चुदक_______________/        ¿HATER? बाप को फील कर चुदकड़😈______________________________/        ¿HATER? बाप को फील कर चुदकड़😈_को फील कHATER? ब_/      ____________________   ¿HATER? ब_/        ¿HATER? ब😈______________________________/        ¿HATER? ब😈______________________________/        ¿HATER? ब😈______________________________/        ¿HATER? ब😈______________________________/        ¿HATER? ब😈______________________________/        ¿HATER? बाप को फील कर चुदकड़😈______________________________/     ________________      ¿H________/        ¿HATER? बाप को फील कर चुदकड़😈______________________________/  ो फील कर चुदकड़😈______________________________/  ो फील कर चुदकड़😈______________________________/        ¿HATER? बाप को फील कर चुदकड़😈______________________________चुदकड़__________कर चुदकडबाप को फील कर चुद___________________________________/        ¿HATER? बा�______________________________/        ¿HATER? बाप को फील_______________________/        ¿HATER? बाप को फील_______________________/        ¿HATER? बाप को फील_______________________/        ¿HATER? बाप को फील कर चुदक बाप को   ल कर चुदकड़😈______________________________/      ल कर चुदकड़😈______________________________/      "]
MONSTER_TEMPLATES = ["¿HATER? बहन के________रह 🍑 __े टके औक______________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में रह 🍑___       ा______________  ________बहन क___     ात ATER? बहन के टके औकात मेER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह ¿HATER? बहन के टके औका¿HATER? बहन के टके औकात ATER? बहन के ___ औकात मेTER? बहन__/        ¿HATER? बहन के टके औक ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में _____________/        ¿HATER? बहन के टके औकात में रह 🍑___________त में रह 🍑_____________ATं रह 🍑_______ औकात मेER?  🍑_के टके औ  ¿HATER? बहन के टके औका¿HATER? _____/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह __________/        ¿HATER? बहन के टके औकात में रह " ]
SAM_TEMPLATES = [ "𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼HATER                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　.　　　　　　*𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼HATER                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　.　　　　　　*𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼HATER                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　.　　　　　　*𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼HATER                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　.　　　　　　*𝐃ᴇʟʜɪ 𝐌ᴀɪɴ  𝐇ᴀ 𝐐ᴜᴛᴜʙ 𝐌ɪɴᴀʀ 🗼HATER                           𝐊ɪ 𝐌ᴀᴀ 𝐁ᴀᴅɪ 𝐂ʜɪɴᴀʀ 💗😜　　　　　　　　　‍ ‍　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　 ✦　˚　　　　　　　　　　　　　　‍ ‍ ,　　　*　　 .　　　　　.　　　　　　　　　　　*🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　.　　　　.　　　　.　　　 🌕　　　　　　　　　　　.　　　　　　　🚀　　　˚　　　　　　　　　　　.　　　　　　" ]
HUGE_MESSAGE = r"━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃Ꭿ          ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃Ꭿ          ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃Ꭿ          ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃Ꭿ          ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃Ꭿ          ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃Ꭿ          ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃Ꭿ          ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃Ꭿ   " * 8

ARUSH_TEMPLATES = []   # prevent NameError

# ==================== TEMPLATE SEPARATION ====================
# For rename: use all templates (including Hindi abuses)
ALL_RENAME_TEMPLATES = (
    UFO_BASES + REACTION_TEMPLATES + HINDI_ABUSES + DRAKE_TEMPLATES +
    YUVRJ_TEMPLATES + MONSTER_TEMPLATES + SAM_TEMPLATES + ARUSH_TEMPLATES
)

# For messages: use all templates EXCEPT Hindi abuses
MESSAGE_TEMPLATES = (
    UFO_BASES + REACTION_TEMPLATES + DRAKE_TEMPLATES +
    YUVRJ_TEMPLATES + MONSTER_TEMPLATES + SAM_TEMPLATES + ARUSH_TEMPLATES
)
MESSAGE_TEMPLATES.append(HUGE_MESSAGE)

# ==================== GLOBAL STATS ====================
success_count = 0      # successful renames
msg_count_total = 0    # messages sent
fail_count = 0         # failed operations
used_names = set()     # ensure unique names
name_counter = count(1)
lock = asyncio.Lock()

def generate_name(prefix):
    while True:
        base = random.choice(ALL_RENAME_TEMPLATES).strip()
        # Replace both "HATER" and "{target}" with the prefix
        base = base.replace("HATER", prefix).replace("{target}", prefix)
        suffix = next(name_counter)
        name = f"{base} 🔥_{suffix}"
        if name not in used_names:
            used_names.add(name)
            return name

def print_stats():
    sys.stdout.write(f"\r{COLORS['green']}Renames: {success_count}{COLORS['reset']} {COLORS['blue']}Msgs: {msg_count_total}{COLORS['reset']} {COLORS['red']}Failed: {fail_count}{COLORS['reset']}")
    sys.stdout.flush()

# ==================== HELPER FUNCTIONS WITH RETRIES ====================
async def safe_click(page, selector, timeout=5000, retries=2):
    for attempt in range(retries):
        try:
            await page.wait_for_selector(selector, state='visible', timeout=timeout)
            await page.click(selector, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(0.5)
    return False

async def safe_fill(page, selector, value, timeout=5000, retries=2):
    for attempt in range(retries):
        try:
            await page.wait_for_selector(selector, state='visible', timeout=timeout)
            await page.fill(selector, value, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(0.5)
    return False

# ==================== RENAME FUNCTION (uses current page) ====================
async def perform_rename(page, prefix):
    """Perform group name change on the given page."""
    global success_count, fail_count
    try:
        # Gear icon
        gear_selector = '.html-div > .x1i10hfl:nth-child(3) .x1lliihq'
        await safe_click(page, gear_selector, timeout=8000)
        await page.wait_for_timeout(300)

        # Change button
        change_btn_selector = 'div.x10w6t97'
        await page.wait_for_selector(change_btn_selector, state='visible', timeout=8000)

        # Input field
        input_selector = 'input.x96k8nx'
        await page.wait_for_selector(input_selector, state='visible', timeout=8000)

        # Save button
        save_btn_selector = 'div.x9bdzbf'
        await page.wait_for_selector(save_btn_selector, state='visible', timeout=8000)

        name = generate_name(prefix)

        await safe_click(page, change_btn_selector, timeout=4000)
        await page.wait_for_timeout(200)

        await page.click(input_selector, click_count=3, timeout=4000)
        await safe_fill(page, input_selector, name, timeout=4000)
        await page.wait_for_timeout(100)

        disabled = await page.get_attribute(save_btn_selector, "aria-disabled")
        if disabled == "true":
            async with lock:
                fail_count += 1
                print_stats()
            return False

        await safe_click(page, save_btn_selector, timeout=4000)
        async with lock:
            success_count += 1
            print_stats()
        return True

    except Exception as e:
        async with lock:
            fail_count += 1
            print_stats()
        return False

# ==================== MESSAGE LOOP – SUPERFAST + RENAME AFTER 20 MSGS ====================
async def message_loop(context, dm_url, target, semaphore,
                       group_counter, counter_lock, rename_lock):
    global msg_count_total, fail_count
    while True:
        async with semaphore:
            page = await context.new_page()
            try:
                await page.goto(dm_url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(500)

                msg_selectors = [
                    'div[aria-label="Message"][role="textbox"]',
                    'div[role="textbox"][contenteditable="true"]',
                    'div[contenteditable="true"]'
                ]
                msg_selector = None
                for sel in msg_selectors:
                    if await page.locator(sel).count() > 0:
                        msg_selector = sel
                        break
                if not msg_selector:
                    raise Exception("Message input not found")

                await page.wait_for_selector(msg_selector, state='visible', timeout=15000)

                while True:
                    try:
                        # --- Send one message ---
                        base_msg = random.choice(MESSAGE_TEMPLATES)
                        msg = base_msg.replace("{target}", target).replace("HATER", target)

                        await safe_fill(page, msg_selector, msg, timeout=4000)
                        await page.wait_for_timeout(10)          # minimal
                        await page.keyboard.press("Enter")
                        async with lock:
                            msg_count_total += 1
                            print_stats()

                        # --- Check if we need to rename (after every 20 messages total for this group) ---
                        need_rename = False
                        async with counter_lock:
                            group_counter[dm_url] += 1
                            if group_counter[dm_url] >= 20:
                                need_rename = True
                                # temporarily release counter lock while we rename
                        if need_rename:
                            async with rename_lock:   # only one rename at a time per group
                                # Re-acquire counter lock to check again (in case another task already renamed)
                                async with counter_lock:
                                    if group_counter[dm_url] >= 20:
                                        # Perform rename on the same page
                                        rename_success = await perform_rename(page, target)
                                        # Reset counter regardless of success/failure
                                        group_counter[dm_url] = 0
                                    else:
                                        # someone else already did it
                                        pass
                            # after rename, continue messaging immediately

                    except Exception as e:
                        async with lock:
                            fail_count += 1
                            print_stats()
                        break   # error → restart page

            except Exception as e:
                async with lock:
                    fail_count += 1
                    print_stats()
            finally:
                await page.close()
            await asyncio.sleep(1)

# ==================== MAIN ====================
async def main():
    banner()
    print(COLORS['cyan'] + "\n⚡ SUPERFAST + RENAME EVERY 20 MESSAGES ⚡" + COLORS['reset'])

    session_id = input("Session ID: ").strip()
    if not session_id:
        print(COLORS['red'] + "❌ Session ID required!" + COLORS['reset'])
        return

    urls_input = input("Group chat URLs (comma separated OR path to .txt file): ").strip()
    dm_urls = []
    if os.path.isfile(urls_input):
        with open(urls_input, 'r', encoding='utf-8') as f:
            dm_urls = [line.strip() for line in f if line.strip()]
        print(COLORS['green'] + f"📁 Loaded {len(dm_urls)} URLs from file." + COLORS['reset'])
    else:
        dm_urls = [url.strip() for url in urls_input.split(",") if url.strip()]

    if not dm_urls:
        print(COLORS['red'] + "❌ No valid URLs provided!" + COLORS['reset'])
        return

    target_prefix = input("Target Prefix (default 'SAM'): ").strip() or "SAM"

    try:
        msg_tasks_per_group = int(input("Message tasks per group (1-10, default 5): ").strip() or "5")
        max_concurrent = int(input("Max concurrent pages (10-500, default 200): ").strip() or "200")
    except ValueError:
        msg_tasks_per_group, max_concurrent = 5, 200

    msg_tasks_per_group = max(1, min(10, msg_tasks_per_group))
    max_concurrent = max(10, min(500, max_concurrent))

    semaphore = asyncio.Semaphore(max_concurrent)

    # Shared state per group
    group_counter = {url: 0 for url in dm_urls}
    counter_locks = {url: asyncio.Lock() for url in dm_urls}
    rename_locks = {url: asyncio.Lock() for url in dm_urls}

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        await context.add_cookies([{
            "name": "sessionid",
            "value": session_id,
            "domain": ".instagram.com",
            "path": "/",
            "secure": True,
            "httpOnly": True
        }])

        tasks = []
        for url in dm_urls:
            for _ in range(msg_tasks_per_group):
                tasks.append(asyncio.create_task(
                    message_loop(context, url, target_prefix, semaphore,
                                 group_counter, counter_locks[url], rename_locks[url])
                ))

        print(f"\n{COLORS['yellow']}🚀 Total immortal tasks: {len(tasks)} (Messages only, rename after 20 msgs total per group)")
        print(f"Max concurrent pages: {max_concurrent}{COLORS['reset']}\n")
        print("🔥 The script will now run forever. Press Ctrl+C to stop.\n")

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print(f"\n{COLORS['red']}⚠️ Interrupted by user{COLORS['reset']}")
        finally:
            await browser.close()

    print(f"\n{COLORS['green']}✅ Finished. Final stats: Renames: {success_count}, Messages: {msg_count_total}, Failed: {fail_count}{COLORS['reset']}")

if __name__ == "__main__":
    asyncio.run(main())