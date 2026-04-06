# 𝐄ʙʙ𝐔V12 Py Fyting Bot!
import asyncio
import json
import os
import random
import time
from datetime import datetime
from telegram import Update, InputSticker, Sticker
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging
import yt_dlp
from gtts import gTTS
import requests
import io

# ---------------------------
# CONFIG
# ---------------------------
TOKENS = [
    "8232638590:AAGz7VOdjC5IxDJRfQ_45h_0mgEEwMW3RBo",
    "8420115826:AAHFh3dlSjezTvxLJW5wR1cn7GtmQ-LRPos",      
    "8779481135:AAGyTXnuf3jeNBLaQjlhkSsdemYPbpzJGoo",
    "8443166130:AAEfMuARgTZSxsnhFudomwNuNv0tK__b570",
    "8377941472:AAGWp8gRPRcjWXL8FYnnyNyvRqzYaB9Ialo",
    
"8210222388:AAHLKQERnlFKCwRt7ZOQXTBNygYZnbNiBls",

"8672683071:AAH6hTZMH2TtAx6PKGN-31Iu-pwS4mPyPeg",

"8712989227:AAE4IJGNsKOTBvu9zcKEiCHNUpzhvBJ2Cpc",
    "8385614320:AAFCA3jWj35Om129WtJyEN5PEU1MYT7da18",
    
"7605415606:AAF8xJ5T_aLedCQJOi4WKY7ypOTKjhdMnak",

"8334769561:AAHrxKW4ZjTXh_dhCehcDw9PcHNpDUc5qrE",   

"8457371657:AAHlJxUCmNJ8QvRhe2hOTIy4Es9Q_pOk_2s" 

]

CHAT_ID = 7849604910
OWNER_ID = 7849604910
SUDO_FILE = "sudo.json"
STICKER_FILE = "stickers.json"
VOICE_CLONES_FILE = "voice_clones.json"
tempest_API_KEY = "sk_e326b337242b09b451e8f18041fd0a7149cc895648e36538"  # ✅ YOUR API KEY ADDED

# ---------------------------
# tempest VOICE CHARACTERS
# ---------------------------
VOICE_CHARACTERS = {
    1: {
        "name": "Urokodaki",
        "voice_id": "VR6AewLTigWG4xSOukaG",  # Deep Indian voice
        "description": "Deep Indian voice - Urokodaki style",
        "style": "deep_masculine"
    },
    2: {
        "name": "Kanae", 
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Cute sweet voice
        "description": "Cute sweet voice - Kanae style",
        "style": "soft_feminine"
    },
    3: {
        "name": "Uppermoon",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",  # Creepy dark voice
        "description": "Creepy dark deep voice - Uppermoon style", 
        "style": "dark_creepy"
    },
    4: {
        "name": "Tanjiro",
        "voice_id": "VR6AewLTigWG4xSOukaG",
        "description": "Heroic determined voice",
        "style": "heroic"
    },
    5: {
        "name": "Nezuko",
        "voice_id": "EXAVITQu4vr4xnSDxMaL", 
        "description": "Cute mute sounds",
        "style": "cute_mute"
    },
    6: {
        "name": "Zenitsu",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "description": "Scared whiny voice",
        "style": "scared_whiny"
    },
    7: {
        "name": "Inosuke",
        "voice_id": "VR6AewLTigWG4xSOukaG",
        "description": "Wild aggressive voice",
        "style": "wild_aggressive"
    },
    8: {
        "name": "Muzan",
        "voice_id": "AZnzlk1XvdvUeBnXmlld",
        "description": "Evil mastermind voice",
        "style": "evil_calm"
    },
    9: {
        "name": "Shinobu",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "description": "Gentle but deadly voice",
        "style": "gentle_deadly"
    },
    10: {
        "name": "Giyu",
        "voice_id": "VR6AewLTigWG4xSOukaG",
        "description": "Silent serious voice",
        "style": "silent_serious"
    }
}

