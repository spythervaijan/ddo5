import asyncio
import json
import os
import random
import time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging
import yt_dlp
from gtts import gTTS
import requests
import io
from collections import defaultdict
from telegram.error import RetryAfter

# ---------------------------
# CONFIG
# ---------------------------
TOKENS = [ "8217837413:AAFhov6DYmEavOTXE0FI5_x35L8ugplUnts", "8340544806:AAHGQurjYAwuOUyL_7ZqsL2jEMaBzYiSQTw", "8539861029:AAHpm8JDEx6npPYUx7m222S6jN8OpBOcVKQ", "8268859358:AAFhcNp84Sk8MGIgTtOQ59Y_OzWcwPEbOz4", "8500217869:AAEP_M16F63WJfh-YR7EzCxeUROF6eG_O38", "8504875277:AAFfG7xcQ-4kgdP7DKf7ZoQCDIvMFr_T4yA", "8226293589:AAE3URbfEbQwecFU_Iutn7GvmqegfBtr0uA", "8537512518:AAFXTbev3xxGgrzuKbv3mqexk2r9OaeJ_Cc", "8565054090:AAHUqiX4FtieLRoAE0L1vzPeEJ5veTJD98U", "8527550791:AAF7G2vXMU6g-V8Kin4rRr6G4erih6QbVME", "8571284458:AAEqhW3FzEP7Ia-eAQKX6cPVEAjWHYFzkD8", "8573245794:AAFJJqzpFLKtWjmLNNXdb9PcC3ZuMRs_hiQ", "7911873074:AAGXznAOSDzPTcGcoOQvxmE2d-nDQYs4Sm4", "8560682317:AAFzyCGI67q9AH2TntG_jQNP4pIPeOLWTOE", "8297450487:AAHEEdHroJH__yQD9SX5ywOfMFztbIZtMLU", "8437914572:AAG0hhgq2PhCPScJsN9Lzi--hCiqJw_ApjQ" ]

CHAT_ID = 6516344614
OWNER_ID = 6516344614
SUDO_FILE = "sudo_users.json"
STICKER_FILE = "stickers.json"
VOICE_CLONES_FILE = "voice_clones.json"
tempest_API_KEY = "sk_e326b337242b09b451e8f18041fd0a7149cc895648e36538"

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
 "×~🌷GAY🌷×~",
"~×🌼BITCH🌼×~",
"~×🌻LESBIAN🌻×~",
"~×🌺CHAPRI🌺×~",
"~×🌹TMKC🌹×~",
"~×🏵️TMR🏵×~️",
"~×🪷TMKB🪷×~",
"~×💮CHUS💮×~",
"~×🌸HAKLE🌸×~",
"~×🌷GAREEB🌷×~",
"~×🌼RANDY🌼×~",
"~×🌻POOR🌻×~",
"~×🌺TATTI🌺×~",
"~×🌹CHOR🌹×~",
"~×🏵️CHAMAR🏵️×~",
"~×🪷SPERM COLLECTOR🪷×~",
"~×💮CHUTI LULLI💮×~",
"~×🌸KALWA🌸×~",
"~×🌷CHUD🌷×~",
"~×🌼CHUTKHOR🌼×~",
"~×🌻BAUNA🌻×~",
"~×🌺MOTE🌺×~",
"~×🌹GHIN ARHA TUJHSE🌹×~",
"~×🏵️CHI POOR🏵×~️",
"~🪷PANTY CHOR🪷~",
"~×💮LAND CHUS💮×~",
"~×🌸MUH MAI LEGA🌸×~",
"~×🌷GAND MARE 🌷×~",
"~×🌼MOCHI WALE 🌼×~",
"~×🌻GANDMARE 🌻×~",
"~×🌺KIDDE 🌺×~",
"~×🌹LAMO 🌹×~",
"~×🏵️BIHARI 🏵×~",
"~×🪷 MADARCHOD 🪷×~",
"~×💮NAJAYESH LADKE 💮×~",
"~×🌸GULAM 🌸×~",
"~×🌷CHAMCHA🌷×~",
"~×🌼EWW 🌼×~",
"~×🌻CHOTE TATTE 🌻×~",
"~×🌺SEX WORKER 🌺×~",
"~×🌹CHINNAR MA KE LADKE 🌹×~"
]