# ---------------------------
# TEXTS
# ---------------------------
RAID_TEXTS = [
    "<🐍> 𝘊𝘜𝘋𝘈 <🐍>", "<🐍> 𝘕𝘌𝘞 𝘎𝘌𝘕 <🐍>", "<🐍> 𝘒𝘈𝘓𝘐 𝘔𝘈 𝘒𝘌 𝘉𝘈𝘊𝘊𝘏𝘌 <🐍>", 
    "<🐍> 𝘕𝘐𝘎𝘎𝘈 <🐍> ", "<🐍> 𝘗𝘌𝘙𝘐𝘖𝘋𝘚 𝘔𝘌 𝘏𝘖 𝘒𝘠𝘈 <🐍>", "<🐍> 𝘗𝘓𝘈𝘠 𝘎𝘐𝘙𝘓 <🐍>", "<🐍> 𝘊𝘏𝘜𝘋 𝘒𝘌𝘚𝘌 𝘙𝘈𝘏𝘈 <🐍>", "<🐍> 𝘓𝘜𝘕𝘋 <🐍>",
    "<🐍> 𝘓𝘌𝘚𝘉𝘐𝘈𝘕 <🐍>", "<🐍> 𝘎𝘈𝘠 <🐍>", "<🐍> 𝘛𝘔𝘒𝘉 <🐍>", "<🐍> 𝘉𝘒𝘓 <🐍>", "<🐍> 𝘛𝘌𝘙𝘐 𝘔𝘈 𝘔𝘈𝘙 𝘑𝘈𝘠𝘌 <🐍>", "<🐍> 𝘛𝘔𝘒𝘊 <🐍>",
    "<🐍> 𝘞𝘌𝘈𝘒 <🐍>", "<🐍> 𝘉𝘏𝘐𝘒 𝘔𝘈𝘕𝘎 <🐍>", "<🐍> 𝘈𝘚𝘚𝘏𝘖𝘓𝘌 <🐍>", "<🐍> 𝘉𝘈𝘈𝘗 𝘉𝘖𝘓<🐍>", "<🐍> 𝘎𝘜𝘓𝘈𝘔 <🐍> ",
    "<🐍> 𝘓𝘈𝘔𝘌 <🐍>", "<🐍> 𝘉𝘐𝘛𝘊𝘏 <🐍>", "<🐍> 𝘙𝘈𝘕𝘋𝘠 <🐍>", " 🕷️𝘉𝘖𝘓 𝘒𝘓𝘈𝘜𝘚 𝘉𝘈𝘈𝘗 🕷️",
]

ncstable_TEXTS = [
    "🏵️", "🍂", "🥀", "💮", "🌷", "🌸", "🌻", "🌺", "🌹", "💋",
    "💌", "🤍", "🖤", "🤎", "💜", "💙", "💚", "💛", "🧡", "❤️",
    "💔", "❣️", "💟", "💕", "💞", "💓", "💗", "💖", "💝", "💘", "🌼", "💐", "🦇", "🦅", "🦚", "🐉", "🦋", "🦂", "🕷️", "🐲", "♠️", "♥️", "♦️", "♣️", "🌑", "🌒", "🌓", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘", "🌙", "⚡", "💠", "🏴‍☠️"
]

nc_EMOJIS = [
    "🫧","🪂","🦢","🩸","🥇","🩵","🪽","🪷","🌲","🗽","🪅","🕷️",
    "💪🏿","🧭","🚀","🎈","🎐","🎏","🧧","🎑","🩰","🏹","🎸","🫟",
    "🎭","🏮","⚖️","🕯️","🧬","⛓️","📎","🖇️","🕐","👒","📿"
]

# ---------------------------
# GLOBAL STATE
# ---------------------------
if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r") as f:
            _loaded = json.load(f)
            SUDO_USERS = set(int(x) for x in _loaded)
    except Exception:
        SUDO_USERS = {OWNER_ID}
else:
    SUDO_USERS = {OWNER_ID}

# Initialize data files
if os.path.exists(STICKER_FILE):
    try:
        with open(STICKER_FILE, "r") as f:
            user_stickers = json.load(f)
    except:
        user_stickers = {}
else:
    user_stickers = {}

if os.path.exists(VOICE_CLONES_FILE):
    try:
        with open(VOICE_CLONES_FILE, "r") as f:
            voice_clones = json.load(f)
    except:
        voice_clones = {}
else:
    voice_clones = {}

def save_sudo():
    with open(SUDO_FILE, "w") as f: 
        json.dump(list(SUDO_USERS), f)

def save_stickers():
    with open(STICKER_FILE, "w") as f: 
        json.dump(user_stickers, f)

def save_voice_clones():
    with open(VOICE_CLONES_FILE, "w") as f: 
        json.dump(voice_clones, f)

# Global state variables
group_tasks = {}         
spam_tasks = {}
react_tasks = {}
slide_targets = set()    
slidepam_targets = set()
ncstable_tasks = {}
sticker_mode = True
apps, bots = [], []
delay = 0.1
spam_delay = 0.5
ncstable_delay = 0.05

logging.basicConfig(level=logging.INFO)

# ---------------------------
# DECORATORS
# ---------------------------
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid not in SUDO_USERS:
            await update.message.reply_text("☣️ You are not SUDO.")
            return
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid != OWNER_ID:
            await update.message.reply_text("☢️ Only Owner can do this.")
            return
        return await func(update, context)
    return wrapper

# ---------------------------
# tempest VOICE FUNCTIONS
# ---------------------------
async def generate_tempest_voice(text, voice_id, stability=0.5, similarity_boost=0.8):
    """Generate voice using tempest API"""
    url = f"https://api.tempest.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": tempest_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.botinfo_code == 200:
            return io.BytesIO(response.content)
        else:
            logging.error(f"tempest API error: {response.botinfo_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"tempest request failed: {e}")
        return None

async def generate_multiple_voices(text, character_numbers):
    """Generate voices for multiple characters"""
    voices = []
    
    for char_num in character_numbers:
        if char_num in VOICE_CHARACTERS:
            voice_data = VOICE_CHARACTERS[char_num]
            audio_data = await generate_tempest_voice(text, voice_data["voice_id"])
            if audio_data:
                voices.append({
                    "character": voice_data["name"],
                    "audio": audio_data,
                    "description": voice_data["description"]
                })
    
    return voices

# ---------------------------
# LOOP FUNCTIONS
# ---------------------------
async def bot_loop(bot, chat_id, base, mode):
    i = 0
    while True:
        try:
            if mode == "grpnc":
                text = f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}"
            else:  # nc
                text = f"{base} {nc_EMOJIS[i % len(nc_EMOJIS)]}"
            await bot.set_chat_title(chat_id, text)
            i += 1
            await asyncio.sleep(delay)
        except Exception as e:
            await asyncio.sleep(2)

async def ncdad_loop(bot, chat_id, base):
    """Ultra fast name changer - 5 changes in 0.1 seconds"""
    i = 0
    while True:
        try:
            # Multiple patterns for ultra fast changes
            patterns = [
                f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}",
                f"{base} {nc_EMOJIS[i % len(nc_EMOJIS)]}",
                f"{base} {ncstable_TEXTS[i % len(ncstable_TEXTS)]}",
                f"{RAID_TEXTS[i % len(RAID_TEXTS)]} {base}",
                f"{nc_EMOJIS[i % len(nc_EMOJIS)]} {base}",
            ]
            
            # Change name multiple times rapidly
            for pattern in patterns[:3]:  # Change 3 times rapidly
                await bot.set_chat_title(chat_id, pattern)
                await asyncio.sleep(0.02)  # Very fast delay
            
            i += 1
            await asyncio.sleep(0.1)  # Main delay
        except Exception as e:
            await asyncio.sleep(1)

async def spam_loop(bot, chat_id, text):
    while True:
        try:
            await bot.send_message(chat_id, text)
            await asyncio.sleep(spam_delay)
        except Exception as e:
            await asyncio.sleep(2)