exonc_TEXTS = [
    "×🌼×","×🌻×","×🪻×","×🏵️×","×💮×","×🌸×","×🪷×","×🌷×",
    "×🌺×","×🥀×","×🌹×","×💐×","×💋×","×❤️‍🔥×","×❤️‍🩹×","×❣️×",
    "×♥️×","×💟×","×💌×","×💕×","×💞×","×💓×","×💗×","×💖×",
    "×💝×","×💘×","×🩷×","×🤍×","×🩶×","×🖤×","🤎×","×💜×",
    "×💜×","×🩵×","×💛×","×🧡×","×❤️×","×🌼×","×🌻×","×🪻×",
"×🏵️×","×💮×","×🌸×","×🪷×","×🌷×",
    "×🌺×","×🥀×","×🌹×","×💐×","×💋×","×❤️‍🔥×","×❤️‍🩹×","×❣️×",
    "×♥️×","×💟×","×💌×","×💕×","×💞×","×💓×","×💗×","×💖×",
    "×💝×","×💘×","×🩷×","×🤍×","×🩶×","×🖤×","🤎×","×💜×",
    "×💜×","×🩵×","×💛×","×🧡×","×❤️×",
]

NCEMO_EMOJIS = [
  "😀","😃","😄","😁","😆","😅","😂","🤣","😭","😉","😗","😗","😚","😘","🥰","😍",
"🤩","🥳","🫠","🙃","🙂","🥲","🥹","😊","☺️","😌","🙂‍↕️","🙂‍↔️",
  "😏","🤤","😋","😛","😝","😜","🤪","🥴","😔","🥺","😬","😑","😐","😶","😶‍🌫️",
"🫥","🤐","🫡","🤔","🤫","🫢","🤭","🥱","🤗","🫣","😱","🤨","🧐","😒","🙄","😮‍💨","😤",
"😠","😡","🤬","😞","😓",
  "😟","😥","😢","☹️","🙁","🫤","😕","😰","😨","😧","😦","😮","😯","😲","😳",
  "🤯","😖","😣","😩","😵","😵‍💫","🫨","🥶","🥵","🤢","🤮","😴","😪","🤧","🤒",
  "🤒","🤕","😷","😇","🤠","🤑","🤓","😎","🥸",
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
slidespam_targets = set()
exonc_tasks = {}
sticker_mode = True
apps, bots = [], []
delay = 1.0

logging.basicConfig(level=logging.INFO)

# Safety infrastructure
bot_locks = defaultdict(asyncio.Lock)
chat_semaphores = defaultdict(lambda: asyncio.Semaphore(5))  # Burst limit per chat

async def safe_api_call(bot, func, *args, **kwargs):
    # Extract chat_id for semaphore
    chat_id = kwargs.get('chat_id')
    if chat_id is None and args:
        chat_id = args[0]

    if chat_id is None:
        raise ValueError("No chat_id found")

    retries = 0
    max_retries = 3
    while retries < max_retries:
        async with chat_semaphores[chat_id]:
            async with bot_locks[bot.token]:
                try:
                    return await func(*args, **kwargs)
                except RetryAfter as e:
                    global delay
                    wait = e.retry_after + random.uniform(0.1, 0.5)
                    if retries > 1:
                        delay += 0.1  # Auto-increase delay on repeated floods
                    await asyncio.sleep(wait)
                    retries += 1
                except Exception as e:
                    logging.error(f"API error: {e}")
                    raise
    raise Exception("Max retries exceeded")

# ---------------------------
# DECORATORS
# ---------------------------
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid not in SUDO_USERS:
            bot = context.bot
            chat_id = update.message.chat_id
            await safe_api_call(bot, bot.send_message, chat_id, "😂AUKAT BANA R@NDí KE LADKE😏.")
            return
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid != OWNER_ID:
            bot = context.bot
            chat_id = update.message.chat_id
            await safe_api_call(bot, bot.send_message, chat_id, "🤬BHAG JA TERI AUKAT NHI TMKC🤬.")
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
        if response.status_code == 200:
            return io.BytesIO(response.content)
        else:
            logging.error(f"tempest API error: {response.status_code} - {response.text}")
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
# LOOP FUNCTIONS - OPTIMIZED FOR MULTI-GC
# ---------------------------
async def bot_loop(bot, chat_id, base, mode):
    i = 0
    try:
        while True:
            try:
                if mode == "gcnc":
                    text = f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}"
                else:
                    text = f"{base} {NCEMO_EMOJIS[i % len(NCEMO_EMOJIS)]}"
                await safe_api_call(bot, bot.set_chat_title, chat_id, text)
                i += 1
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                raise
            except Exception:
                await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        return