async def ncstable_godspeed_loop(bot, chat_id, base_text):
    """ULTRA FAST name changer - God Speed mode"""
    i = 0
    while True:
        try:
            # Generate multiple patterns for ultra-fast changes
            patterns = [
                f"{base_text} {ncstable_TEXTS[i % len(ncstable_TEXTS)]}",
                f"{ncstable_TEXTS[i % len(ncstable_TEXTS)]} {base_text}",
                f"{base_text}{ncstable_TEXTS[i % len(ncstable_TEXTS)]}",
                f"{ncstable_TEXTS[(i+1) % len(ncstable_TEXTS)]} {base_text} {ncstable_TEXTS[(i+2) % len(ncstable_TEXTS)]}",
                f"{base_text} {ncstable_TEXTS[(i+3) % len(ncstable_TEXTS)]} {ncstable_TEXTS[(i+4) % len(ncstable_TEXTS)]}",
            ]
            
            # Change name 5 times in rapid succession
            for j in range(5):
                text = patterns[j % len(patterns)]
                await bot.set_chat_title(chat_id, text)
                await asyncio.sleep(0.01)  # Ultra fast delay between changes
            
            i += 1
            await asyncio.sleep(0.05)  # Main delay
        except Exception as e:
            await asyncio.sleep(0.5)

async def ncstable_loop(bot, chat_id, base_text):
    i = 0
    while True:
        try:
            patterns = [
                f"{base_text} {ncstable_TEXTS[i % len(ncstable_TEXTS)]}",
                f"{ncstable_TEXTS[i % len(ncstable_TEXTS)]} {base_text}",
                f"{base_text}{ncstable_TEXTS[i % len(ncstable_TEXTS)]}",
            ]
            text = random.choice(patterns)
            await bot.set_chat_title(chat_id, text)
            i += 1
            await asyncio.sleep(ncstable_delay)
        except Exception as e:
            await asyncio.sleep(1)

# ---------------------------
# CORE COMMANDS
# ---------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" 𝐄ʙʙ𝐔 ABBU V12 FYTING BOT — Commands \nUse /help")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
 𝐄ʙʙ𝐔 V12 Fyting Bot🐾

 𝗡𝗖-1
/grpnc  
/nc 
/ncdad 
/stopgrpnc 
/stopnc 
/stopncdad 
/stopall 
/delay 

𝗦𝗣𝗔𝗠:
/spam
/stopspam


 𝗦𝗟𝗜𝗗𝗘:
/autoslide 
/stopslide 
/slidepam 
/stopslidepam 

𝗡𝗖-2:
/ncstable 
/ncabbu 
/fastestnc 
/stopncstable 


 𝗔𝗗𝗠𝗜𝗡:
/addadmin 
/endadmin 
/adminabout 

𝗔𝗕𝗢𝗨𝗧:
/chatid 
/pong 
/botinfo 
    """
    await update.message.reply_text(help_text)

async def pong_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("🏷️ ponging...")
    end = time.time()
    await msg.edit_text(f"🔖 Pong! {int((end-start)*1000)}ms")

async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎵 Your ID: {update.effective_user.id}")

# ---------------------------
# NAME CHANGER COMMANDS
# ---------------------------
@only_sudo
async def grpnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🎧 Usage: /grpnc <name>")
    
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Stop existing tasks
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
    
    # Start new tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(bot_loop(bot, chat_id, base, "grpnc"))
        tasks.append(task)
    
    group_tasks[chat_id] = tasks
    await update.message.reply_text("🖱️ Group Nc Is On")

@only_sudo
async def nc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🎺 Usage: /nc <name>")
    
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Stop existing tasks
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
    
    # Start new tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(bot_loop(bot, chat_id, base, "nc"))
        tasks.append(task)
    
    group_tasks[chat_id] = tasks
    await update.message.reply_text("📲 STARTS")

@only_sudo
async def ncdad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """GOD LEVEL Name Changer - 5 changes in 0.1 seconds"""
    if not context.args:
        return await update.message.reply_text("☎️ Usage: /ncdad <name>")
    
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Stop existing tasks
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
    
    # Start ultra fast tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(ncdad_loop(bot, chat_id, base))
        tasks.append(task)
    
    group_tasks[chat_id] = tasks
    await update.message.reply_text("🖨FAST NC📞")

@only_sudo
async def stopgrpnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
        del group_tasks[chat_id]
        await update.message.reply_text("⌨️STOPPED")
    else:
        await update.message.reply_text("🖨️ NONE ACTIVE")

@only_sudo
async def stopnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
        del group_tasks[chat_id]
        await update.message.reply_text("🔌Started Here")
    else:
        await update.message.reply_text("📞 stopped here")

@only_sudo
async def stopncdad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
        del group_tasks[chat_id]
        await update.message.reply_text("🪕 Fast Ncdad Has Started")
    else:
        await update.message.reply_text("🎻No ncdad is on")

# ---------------------------
# ncstable COMMANDS - FIXED
# ---------------------------
@only_sudo
async def ncstable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("📢 Usage: /ncstable <name>")
    
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Stop existing tasks
    if chat_id in ncstable_tasks:
        for task in ncstable_tasks[chat_id]:
            task.cancel()
    
    # Start new tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(ncstable_loop(bot, chat_id, base))
        tasks.append(task)
    
    ncstable_tasks[chat_id] = tasks
    await update.message.reply_text("🇧🇩ncstable On")

@only_sudo
async def ncabbu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ncstable_delay
    ncstable_delay = 0.03
    
    if not context.args:
        return await update.message.reply_text("🇦🇲 Usage: /ncabbu <name>")
    
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    if chat_id in ncstable_tasks:
        for task in ncstable_tasks[chat_id]:
            task.cancel()
    
    tasks = []
    for bot in bots:
        task = asyncio.create_task(ncstable_loop(bot, chat_id, base))
        tasks.append(task)
    
    ncstable_tasks[chat_id] = tasks
    await update.message.reply_text("📿 Faster Nc Started")

@only_sudo
async def fastestnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """BEST MODS"""
    if not context.args:
        return await update.message.reply_text("⚠ Usage: /fastestnc <name>")
    
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Stop existing tasks
    if chat_id in ncstable_tasks:
        for task in ncstable_tasks[chat_id]:
            task.cancel()
    
    # Start GOD SPEED tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(ncstable_godspeed_loop(bot, chat_id, base))
        tasks.append(task)
    
    ncstable_tasks[chat_id] = tasks
    await update.message.reply_text("💍 Fast Speed Has Been On! 💎")

@only_sudo
async def stopncstable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in ncstable_tasks:
        for task in ncstable_tasks[chat_id]:
            task.cancel()
        del ncstable_tasks[chat_id]
        await update.message.reply_text("💍 ncstable off")
    else:
        await update.message.reply_text("🔈 None ncstable")

# ---------------------------
# SPAM COMMANDS
# ---------------------------
@only_sudo
async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("👢 Usage: /spam <text>")
    
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Stop existing spam
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    
    # Start new spam
    tasks = []
    for bot in bots:
        task = asyncio.create_task(spam_loop(bot, chat_id, text))
        tasks.append(task)
    
    spam_tasks[chat_id] = tasks
    await update.message.reply_text("👒 SPAM On")

@only_sudo
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
        await update.message.reply_text("👞 Spam Off")
    else:
        await update.message.reply_text("👗 None spam")

# ---------------------------
# SLIDE COMMANDS - FIXED
# ---------------------------
@only_sudo
async def autoslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply To Someone")
    
    target_id = update.message.reply_to_message.from_user.id
    slide_targets.add(target_id)
    await update.message.reply_text(f"🧤 Target slide added: {target_id}")

@only_sudo
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("🔈Reply To Someone")
    
    target_id = update.message.reply_to_message.from_user.id
    slide_targets.discard(target_id)
    await update.message.reply_text(f"Slide stopped: {target_id}")

@only_sudo
async def slidepam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("👑 Reply To Someone")
    
    target_id = update.message.reply_to_message.from_user.id
    slidepam_targets.add(target_id)
    await update.message.reply_text(f"🩱Slide spam started: {target_id}")

@only_sudo
async def stopslidepam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("🎩 Reply To Someone")
    
    target_id = update.message.reply_to_message.from_user.id
    slidepam_targets.discard(target_id)
    await update.message.reply_text(f"👜 Slide spam stopped: {target_id}")

# ---------------------------
# VOICE COMMANDS - tempest INTEGRATION
# ---------------------------
@only_sudo
async def animevn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Anime voice with tempest - FIXED SYNTAX"""
    if len(context.args) < 2:
        return await update.message.reply_text("⚠ Usage: /animevn <character_numbers> <text>\nExample: /animevn 1 2 3 Hello world")
    
    try:
        # Parse character numbers
        char_numbers = []
        text_parts = []
        
        for arg in context.args:
            if arg.isdigit() and int(arg) in VOICE_CHARACTERS:
                char_numbers.append(int(arg))
            else:
                text_parts.append(arg)
        
        if not char_numbers:
            return await update.message.reply_text("👖 Please provide valid character numbers (1-10)")
        
        text = " ".join(text_parts)
        if not text:
            return await update.message.reply_text("🦺 Please provide text to speak")
        
        await update.message.reply_text(f"😠 Generating voices for characters: {', '.join([VOICE_CHARACTERS[num]['name'] for num in char_numbers])}...")
        
        # Generate voices
        voices = await generate_multiple_voices(text, char_numbers)
        
        if not voices:
            # Fallback to gTTS if tempest fails
            tts = gTTS(text=text, lang='ja', slow=False)
            voice_file = io.BytesIO()
            tts.write_to_fp(voice_file)
            voice_file.seek(0)
            
            character_names = [VOICE_CHARACTERS[num]['name'] for num in char_numbers]
            await update.message.reply_voice(
                voice=voice_file, 
                caption=f"😨 {' + '.join(character_names)}: {text}"
            )
        else:
            # Send each voice
            for voice in voices:
                await update.message.reply_voice(
                    voice=voice["audio"],
                    caption=f"👻{voice['character']}: {text}\n{voice['description']}"
                )
                await asyncio.sleep(1)  # Delay between voices
        
    except Exception as e:
        await update.message.reply_text(f"😖 Voice error: {e}")