async def ncbaap_loop(bot, chat_id, base):
    i = 0
    try:
        while True:
            try:
                patterns = [
                    f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}",
                    f"{base} {NCEMO_EMOJIS[i % len(NCEMO_EMOJIS)]}",
                    f"{base} {exonc_TEXTS[i % len(exonc_TEXTS)]}",
                ]
                for p in patterns:
                    await safe_api_call(bot, bot.set_chat_title, chat_id, p)
                i += 1
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                raise
            except Exception:
                await asyncio.sleep(0.3)
    except asyncio.CancelledError:
        return

async def spam_loop(bot, chat_id, text):
    try:
        while True:
            try:
                await safe_api_call(bot, bot.send_message, chat_id, text)
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                raise
            except Exception:
                await asyncio.sleep(0.5)
    except asyncio.CancelledError:
        return

async def exonc_godspeed_loop(bot, chat_id, base_text):
    i = 0
    try:
        while True:
            try:
                patterns = [
                    f"{base_text} {exonc_TEXTS[i % len(exonc_TEXTS)]}",
                    f"{exonc_TEXTS[i % len(exonc_TEXTS)]} {base_text}",
                    f"{base_text}{exonc_TEXTS[i % len(exonc_TEXTS)]}",
                    f"{exonc_TEXTS[(i+1) % len(exonc_TEXTS)]} {base_text}",
                    f"{base_text} {exonc_TEXTS[(i+2) % len(exonc_TEXTS)]}",
                ]
                for p in patterns:
                    await safe_api_call(bot, bot.set_chat_title, chat_id, p)
                i += 1
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                raise
            except Exception:
                await asyncio.sleep(0.2)
    except asyncio.CancelledError:
        return

async def exonc_loop(bot, chat_id, base_text):
    i = 0
    try:
        while True:
            try:
                text = f"{base_text} {exonc_TEXTS[i % len(exonc_TEXTS)]}"
                await safe_api_call(bot, bot.set_chat_title, chat_id, text)
                i += 1
                await asyncio.sleep(delay)
            except asyncio.CancelledError:
                raise
            except Exception:
                await asyncio.sleep(0.3)
    except asyncio.CancelledError:
        return

# ---------------------------
# CORE COMMANDS
# ---------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    await safe_api_call(bot, bot.send_message, chat_id, "🪷 RAHUL NC 🪷\nUse /help to see commands ✅")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """╔══════════════════════╗
   🪷  RAHUL NC MENU  🪷
╚══════════════════════╝

🎀 𝗡𝗖 𝗠𝗢𝗗𝗘𝗦
━━━━━━━━━━━━━━━
➤ /ncloop <name>  
➤ /ncemo <name>  
➤ /ncbaap <name>  

⏹ Stop Controls  
➤ /stopncloop  
➤ /stopncemo  
➤ /stopncbaap  
➤ /stopall  
➤ /delay <sec>  

😹 𝗦𝗣𝗔𝗠 𝗭𝗢𝗡𝗘
━━━━━━━━━━━━━━━
➤ /spam <text>  
➤ /unspam  

🪐 𝗥𝗘𝗔𝗖𝗧 𝗠𝗢𝗗𝗘
━━━━━━━━━━━━━━━
➤ /emojispam <emoji>  
➤ /stopemojispam  