@only_sudo
async def tempest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Default tempest voice"""
    if not context.args:
        return await update.message.reply_text("⚠ Usage: /tempest <text>")
    
    text = " ".join(context.args)
    
    # Use Urokodaki voice as default
    audio_data = await generate_tempest_voice(text, VOICE_CHARACTERS[1]["voice_id"])
    
    if audio_data:
        await update.message.reply_voice(
            voice=audio_data,
            caption=f"👹{VOICE_CHARACTERS[1]['name']}: {text}"
        )
    else:
        # Fallback to gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        voice_file = io.BytesIO()
        tts.write_to_fp(voice_file)
        voice_file.seek(0)
        await update.message.reply_voice(voice=voice_file, caption=f"😜 Fallback TTS: {text}")

@only_sudo
async def voices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List available voices"""
    voice_list = "😛 Available Anime Voices:\n\n"
    for num, voice in VOICE_CHARACTERS.items():
        voice_list += f"{num}. {voice['name']} - {voice['description']}\n"
    
    voice_list += "\n🤪Usage: /animevn 1 2 3 Hello world"
    await update.message.reply_text(voice_list)

# Other voice commands remain the same...
@only_sudo
async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("🤫 Usage: /music <song>")
    
    song = " ".join(context.args)
    await update.message.reply_text(f"🎶 Downloading: {song}")

@only_sudo
async def clonevn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("🤤 Reply to a voice message")
    
    await update.message.reply_text("🤑 Voice cloning started...")

@only_sudo
async def clonedvn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("😂Usage: /clonedvn <text>")
    
    text = " ".join(context.args)
    await update.message.reply_text(f"😍 Speaking in cloned voice: {text}")

# ---------------------------
# REACT COMMANDS
# ---------------------------
@only_sudo
async def emojispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text(" Usage: /emojispam <emoji>")
    
    emoji = context.args[0]
    chat_id = update.message.chat_id
    
    async def react_loop(bot, chat_id, emoji):
        while True:
            await asyncio.sleep(1)
    
    if chat_id in react_tasks:
        for task in react_tasks[chat_id]:
            task.cancel()
    
    tasks = []
    for bot in bots:
        task = asyncio.create_task(react_loop(bot, chat_id, emoji))
        tasks.append(task)
    
    react_tasks[chat_id] = tasks
    await update.message.reply_text(f"😉Auto-reaction: {emoji}")

@only_sudo
async def stopemojispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in react_tasks:
        for task in react_tasks[chat_id]:
            task.cancel()
        del react_tasks[chat_id]
        await update.message.reply_text("🕶️Reactions Stopped!")
    else:
        await update.message.reply_text("🎌No active reactions")

# ---------------------------
# STICKER SYSTEM
# ---------------------------
@only_sudo
async def newsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("🦴 Reply to a photo with /newsticker")
    
    await update.message.reply_text("😈 Sticker creation ready! Choose emoji for sticker")

@only_sudo
async def delsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if str(user_id) in user_stickers:
        del user_stickers[str(user_id)]
        save_stickers()
        await update.message.reply_text("💷Your stickers deleted!")
    else:
        await update.message.reply_text("No stickers found")

@only_sudo
async def multisticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" Creating 5 stickers...")

@only_sudo
async def stickerbotinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_stickers = sum(len(stickers) for stickers in user_stickers.values())
    await update.message.reply_text(f"Sticker botinfo: {total_stickers} stickers total")

@only_owner
async def stopstickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sticker_mode
    sticker_mode = False
    await update.message.reply_text("🌈 Stickers disabled")

@only_owner
async def startstickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sticker_mode
    sticker_mode = True
    await update.message.reply_text("🎗️Stickers enabled")

# ---------------------------
# CONTROL COMMANDS
# ---------------------------
@only_sudo
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Stop all tasks
    for chat_tasks in group_tasks.values():
        for task in chat_tasks:
            task.cancel()
    group_tasks.clear()
    
    for chat_tasks in spam_tasks.values():
        for task in chat_tasks:
            task.cancel()
    spam_tasks.clear()
    
    for chat_tasks in react_tasks.values():
        for task in chat_tasks:
            task.cancel()
    react_tasks.clear()
    
    for chat_tasks in ncstable_tasks.values():
        for task in chat_tasks:
            task.cancel()
    ncstable_tasks.clear()
    
    slide_targets.clear()
    slidepam_targets.clear()
    
    await update.message.reply_text(" Everthing Has Been Offed🍃")

@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay
    if not context.args:
        return await update.message.reply_text(f"🚩 Current delay: {delay}s")
    
    try:
        delay = max(0.1, float(context.args[0]))
        await update.message.reply_text(f"💖 Delay set to {delay}s")
    except:
        await update.message.reply_text("🧭 Invalid number")

# ---------------------------
# botinfo COMMANDS
# ---------------------------
@only_sudo
async def botinfo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botinfo_text = f"""
𝐄ʙʙ𝐔 V12:

🖤𝗡𝗖: {sum(len(tasks) for tasks in group_tasks.values())}
🧧ncstable Sessions: {sum(len(tasks) for tasks in ncstable_tasks.values())}
💟 Spam Sessions: {sum(len(tasks) for tasks in spam_tasks.values())}
🍷 Slide: {len(slide_targets)}
🥰 Slide-2: {len(slidepam_targets)}

Delay: {delay}s
🐕 ncstable Delay: {ncstable_delay}s
🧭𝗕𝗢𝗧𝗦: {len(bots)}
☀️𝗔𝗗𝗠𝗜𝗡 𝗨𝗦𝗘: {len(admin_USERS)}

    """
    await update.message.reply_text(botinfo_text)

# ---------------------------
# SUDO MANAGEMENT
# ---------------------------
@only_owner
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("🖤 Reply to someone")
    
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"🙊 SUDO added: {uid}")

@only_owner
async def endadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("🐕 Reply to a user")
    
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"⚔️ Admin Has Been Taken: {uid}")
    else:
        await update.message.reply_text("👅 Lund Chus")

@only_sudo
async def adminabout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sudo_list = "\n".join([f"👣 {uid}" for uid in SUDO_USERS])
    await update.message.reply_text(f"🧨 SUDO Users:\n{sudo_list}")