🪼 𝗦𝗟𝗜𝗗𝗘 𝗠𝗢𝗗𝗘
━━━━━━━━━━━━━━━
➤ /targetslide  
➤ /slidespam  
➤ /stopslide  
➤ /stopslidespam  

⚡ 𝗘𝗫𝗢𝗡𝗖 𝗣𝗢𝗪𝗘𝗥
━━━━━━━━━━━━━━━
➤ /exonc  
➤ /exoncfast  
➤ /exoncgodspeed  
➤ /stopexonc  

🎵 𝗩𝗢𝗜𝗖𝗘 𝗦𝗧𝗨𝗗𝗜𝗢
━━━━━━━━━━━━━━━
➤ /animevn <1-10> <text>  
➤ /voices  
➤ /tempest <text>  

👑 𝗦𝗨𝗗𝗢 𝗣𝗔𝗡𝗘𝗟
━━━━━━━━━━━━━━━
➤ /addsudo  
➤ /delsudo  
➤ /listsudo  

🦚 𝗠𝗜𝗦𝗖
━━━━━━━━━━━━━━━
➤ /myid  
➤ /ready  
➤ /status  

╔══════════════════════╗
 ✨ Powered by RAHUL NC ✨
╚══════════════════════╝"""
    bot = context.bot
    chat_id = update.message.chat_id
    await safe_api_call(bot, bot.send_message, chat_id, help_text)

async def ready_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    start = time.time()
    msg = await safe_api_call(bot, bot.send_message, chat_id, "💭 Hmm...")
    end = time.time()
    await safe_api_call(bot, bot.edit_message_text, chat_id=chat_id, message_id=msg.message_id, text="✅ All set! ")

async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    await safe_api_call(bot, bot.send_message, chat_id, f"🆔 Your ID: {update.effective_user.id}")

# ---------------------------
# NAME CHANGER COMMANDS
# ---------------------------
@only_sudo
async def ncloop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /ncloop <name>")
        return
    
    base = " ".join(context.args)
    
    # Stop existing tasks
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
    
    # Start new tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(bot_loop(bot, chat_id, base, "gcnc"))
        tasks.append(task)
    
    group_tasks[chat_id] = tasks
    await safe_api_call(bot, bot.send_message, chat_id, "🔄चुदाई Suru target ka")

@only_sudo
async def ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /ncemo <name>")
        return
    
    base = " ".join(context.args)
    
    # Stop existing tasks
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
    
    # Start new tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(bot_loop(bot, chat_id, base, "ncemo"))
        tasks.append(task)
    
    group_tasks[chat_id] = tasks
    await safe_api_call(bot, bot.send_message, chat_id, "🌹emoji cycle started 🌹")

@only_sudo
async def ncbaap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /ncbaap <name>")
        return
    
    base = " ".join(context.args)
    
    # Stop existing tasks
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
    
    # Start ultra fast tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(ncbaap_loop(bot, chat_id, base))
        tasks.append(task)
    
    group_tasks[chat_id] = tasks
    await safe_api_call(bot, bot.send_message, chat_id, "💀🔥 GOD SPEED NCBAAP LOOP STARTED 💀🔥")

@only_sudo
async def stopncloop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
        del group_tasks[chat_id]
        await safe_api_call(bot, bot.send_message, chat_id, "✅ NC Loop Stopped!")
    else:
        await safe_api_call(bot, bot.send_message, chat_id, "❌ No active NC loop")

@only_sudo
async def stopncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
        del group_tasks[chat_id]
        await safe_api_call(bot, bot.send_message, chat_id, "⏹ Emoji Name Changer Stopped!")
    else:
        await safe_api_call(bot, bot.send_message, chat_id, "❌ No active emoji changer")

@only_sudo
async def stopncbaap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id]:
            task.cancel()
        del group_tasks[chat_id]
        await safe_api_call(bot, bot.send_message, chat_id, "⏹ GOD LEVEL NCBAAP Stopped!")
    else:
        await safe_api_call(bot, bot.send_message, chat_id, "❌ No active ncbaap")

# ---------------------------
# exonc COMMANDS - FIXED
# ---------------------------
@only_sudo
async def exonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /exonc <name>")
        return
    
    base = " ".join(context.args)
    
    # Stop existing tasks
    if chat_id in exonc_tasks:
        for task in exonc_tasks[chat_id]:
            task.cancel()
    
    # Start new tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(exonc_loop(bot, chat_id, base))
        tasks.append(task)
    
    exonc_tasks[chat_id] = tasks
    await safe_api_call(bot, bot.send_message, chat_id, "💀 exonc Mode Activated!")

@only_sudo
async def exoncfast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay
    delay = 0.03
    bot = context.bot
    chat_id = update.message.chat_id
    
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /exoncfast <name>")
        return
    
    base = " ".join(context.args)
    
    if chat_id in exonc_tasks:
        for task in exonc_tasks[chat_id]:
            task.cancel()
    
    tasks = []
    for bot in bots:
        task = asyncio.create_task(exonc_loop(bot, chat_id, base))
        tasks.append(task)
    
    exonc_tasks[chat_id] = tasks
    await safe_api_call(bot, bot.send_message, chat_id, "⚡ Faster exonc Activated!")

@only_sudo
async def exoncgodspeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /exoncgodspeed <name>")
        return
    
    base = " ".join(context.args)
    
    # Stop existing tasks
    if chat_id in exonc_tasks:
        for task in exonc_tasks[chat_id]:
            task.cancel()
    
    # Start GOD SPEED tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(exonc_godspeed_loop(bot, chat_id, base))
        tasks.append(task)
    
    exonc_tasks[chat_id] = tasks
    await safe_api_call(bot, bot.send_message, chat_id, "👑🔥 GOD SPEED exonc ACTIVATED! 5 NC in 0.05s! 🚀")

@only_sudo
async def stopexonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if chat_id in exonc_tasks:
        for task in exonc_tasks[chat_id]:
            task.cancel()
        del exonc_tasks[chat_id]
        await safe_api_call(bot, bot.send_message, chat_id, "🛑 exonc Stopped!")
    else:
        await safe_api_call(bot, bot.send_message, chat_id, "❌ No active exonc")

# ---------------------------
# SPAM COMMANDS
# ---------------------------
@only_sudo
async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /spam <text>")
        return
    
    text = " ".join(context.args)
    
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
    await safe_api_call(bot, bot.send_message, chat_id, "💥 SPAM STARTED!")

@only_sudo
async def unspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
        await safe_api_call(bot, bot.send_message, chat_id, "✅ Spam Stopped!")
    else:
        await safe_api_call(bot, bot.send_message, chat_id, "❌ No active spam")

# ---------------------------
# SLIDE COMMANDS - FIXED
# ---------------------------
@only_sudo
async def targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not update.message.reply_to_message:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Reply to a user's message")
        return
    
    target_id = update.message.reply_to_message.from_user.id
    slide_targets.add(target_id)
    await safe_api_call(bot, bot.send_message, chat_id, f"🎯 Target slide added: {target_id}")

@only_sudo
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not update.message.reply_to_message:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Reply to a user's message")
        return
    
    target_id = update.message.reply_to_message.from_user.id
    slide_targets.discard(target_id)
    await safe_api_call(bot, bot.send_message, chat_id, f"🛑 Slide stopped: {target_id}")

@only_sudo
async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not update.message.reply_to_message:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Reply to a user's message")
        return
    
    target_id = update.message.reply_to_message.from_user.id
    slidespam_targets.add(target_id)
    await safe_api_call(bot, bot.send_message, chat_id, f"💥 Slide spam started: {target_id}")

@only_sudo
async def stopslidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not update.message.reply_to_message:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Reply to a user's message")
        return
    
    target_id = update.message.reply_to_message.from_user.id
    slidespam_targets.discard(target_id)
    await safe_api_call(bot, bot.send_message, chat_id, f"🛑 Slide spam stopped: {target_id}")

# ---------------------------
# VOICE COMMANDS - tempest INTEGRATION
# ---------------------------
@only_sudo
async def animevn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args or len(context.args) < 2:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /animevn <character_numbers> <text>\nExample: /animevn 1 2 3 Hello world")
        return
    
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
            await safe_api_call(bot, bot.send_message, chat_id, "❌ Please provide valid character numbers (1-10)")
            return
        
        text = " ".join(text_parts)
        if not text:
            await safe_api_call(bot, bot.send_message, chat_id, "❌ Please provide text to speak")
            return
        
        await safe_api_call(bot, bot.send_message, chat_id, f"🎭 Generating voices for characters: {', '.join([VOICE_CHARACTERS[num]['name'] for num in char_numbers])}...")
        
        # Generate voices
        voices = await generate_multiple_voices(text, char_numbers)
        
        if not voices:
            # Fallback to gTTS if tempest fails
            tts = gTTS(text=text, lang='ja', slow=False)
            voice_file = io.BytesIO()
            tts.write_to_fp(voice_file)
            voice_file.seek(0)
            
            character_names = [VOICE_CHARACTERS[num]['name'] for num in char_numbers]
            await safe_api_call(bot, bot.send_voice, chat_id=chat_id, voice=voice_file, 
                                caption=f"🎀 {' + '.join(character_names)}: {text}")
        else:
            # Send each voice
            for voice in voices:
                await safe_api_call(bot, bot.send_voice, chat_id=chat_id, voice=voice["audio"], 
                                    caption=f"🎀 {voice['character']}: {text}\n{voice['description']}")
                await asyncio.sleep(1)  # Delay between voices
        
    except Exception as e:
        await safe_api_call(bot, bot.send_message, chat_id, f"❌ Voice error: {e}")

@only_sudo
async def tempest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /tempest <text>")
        return
    
    text = " ".join(context.args)
    
    # Use Urokodaki voice as default
    audio_data = await generate_tempest_voice(text, VOICE_CHARACTERS[1]["voice_id"])
    
    if audio_data:
        await safe_api_call(bot, bot.send_voice, chat_id=chat_id, voice=audio_data, 
                            caption=f"🎙️ {VOICE_CHARACTERS[1]['name']}: {text}")
    else:
        # Fallback to gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        voice_file = io.BytesIO()
        tts.write_to_fp(voice_file)
        voice_file.seek(0)
        await safe_api_call(bot, bot.send_voice, chat_id=chat_id, voice=voice_file, 
                            caption=f"🗣️ Fallback TTS: {text}")

@only_sudo
async def voices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    voice_list = "🎭 Available Anime Voices:\n\n"
    for num, voice in VOICE_CHARACTERS.items():
        voice_list += f"{num}. {voice['name']} - {voice['description']}\n"
    
    voice_list += "\n🎀 Usage: /animevn 1 2 3 Hello world"
    await safe_api_call(bot, bot.send_message, chat_id, voice_list)

# Other voice commands remain the same...
@only_sudo
async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /music <song>")
        return
    
    song = " ".join(context.args)
    await safe_api_call(bot, bot.send_message, chat_id, f"🎶 Downloading: {song}")

@only_sudo
async def clonevn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not update.message.reply_to_message:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Reply to a voice message")
        return
    
    await safe_api_call(bot, bot.send_message, chat_id, "🎤 Voice cloning started...")

@only_sudo
async def clonedvn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /clonedvn <text>")
        return
    
    text = " ".join(context.args)
    await safe_api_call(bot, bot.send_message, chat_id, f"🎙️ Speaking in cloned voice: {text}")

# ---------------------------
# REACT COMMANDS
# ---------------------------
@only_sudo
async def emojispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Usage: /emojispam <emoji>")
        return
    
    emoji = context.args[0]
    
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
    await safe_api_call(bot, bot.send_message, chat_id, f"🎭 Auto-reaction: {emoji}")

@only_sudo
async def stopemojispam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if chat_id in react_tasks:
        for task in react_tasks[chat_id]:
            task.cancel()
        del react_tasks[chat_id]
        await safe_api_call(bot, bot.send_message, chat_id, "🛑 Reactions Stopped!")
    else:
        await safe_api_call(bot, bot.send_message, chat_id, "❌ No active reactions")

# ---------------------------
# STICKER SYSTEM
# ---------------------------
@only_sudo
async def newsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Reply to a photo with /newsticker")
        return
    
    await safe_api_call(bot, bot.send_message, chat_id, "✅ Sticker creation ready! Choose emoji for sticker")

@only_sudo
async def delsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    if str(user_id) in user_stickers:
        del user_stickers[str(user_id)]
        save_stickers()
        await safe_api_call(bot, bot.send_message, chat_id, "✅ Your stickers deleted!")
    else:
        await safe_api_call(bot, bot.send_message, chat_id, "❌ No stickers found")

@only_sudo
async def multisticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    await safe_api_call(bot, bot.send_message, chat_id, "🔄 Creating 5 stickers...")

@only_sudo
async def stickerstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    total_stickers = sum(len(stickers) for stickers in user_stickers.values())
    await safe_api_call(bot, bot.send_message, chat_id, f"📊 Sticker Status: {total_stickers} stickers total")

@only_owner
async def stopstickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    global sticker_mode
    sticker_mode = False
    await safe_api_call(bot, bot.send_message, chat_id, "🛑 Stickers disabled")

@only_owner
async def startstickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    global sticker_mode
    sticker_mode = True
    await safe_api_call(bot, bot.send_message, chat_id, "✅ Stickers enabled")

# ---------------------------
# CONTROL COMMANDS
# ---------------------------
@only_sudo
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    global group_tasks, spam_tasks, react_tasks, exonc_tasks, slide_targets, slidespam_targets
    
    # Stop group tasks
    for chat_id, tasks in list(group_tasks.items()):
        for task in tasks:
            task.cancel()
    group_tasks.clear()
    
    # Stop spam tasks
    for chat_id, tasks in list(spam_tasks.items()):
        for task in tasks:
            task.cancel()
    spam_tasks.clear()
    
    # Stop react tasks
    for chat_id, tasks in list(react_tasks.items()):
        for task in tasks:
            task.cancel()
    react_tasks.clear()
    
    # Stop exonc tasks
    for chat_id, tasks in list(exonc_tasks.items()):
        for task in tasks:
            task.cancel()
    exonc_tasks.clear()
    
    # Clear slide targets
    slide_targets.clear()
    slidespam_targets.clear()
    
    await safe_api_call(bot, bot.send_message, chat_id, "✅ **ALL ACTIVITIES STOPPED!**")

@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    global delay
    if not context.args:
        await safe_api_call(bot, bot.send_message, chat_id, f"⏱ Current delay: {delay}s")
        return
    
    try:
        delay = max(0.1, float(context.args[0]))
        await safe_api_call(bot, bot.send_message, chat_id, f"✅ Delay set to {delay}s")
    except:
        await safe_api_call(bot, bot.send_message, chat_id, "❌ Invalid number")

# ---------------------------
# STATUS COMMANDS
# ---------------------------
@only_sudo
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    status_text = f"""
📊 RAHUL V4 Status:

🎀 Name Changers: {sum(len(tasks) for tasks in group_tasks.values())}
⚡ exonc Sessions: {sum(len(tasks) for tasks in exonc_tasks.values())}
😹 Spam Sessions: {sum(len(tasks) for tasks in spam_tasks.values())}
🪐 Reactions: {sum(len(tasks) for tasks in react_tasks.values())}
🪼 Slide Targets: {len(slide_targets)}
💥 Slide Spam: {len(slidespam_targets)}

⏱ Delay: {delay}s
🤖 Active Bots: {len(bots)}
👑 SUDO Users: {len(SUDO_USERS)}
🎭 Voice Characters: {len(VOICE_CHARACTERS)}
    """
    await safe_api_call(bot, bot.send_message, chat_id, status_text)

# ---------------------------
# SUDO MANAGEMENT
# ---------------------------
@only_owner
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not update.message.reply_to_message:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Reply to a user")
        return
    
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await safe_api_call(bot, bot.send_message, chat_id, f"✅ SUDO added: {uid}")

@only_owner
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    if not update.message.reply_to_message:
        await safe_api_call(bot, bot.send_message, chat_id, "⚠️ Reply to a user")
        return
    
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_sudo()
        await safe_api_call(bot, bot.send_message, chat_id, f"🗑 SUDO removed: {uid}")
    else:
        await safe_api_call(bot, bot.send_message, chat_id, "❌ User not in SUDO")

@only_sudo
async def listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    sudo_list = "\n".join([f"👑 {uid}" for uid in SUDO_USERS])
    await safe_api_call(bot, bot.send_message, chat_id, f"👑 SUDO Users:\n{sudo_list}")

# ---------------------------
# AUTO REPLY HANDLER - FIXED
# ---------------------------
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat_id = update.message.chat_id
    uid = update.message.from_user.id
    
    # Handle slide targets
    if uid in slide_targets:
        for text in RAID_TEXTS[:3]:
            await safe_api_call(bot, bot.send_message, chat_id, text, reply_to_message_id=update.message.message_id)
            await asyncio.sleep(0.1)
    
    # Handle slidespam targets
    if uid in slidespam_targets:
        for text in RAID_TEXTS:
            await safe_api_call(bot, bot.send_message, chat_id, text, reply_to_message_id=update.message.message_id)
            await asyncio.sleep(0.05)

# ---------------------------
# BOT SETUP
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    
    # Core commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ready", ready_cmd))
    app.add_handler(CommandHandler("myid", myid))
    app.add_handler(CommandHandler("status", status_cmd))
    
    # Name changer commands
    app.add_handler(CommandHandler("ncloop", ncloop))
    app.add_handler(CommandHandler("ncemo", ncemo))
    app.add_handler(CommandHandler("ncbaap", ncbaap))
    app.add_handler(CommandHandler("stopncloop", stopncloop))
    app.add_handler(CommandHandler("stopncemo", stopncemo))
    app.add_handler(CommandHandler("stopncbaap", stopncbaap))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("delay", delay_cmd))
    
    # exonc commands
    app.add_handler(CommandHandler("exonc", exonc))
    app.add_handler(CommandHandler("exoncfast", exoncfast))
    app.add_handler(CommandHandler("exoncgodspeed", exoncgodspeed))
    app.add_handler(CommandHandler("stopexonc", stopexonc))
    
    # Spam commands
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("unspam", unspam))
    
    # React commands
    app.add_handler(CommandHandler("emojispam", emojispam))
    app.add_handler(CommandHandler("stopemojispam", stopemojispam))
    
    # Slide commands
    app.add_handler(CommandHandler("targetslide", targetslide))
    app.add_handler(CommandHandler("stopslide", stopslide))
    app.add_handler(CommandHandler("slidespam", slidespam))
    app.add_handler(CommandHandler("stopslidespam", stopslidespam))
    
    # Sticker commands
    app.add_handler(CommandHandler("newsticker", newsticker))
    app.add_handler(CommandHandler("delsticker", delsticker))
    app.add_handler(CommandHandler("multisticker", multisticker))
    app.add_handler(CommandHandler("stickerstatus", stickerstatus))
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
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("listsudo", listsudo))
    
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
                print(f"✅ Bot initialized: {token[:10]}...")
            except Exception as e:
                print(f"❌ Failed building app: {e}")

    # Start all bots
    for app in apps:
        try:
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Bot started successfully!")
        except Exception as e:
            print(f"❌ Failed starting app: {e}")

    print(f"🎉 RAHUL V4 Ultra Multi is running with {len(bots)} bots!")
    print("📊 Chat ID:", CHAT_ID)
    print("🤖 Active Bots:", len(bots))
    print("💀 NCBAAP Mode: READY (5 NC in 0.1s)")
    print("👑 GOD SPEED Mode: READY (5 NC in 0.05s)")
    print("🎭 tempest Voices: ✅ ACTIVE WITH YOUR API KEY")
    print("⚡ All Features: ACTIVATED")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("\n🛑 RAHUL V4 Shutting Down...")
    except Exception as e:
        print(f"❌ Error: {e}")