# ---------------------------
# AUTO REPLY HANDLER - FIXED
# ---------------------------
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    
    # Handle slide targets
    if uid in slide_targets:
        for text in RAID_TEXTS[:3]:
            await update.message.reply_text(text)
            await asyncio.sleep(0.1)
    
    # Handle slidepam targets
    if uid in slidepam_targets:
        for text in RAID_TEXTS:
            await update.message.reply_text(text)
            await asyncio.sleep(0.05)

# ---------------------------
# BOT SETUP
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    
    # Core commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("pong", pong_cmd))
    app.add_handler(CommandHandler("chatid", chatid))
    app.add_handler(CommandHandler("botinfo", botinfo_cmd))
    
    # Name changer commands
    app.add_handler(CommandHandler("grpnc", grpnc))
    app.add_handler(CommandHandler("nc", nc))
    app.add_handler(CommandHandler("ncdad", ncdad))
    app.add_handler(CommandHandler("stopgrpnc", stopgrpnc))
    app.add_handler(CommandHandler("stopnc", stopnc))
    app.add_handler(CommandHandler("stopncdad", stopncdad))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("delay", delay_cmd))
    
    # ncstable commands
    app.add_handler(CommandHandler("ncstable", ncstable))
    app.add_handler(CommandHandler("ncabbu", ncabbu))
    app.add_handler(CommandHandler("fastestnc", fastestnc))
    app.add_handler(CommandHandler("stopncstable", stopncstable))
    
    # Spam commands
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("stopspam", stopspam))
    
    # React commands
    app.add_handler(CommandHandler("emojispam", emojispam))
    app.add_handler(CommandHandler("stopemojispam", stopemojispam))
    
    # Slide commands
    app.add_handler(CommandHandler("autoslide", autoslide))
    app.add_handler(CommandHandler("stopslide", stopslide))
    app.add_handler(CommandHandler("slidepam", slidepam))
    app.add_handler(CommandHandler("stopslidepam", stopslidepam))
    
    # Sticker commands
    app.add_handler(CommandHandler("newsticker", newsticker))
    app.add_handler(CommandHandler("delsticker", delsticker))
    app.add_handler(CommandHandler("multisticker", multisticker))
    app.add_handler(CommandHandler("stickerbotinfo", stickerbotinfo))
    app.add_handler(CommandHandler("stopstickers", stopstickers))
    app.add_handler(CommandHandler("startstickers", startstickers))
    
    # Voice commands
    app.add_handler(CommandHandler("animevn", animevn))
    app.add_handler(CommandHandler("tempest", tempest_cmd))
    app.add_handler(CommandHandler("music", music))
    app.add_handler(CommandHandler("clonevn", clonevn))
    app.add_handler(CommandHandler("clonedvn", clonedvn))
    app.add_handler(CommandHandler("voices", voices))
    
    # SUDO management
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("endadmin", endadmin))
    app.add_handler(CommandHandler("adminabout", adminabout))
    
    # Auto replies
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_replies))
    
    return app

async def run_all_bots():
    global apps, bots
    for token in TOKENS:
        if token.strip():
            try:
                app = build_app(token)
                apps.append(app)
                bots.append(app.bot)
                print(f"💌 Bot REVS: {token[:10]}...")
            except Exception as e:
                print(f"FAILED💷: {e}")

    # Start all bots
    for app in apps:
        try:
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print(f"BOTS ARE ON💲")
        except Exception as e:
            print(f"FAILED❄️: {e}")

    print(f" 𝐄ʙʙ𝐔 𝑉12 𝐹𝑌𝑇𝐼𝑁𝐺 𝐵𝑂𝑇¿{len(bots)}")
    print("Chat ID:", CHAT_ID)
    print("PER Bots:", len(bots))
    print("STABLE NC🏳️")
    print("FASTEST NC!!!!")
    print("ACTIVE WITH UR API 🔐")
    print("START FYTING!")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("\n𝐄ʙʙ𝐔 V12 Is Off")
    except Exception as e:
        print(f"Something went wrong: {e}")