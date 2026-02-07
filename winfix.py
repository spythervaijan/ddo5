import argparse
import json
import os
import time
import random
import logging
import unicodedata
import sqlite3
import re
from playwright.sync_api import sync_playwright
import urllib.parse
import subprocess
import pty
import errno
import sys
from typing import Dict, List
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import threading
import uuid
import signal
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import asyncio
from dotenv import load_dotenv
from playwright_stealth import stealth_sync
from instagrapi import Client
from instagrapi.exceptions import ChallengeRequired, TwoFactorRequired, PleaseWaitFewMinutes, RateLimitError, LoginRequired
import psutil
from queue import Queue, Empty

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_bot.log'),
        logging.StreamHandler()
    ]
)

user_fetching = set()
user_cancel_fetch = set()  # new set
AUTHORIZED_FILE = 'authorized_users.json'
TASKS_FILE = 'tasks.json'
OWNER_TG_ID = int(os.environ.get('OWNER_TG_ID'))
BOT_TOKEN = os.environ.get('BOT_TOKEN')
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

authorized_users = []  # list of {'id': int, 'username': str}
users_data: Dict[int, Dict] = {}  # unlocked data {'accounts': list, 'default': int, 'pairs': dict or None, 'switch_minutes': int, 'threads': int}
users_pending: Dict[int, Dict] = {}  # pending challenges
users_tasks: Dict[int, List[Dict]] = {}  # tasks per user
persistent_tasks = []
running_processes: Dict[int, subprocess.Popen] = {}
waiting_for_otp = {}
user_queues = {}
user_fetching = set()

# Ensure sessions directory exists
os.makedirs('sessions', exist_ok=True)

# === PATCH: Fix instagrapi invalid timestamp bug ===
def _sanitize_timestamps(obj):
    """Fix invalid *_timestamp_us fields in Instagram data"""
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if isinstance(v, int) and k.endswith("_timestamp_us"):
                try:
                    secs = int(v) // 1_000_000  # convert microseconds → seconds
                except Exception:
                    secs = None
                # skip impossible years (>2100 or negative)
                if secs is None or secs < 0 or secs > 4102444800:
                    new_obj[k] = None
                else:
                    new_obj[k] = secs
            else:
                new_obj[k] = _sanitize_timestamps(v)
        return new_obj
    elif isinstance(obj, list):
        return [_sanitize_timestamps(i) for i in obj]
    else:
        return obj


async def playwright_login_and_save_state(username: str, password: str, user_id: int) -> str:
    """
    Async Playwright login.
    - Instagram me login karta hai
    - storage_state ko sessions/<user>_<username>_state.json me save karta hai
    - file path return karta hai
    """
    COOKIE_FILE = f"sessions\\{user_id}_{username}_state.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        context = await browser.new_context(
            user_agent=USER_AGENT,  # tumhara existing USER_AGENT
            viewport={"width": 1280, "height": 720},
        )

        page = await context.new_page()

        login_url = "https://www.instagram.com/accounts/login/?__coig_login=1"
        logging.info("[PLOGIN-ASYNC] Goto %s", login_url)

        await page.goto(login_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)

        logging.info(
            "[PLOGIN-ASYNC] After goto -> URL=%s TITLE=%s",
            page.url,
            await page.title(),
        )

        # ---------- CHECK LOGIN FORM ----------
        username_inputs = await page.locator('input[name="username"]').count()
        if username_inputs == 0:
            logging.warning(
                "[PLOGIN-ASYNC] Username field not found. URL=%s",
                page.url,
            )
            await page.wait_for_timeout(5000)
            username_inputs = await page.locator('input[name=\"username\"]').count()

        if username_inputs == 0:
            # Still nahi mila → intro/splash
            html_snippet = (await page.content())[:1000].replace("\n", " ")
            logging.warning(
                "[PLOGIN-ASYNC] Login form NOT loaded. URL=%s SNIPPET=%s",
                page.url,
                html_snippet,
            )
            await browser.close()
            raise ValueError("ERROR_010: Instagram login form not loaded (stuck on intro/splash)")

        # ---------- HUMAN-LIKE LOGIN ----------
        username_input = page.locator('input[name="username"]')
        password_input = page.locator('input[name="password"]')
        login_button = page.locator('button[type="submit"]').first

        # Username typing
        await username_input.click()
        await page.wait_for_timeout(random.randint(300, 900))
        await username_input.fill("")  # clear
        await username_input.type(username, delay=random.randint(60, 140))  # ms per char

        # Password typing
        await page.wait_for_timeout(random.randint(300, 900))
        await password_input.click()
        await page.wait_for_timeout(random.randint(200, 700))
        await password_input.fill("")
        await password_input.type(password, delay=random.randint(60, 140))

        # Click login with tiny jitter
        await page.wait_for_timeout(random.randint(400, 1000))
        await login_button.click()
        logging.info("[PLOGIN-ASYNC] Submitted login form for %s", username)

        # ---------- POST-LOGIN CHECK (OTP / SUCCESS) ----------
        # Thoda time do redirect ke liye
        await page.wait_for_timeout(5000)

        current_url = page.url
        logging.info("[PLOGIN-ASYNC] After login URL=%s", current_url)

        # Quick OTP detection without long timeout
        otp_locator = page.locator('input[name="verificationCode"]')
        otp_count = await otp_locator.count()

        if otp_count > 0 or "challenge" in current_url or "two_factor" in current_url:
            logging.info(
                "[PLOGIN-ASYNC] OTP / challenge detected for user %s (url=%s, otp_count=%s)",
                username,
                current_url,
                otp_count,
            )
            await browser.close()
            # Abhi ke liye clear error; baad me Telegram OTP flow hook kar sakte hain
            raise ValueError("ERROR_OTP: OTP / challenge required. Please use session/2FA flow.")

        # Agar yahan tak aa gaye aur URL jaise:
        # - /accounts/onetap/...
        # - / (home feed, profile, etc.)
        # to login successful maan lo
        logging.info("[PLOGIN-ASYNC] No OTP required, login looks successful. URL=%s", current_url)

        # Kuch extra wait, phir state save
        await page.wait_for_timeout(4000)

        await context.storage_state(path=COOKIE_FILE)
        logging.info("[PLOGIN-ASYNC] storage_state saved to %s", COOKIE_FILE)

        await browser.close()
        logging.info("[PLOGIN-ASYNC] Browser closed for user_id=%s", user_id)

    return COOKIE_FILE


# 🧩 Monkeypatch instagrapi to fix validation crash
try:
    import instagrapi.extractors as extractors
    _orig_extract_reply_message = extractors.extract_reply_message

    def patched_extract_reply_message(data):
        data = _sanitize_timestamps(data)
        return _orig_extract_reply_message(data)

    extractors.extract_reply_message = patched_extract_reply_message
    print("[Patch] Applied timestamp sanitizer to instagrapi extractors ✅")
except Exception as e:
    print(f"[Patch Warning] Could not patch instagrapi: {e}")
# === END PATCH ===

# --- Playwright sync helper: run sync_playwright() inside a fresh thread ---
def run_with_sync_playwright(fn, *args, **kwargs):
    """
    Runs `fn(p, *args, **kwargs)` where p is the object returned by sync_playwright()
    inside a new thread and returns fn's return value (or raises exception).
    """
    result = {"value": None, "exc": None}

    def target():
        try:
            with sync_playwright() as p:
                result["value"] = fn(p, *args, **kwargs)
        except Exception as e:
            result["exc"] = e

    t = threading.Thread(target=target)
    t.start()
    t.join()
    if result["exc"]:
        raise result["exc"]
    return result["value"]

def load_authorized():
    global authorized_users
    if os.path.exists(AUTHORIZED_FILE):
        with open(AUTHORIZED_FILE, 'r') as f:
            authorized_users = json.load(f)
    # Ensure owner is authorized
    if not any(u['id'] == OWNER_TG_ID for u in authorized_users):
        authorized_users.append({'id': OWNER_TG_ID, 'username': 'owner'})

load_authorized()

def load_users_data():
    global users_data
    users_data = {}
    for file in os.listdir('.'):
        if file.startswith('user_') and file.endswith('.json'):
            user_id_str = file[5:-5]
            if user_id_str.isdigit():
                user_id = int(user_id_str)
                with open(file, 'r') as f:
                    data = json.load(f)
                # Defaults
                if 'pairs' not in data:
                    data['pairs'] = None
                if 'switch_minutes' not in data:
                    data['switch_minutes'] = 10
                if 'threads' not in data:
                    data['threads'] = 1
                users_data[user_id] = data

load_users_data()

def save_authorized():
    with open(AUTHORIZED_FILE, 'w') as f:
        json.dump(authorized_users, f)

def save_user_data(user_id: int, data: Dict):
    with open(f'user_{user_id}.json', 'w') as f:
        json.dump(data, f)

def is_authorized(user_id: int) -> bool:
    return any(u['id'] == user_id for u in authorized_users)

def is_owner(user_id: int) -> bool:
    return user_id == OWNER_TG_ID

def future_expiry(days=365):
    return int(time.time()) + days*24*3600

def convert_for_playwright(insta_file, playwright_file):
    try:
        with open(insta_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        return

    cookies = []
    auth = data.get("authorization_data", {})
    for name, value in auth.items():
        cookies.append({
            "name": name,
            "value": urllib.parse.unquote(value),
            "domain": ".instagram.com",
            "path": "/",
            "expires": future_expiry(),
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        })

    playwright_state = {
        "cookies": cookies,
        "origins": [{"origin": "https://www.instagram.com", "localStorage": []}]
    }

    with open(playwright_file, "w") as f:
        json.dump(playwright_state, f, indent=4)

def get_storage_state_from_instagrapi(settings: Dict):
    cl = Client()
    cl.set_settings(settings)

    # Collect cookies from instagrapi structures (compatible with multiple instagrapi versions)
    cookies_dict = {}
    if hasattr(cl, "session") and cl.session:
        try:
            cookies_dict = cl.session.cookies.get_dict()
        except Exception:
            cookies_dict = {}
    elif hasattr(cl, "private") and hasattr(cl.private, "cookies"):
        try:
            cookies_dict = cl.private.cookies.get_dict()
        except Exception:
            cookies_dict = {}
    elif hasattr(cl, "_http") and hasattr(cl._http, "cookies"):
        try:
            cookies_dict = cl._http.cookies.get_dict()
        except Exception:
            cookies_dict = {}

    cookies = []
    for name, value in cookies_dict.items():
        cookies.append({
            "name": name,
            "value": value,
            "domain": ".instagram.com",
            "path": "/",
            "expires": int(time.time()) + 365*24*3600,
            "httpOnly": True,
            "secure": True,
            "sameSite": "Lax"
        })

    storage_state = {
        "cookies": cookies,
        "origins": [{"origin": "https://www.instagram.com", "localStorage": []}]
    }
    return storage_state

def instagrapi_login(username, password):
    cl = Client()
    session_file = f"{username}_session.json"
    playwright_file = f"{username}_state.json"
    try:
        cl.login(username, password)
        cl.dump_settings(session_file)
        convert_for_playwright(session_file, playwright_file)
    except (ChallengeRequired, TwoFactorRequired):
        raise ValueError("ERROR_004: Login challenge or 2FA required")
    except (PleaseWaitFewMinutes, RateLimitError):
        raise ValueError("ERROR_002: Rate limit exceeded")
    except Exception as e:
        raise ValueError(f"ERROR_007: Login failed - {str(e)}")
    return json.load(open(playwright_file))

def list_group_chats(user_id, storage_state, username, password, max_groups=10, amount=10):
    username = username.strip().lower()
    norm_username = username.strip().lower()
    session_file = f"sessions\\{user_id}_{norm_username}_session.json"
    playwright_file = f"sessions\\{user_id}_{norm_username}_state.json"
    cl = Client()
    updated = False
    new_state = None

    # Load existing session if available
    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
        except Exception:
            pass

    try:
        threads = cl.direct_threads(amount=amount)
        time.sleep(random.uniform(1.0, 3.0))
    except LoginRequired:
        cl.login(username, password)
        cl.dump_settings(session_file)
        convert_for_playwright(session_file, playwright_file)
        updated = True
        threads = cl.direct_threads(amount=amount)
        time.sleep(random.uniform(1.0, 3.0))

    groups = []
    for thread in threads:
        if len(groups) >= max_groups:
            break
        if getattr(thread, "is_group", False):
            member_count = len(getattr(thread, "users", [])) + 1
            if member_count < 3:
                continue

            title = getattr(thread, "thread_title", None) or getattr(thread, "title", None)
            if not title or title.strip() == "":
                try:
                    users_part = ", ".join([u.username for u in getattr(thread, "users", [])][:3])
                    display = users_part if users_part else "<no name>"
                except Exception:
                    display = "<no name>"
            else:
                display = title

            url = f"https://www.instagram.com/direct/t/{getattr(thread, 'thread_id', getattr(thread, 'id', 'unknown'))}"
            groups.append({'display': display, 'url': url})

    if updated and os.path.exists(playwright_file):
        new_state = get_storage_state_from_instagrapi(cl.get_settings())
        with open(playwright_file, 'w') as f:
            json.dump(new_state, f)
    elif os.path.exists(playwright_file):
        new_state = json.load(open(playwright_file))
    else:
        new_state = storage_state

    return groups, new_state

def get_dm_thread_url(user_id, username, password, target_username):
    norm_username = username.strip().lower()
    session_file = f"sessions\\{user_id}_{norm_username}_session.json"
    playwright_file = f"sessions\\{user_id}_{norm_username}_state.json"
    cl = Client()
    updated = False

    if os.path.exists(session_file):
        try:
            cl.load_settings(session_file)
        except Exception:
            pass

    try:
        threads = cl.direct_threads(amount=10)
        time.sleep(random.uniform(1.0, 3.0))
    except LoginRequired:
        cl.login(username, password)
        cl.dump_settings(session_file)
        convert_for_playwright(session_file, playwright_file)
        updated = True
        threads = cl.direct_threads(amount=10)
        time.sleep(random.uniform(1.0, 3.0))

    for thread in threads:
        if not getattr(thread, 'is_group', True) and len(getattr(thread, 'users', [])) == 1:
            try:
                user = thread.users[0]
                if user.username == target_username:
                    thread_id = getattr(thread, 'thread_id', getattr(thread, 'id', None))
                    if thread_id:
                        url = f"https://www.instagram.com/direct/t/{thread_id}/"
                        if updated:
                            settings = cl.get_settings()
                            new_state = get_storage_state_from_instagrapi(settings)
                            with open(playwright_file, 'w') as f:
                                json.dump(new_state, f)
                        return url
            except Exception:
                continue

    return None

def perform_login(page, username, password):
    try:
        page.evaluate("""() => {
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            window.chrome = { app: {}, runtime: {} };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: 'denied' }) :
                originalQuery(parameters)
            );
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Google Inc. (Intel)';
                if (parameter === 37446) return 'ANGLE (Intel, Intel(R) UHD Graphics 630 (0x00003E9B) Direct3D11 vs_5_0 ps_5_0, D3D11)';
                return getParameter.call(this, parameter);
            };
        }""")

        username_locator = page.locator('input[name="username"]')
        username_locator.wait_for(state='visible', timeout=10000)
        username_locator.focus()
        time.sleep(random.uniform(0.5, 1.5))
        for char in username:
            username_locator.press(char)
            time.sleep(random.uniform(0.05, 0.15))

        password_locator = page.locator('input[name="password"]')
        password_locator.wait_for(state='visible', timeout=10000)
        time.sleep(random.uniform(0.5, 1.5))
        password_locator.focus()
        time.sleep(random.uniform(0.3, 0.8))
        for char in password:
            password_locator.press(char)
            time.sleep(random.uniform(0.05, 0.15))

        time.sleep(random.uniform(1.0, 2.5))

        submit_locator = page.locator('button[type="submit"]')
        submit_locator.wait_for(state='visible', timeout=10000)
        if not submit_locator.is_enabled():
            raise Exception("Submit button not enabled")
        submit_locator.click()

        try:
            page.wait_for_url(lambda url: 'accounts/login' not in url and 'challenge' not in url and 'two_factor' not in url, timeout=60000)
            
            if page.locator('[role="alert"]').count() > 0:
                error_text = page.locator('[role="alert"]').inner_text().lower()
                if 'incorrect' in error_text or 'wrong' in error_text:
                    raise ValueError("ERROR_001: Invalid credentials")
                elif 'wait' in error_text or 'few minutes' in error_text or 'too many' in error_text:
                    raise ValueError("ERROR_002: Rate limit exceeded")
                else:
                    raise ValueError(f"ERROR_003: Login error - {error_text}")
        except TimeoutError:
            current_url = page.url
            page_content = page.content().lower()
            if 'challenge' in current_url:
                raise ValueError("ERROR_004: Login challenge required")
            elif 'two_factor' in current_url or 'verify' in current_url:
                raise ValueError("ERROR_005: 2FA verification required")
            elif '429' in page_content or 'rate limit' in page_content or 'too many requests' in page_content:
                raise ValueError("ERROR_002: Rate limit exceeded")
            elif page.locator('[role="alert"]').count() > 0:
                error_text = page.locator('[role="alert"]').inner_text().lower()
                raise ValueError(f"ERROR_006: Login failed - {error_text}")
            else:
                raise ValueError("ERROR_007: Login timeout or unknown error")

        logging.info("Login successful")
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        raise

# ---------------- Globals for PTY ----------------
APP = None
LOOP = None
SESSIONS = {}
SESSIONS_LOCK = threading.Lock()

# ---------------- Child PTY login ----------------
def child_login(user_id: int, username: str, password: str):
    cl = Client()
    username = username.strip().lower()
    session_file = f"sessions\\{user_id}_{username}_session.json"
    playwright_file = f"sessions\\{user_id}_{username}_state.json"
    try:
        print(f"[{username}] ⚙️ Attempting login.. if you are stucked here check your gmail or messages check for otp and enter otp here eg: 192122.")
        cl.login(username, password)
        cl.dump_settings(session_file)
        convert_for_playwright(session_file, playwright_file)
        print(f"[{username}] ✅ Logged in successfully. Session saved: {session_file}")
    except TwoFactorRequired:
        print(f" Enter code (6 digits) for {username} (2FA): ", end="", flush=True)
        otp = input().strip()
        try:
            cl.login(username, password, verification_code=otp)
            cl.dump_settings(session_file)
            convert_for_playwright(session_file, playwright_file)
            print(f"[{username}] ✅ OTP resolved. Logged in. Session saved: {session_file}")
        except Exception as e:
            print(f"[{username}] ❌ OTP failed: {e}")
    except ChallengeRequired:
        print(f" Enter code (6 digits) for {username} (Challenge): ", end="", flush=True)
        otp = input().strip()
        try:
            cl.challenge_resolve(cl.last_json, security_code=otp)
            cl.dump_settings(session_file)
            convert_for_playwright(session_file, playwright_file)
            print(f"[{username}] ✅ OTP resolved. Logged in. Session saved: {session_file}")
        except Exception as e:
            print(f"[{username}] ❌ OTP failed: {e}")
    except Exception as e:
        print(f"[{username}] ❌ Login failed: {e}")
    finally:
        time.sleep(0.5)
        sys.exit(0)

# ---------------- PTY reader thread ----------------
def reader_thread(user_id: int, chat_id: int, master_fd: int, username: str, password: str):
    global APP, LOOP
    buf = b""
    while True:
        try:
            data = os.read(master_fd, 1024)
            if not data:
                break
            buf += data
            while b"\n" in buf or len(buf) > 2048:
                if b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    text = line.decode(errors="ignore").strip()
                else:
                    text = buf.decode(errors="ignore")
                    buf = b""
                if not text:
                    continue
                if text.startswith("Code entered"):
                    continue
                lower = text.lower()
                if (
                    len(text) > 300
                    or "cdninstagram.com" in lower
                    or "http" in lower
                    or "{" in text
                    or "}" in text
                    or "debug" in lower
                    or "info" in lower
                    or "urllib3" in lower
                    or "connection" in lower
                    or "starting new https" in lower
                    or "instagrapi" in lower
                ):
                    continue
                try:
                    if APP and LOOP:
                        asyncio.run_coroutine_threadsafe(
                            APP.bot.send_message(chat_id=chat_id, text=f"🔥{text}"), LOOP
                        )
                except Exception:
                    logging.error("[THREAD] send_message failed")
        except OSError as e:
            if e.errno == errno.EIO:
                break
            else:
                logging.error("[THREAD] PTY read error: %s", e)
                break
        except Exception as e:
            logging.error("[THREAD] Unexpected error: %s", e)
            break
    try:
        playwright_file = f"sessions\\{user_id}_{username}_state.json"
        if os.path.exists(playwright_file):
            with open(playwright_file, 'r') as f:
                state = json.load(f)
            if user_id in users_data:
                data = users_data[user_id]
            else:
                data = {'accounts': [], 'default': None, 'pairs': None, 'switch_minutes': 10, 'threads': 1}
            # normalize incoming username
            norm_username = username.strip().lower()

            for i, acc in enumerate(data['accounts']):
                if acc.get('ig_username', '').strip().lower() == norm_username:
                    # overwrite existing entry for exact same username (normalized)
                    data['accounts'][i] = {'ig_username': norm_username, 'password': password, 'storage_state': state}
                    data['default'] = i
                    break
            else:
                # not found -> append new normalized account
                data['accounts'].append({'ig_username': norm_username, 'password': password, 'storage_state': state})
                data['default'] = len(data['accounts']) - 1

            save_user_data(user_id, data)
            users_data[user_id] = data

            # send msg via threadsafe
            asyncio.run_coroutine_threadsafe(
                APP.bot.send_message(chat_id, "✅ Login successful and saved securely! 🎉"),
                LOOP
            )
        else:
            asyncio.run_coroutine_threadsafe(
                APP.bot.send_message(chat_id, "⚠️ Login failed. No session saved."),
                LOOP
            )
    except Exception as e:
        logging.error("[THREAD] Post-login save error: %s", e)
    finally:
        # Cleanup
        os.close(master_fd)
        with SESSIONS_LOCK:
            SESSIONS.pop(user_id, None)

def windows_console_login(user_id: int, username: str, password: str, chat_id: int):
    """Windows console-based login without PTY"""
    cl = Client()
    username = username.strip().lower()
    session_file = f"sessions\\{user_id}_{username}_session.json"
    playwright_file = f"sessions\\{user_id}_{username}_state.json"
    
    try:
        print(f"[{username}] ⚙️ Attempting login...")
        cl.login(username, password)
        cl.dump_settings(session_file)
        convert_for_playwright(session_file, playwright_file)
        return True, "✅ Logged in successfully!"
    except TwoFactorRequired:
        return False, "2FA_REQUIRED"
    except ChallengeRequired:
        return False, "CHALLENGE_REQUIRED"
    except Exception as e:
        return False, f"Login failed: {e}"

def handle_windows_login_otp(user_id: int, username: str, password: str, otp: str, challenge_type: str):
    """Handle OTP for Windows login"""
    cl = Client()
    session_file = f"sessions\\{user_id}_{username}_session.json"
    playwright_file = f"sessions\\{user_id}_{username}_state.json"
    
    try:
        if challenge_type == "2FA_REQUIRED":
            cl.login(username, password, verification_code=otp)
        elif challenge_type == "CHALLENGE_REQUIRED":
            cl.challenge_resolve(cl.last_json, security_code=otp)
        
        cl.dump_settings(session_file)
        convert_for_playwright(session_file, playwright_file)
        return True, "✅ OTP resolved. Logged in successfully!"
    except Exception as e:
        return False, f"OTP failed: {e}"

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id in waiting_for_otp:
        if len(text) == 6 and text.isdigit():
            challenge_info = waiting_for_otp[user_id]
            username = challenge_info['username']
            password = challenge_info['password']
            challenge_type = challenge_info['type']
            
            success, message = handle_windows_login_otp(user_id, username, password, text, challenge_type)
            
            if success:
                # Save to user data
                playwright_file = f"sessions\\{user_id}_{username}_state.json"
                if os.path.exists(playwright_file):
                    with open(playwright_file, 'r') as f:
                        state = json.load(f)
                    
                    if user_id in users_data:
                        data = users_data[user_id]
                    else:
                        data = {'accounts': [], 'default': None, 'pairs': None, 'switch_minutes': 10, 'threads': 1}
                    
                    norm_username = username.strip().lower()
                    found = False
                    
                    for i, acc in enumerate(data['accounts']):
                        if acc.get('ig_username', '').strip().lower() == norm_username:
                            data['accounts'][i] = {'ig_username': norm_username, 'password': password, 'storage_state': state}
                            data['default'] = i
                            found = True
                            break
                    
                    if not found:
                        data['accounts'].append({'ig_username': norm_username, 'password': password, 'storage_state': state})
                        data['default'] = len(data['accounts']) - 1
                    
                    save_user_data(user_id, data)
                    users_data[user_id] = data
                    
                    await update.message.reply_text("✅ Login successful and saved securely! 🎉")
                else:
                    await update.message.reply_text("⚠️ Login failed. No session saved.")
            else:
                await update.message.reply_text(f"❌ {message}")
            
            del waiting_for_otp[user_id]
            return
        else:
            await update.message.reply_text("❌ Invalid code. Please enter 6-digit code.")
            return

USERNAME, PASSWORD = range(2)
PLO_USERNAME, PLO_PASSWORD = range(2)
SLOG_SESSION, SLOG_USERNAME = range(2)
PSID_SESSION, PSID_USERNAME = range(2)
MODE, SELECT_GC, TARGET, MESSAGES = range(4)
P_MODE, P_TARGET_DISPLAY, P_THREAD_URL, P_MESSAGES = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to Spyther's spam bot ⚡ type /help to see available commands")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    help_text = """
🌟 Available commands: 🌟
 /help ⚡ - Show this help
 /login 📱 - Login to Instagram account
 /plogin 🔐 - Playwright human-like login
 /slogin 🔑 - Login with session ID
 /psid 🔑 - Proxy session ID login
 /viewmyac 👀 - View your saved accounts
 /setig 🔄 <number> - Set default account
 /pair 📦 ig1-ig2 - Create account pair for rotation
 /unpair ✨ - to unpair paired accounts (unpair all or unpair <account>
 /switch ⏱️ <min> - Set switch interval (5+ min)
 /threads 🔢 <1-5> - Set number of threads
 /viewpref ⚙️ - View preferences
 /attack 💥 - Start sending messages
 /pattack 💥 - Proxy attack
 /stop 🛑 <pid/all> - Stop tasks
 /task 📋 - View ongoing tasks
 /logout 🚪 <username> - Logout and remove account
 /kill 🔪 <pid> - Kill process (admin)
 /flush 🧹 - Stop all tasks globally
 /usg 📊 - System usage
 /cancel 🚫 - Cancel ongoing fetch
    """
    if is_owner(user_id):
        help_text += """
Admin commands: 👑
 /add ➕ <tg_id> - Add authorized user
 /remove ➖ <tg_id> - Remove authorized user
 /users 📜 - List authorized users
 /flush 🧹 - Stop all tasks globally
        """
    await update.message.reply_text(help_text)

async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return ConversationHandler.END
    await update.message.reply_text("📱 Enter Instagram username: 📱")
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ig_username'] = update.message.text.strip().lower()
    await update.message.reply_text("🔒 Enter password: 🔒")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    username = context.user_data['ig_username']
    password = update.message.text.strip()
    
    await update.message.reply_text("🔄 Starting login process...")
    
    # Windows console login
    success, message = windows_console_login(user_id, username, password, chat_id)
    
    if success:
        await update.message.reply_text("✅ Login successful and saved securely! 🎉")
    elif message in ["2FA_REQUIRED", "CHALLENGE_REQUIRED"]:
        waiting_for_otp[user_id] = {
            'username': username,
            'password': password,
            'type': message
        }
        await update.message.reply_text("🔐 OTP/Challenge required. Please enter the 6-digit code:")
    else:
        await update.message.reply_text(f"❌ {message}")
    
    return ConversationHandler.END

async def plogin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return ConversationHandler.END

    await update.message.reply_text("🔐 Enter Instagram username for Playwright login: ")
    return PLO_USERNAME

async def plogin_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['pl_username'] = update.message.text.strip().lower()
    await update.message.reply_text("🔒 Enter password: 🔒")
    return PLO_PASSWORD

async def plogin_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    username = context.user_data['pl_username']
    password = update.message.text.strip()

    await update.message.reply_text("🔄 Starting Playwright login...")

    try:
        state_file = await playwright_login_and_save_state(username, password, user_id)
        logging.info("[PLOGIN] Loading storage_state from %s", state_file)
        state = json.load(open(state_file))

        cookies = [c for c in state.get('cookies', []) if c.get('domain') == '.instagram.com']
        logging.info("[PLOGIN] cookies for .instagram.com = %s", len(cookies))

        sessionid = None
        for c in cookies:
            if c.get("name") == "sessionid":
                sessionid = c.get("value")
                break

        if not sessionid:
            logging.error("[PLOGIN] sessionid cookie not found in storage_state")
            raise ValueError("ERROR_011: sessionid cookie not found")

        cl = Client()
        logging.info("[PLOGIN] Logging into Instagrapi using sessionid (len=%s)", len(sessionid))
        cl.login_by_sessionid(sessionid)

        session_file = f"sessions\\{user_id}_{username}_session.json"
        logging.info("[PLOGIN] Dumping Instagrapi settings to %s", session_file)
        cl.dump_settings(session_file)

        if user_id not in users_data:
            users_data[user_id] = {
                'accounts': [],
                'default': None,
                'pairs': None,
                'switch_minutes': 10,
                'threads': 1,
            }
            save_user_data(user_id, users_data[user_id])

        data = users_data[user_id]
        found = False
        for i, acc in enumerate(data['accounts']):
            if acc.get('ig_username', '').strip().lower() == username:
                acc['password'] = password
                acc['storage_state'] = state
                data['default'] = i
                found = True
                logging.info("[PLOGIN] Updated existing account index=%s", i)
                break

        if not found:
            data['accounts'].append({
                'ig_username': username,
                'password': password,
                'storage_state': state,
            })
            data['default'] = len(data['accounts']) - 1
            logging.info("[PLOGIN] Added new account, total=%s", len(data['accounts']))

        save_user_data(user_id, data)

        await update.message.reply_text("✅ Playwright login successful! Sessions saved. 🎉")

    except ValueError as ve:
        err_msg = str(ve)
        logging.error("[PLOGIN] ValueError: %s", err_msg)
        await update.message.reply_text(f"❌ Login failed: {err_msg}")

    except Exception as e:
        err_msg = str(e)
        logging.error("[PLOGIN] Unexpected error: %s", err_msg)
        await update.message.reply_text(f"❌ Unexpected login error: {err_msg}")

    return ConversationHandler.END

async def slogin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return ConversationHandler.END

    await update.message.reply_text("🔑 Enter session ID: 🔑")
    return SLOG_SESSION

async def slogin_get_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['session_id'] = update.message.text.strip()
    await update.message.reply_text("📱 Enter Instagram username: 📱")
    return SLOG_USERNAME

async def slogin_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    username = update.message.text.strip().lower()
    session_id = context.user_data['session_id']

    await update.message.reply_text("🔄 Starting session login...")

    try:
        cl = Client()
        cl.login_by_sessionid(session_id)
        session_file = f"sessions\\{user_id}_{username}_session.json"
        cl.dump_settings(session_file)

        playwright_file = f"sessions\\{user_id}_{username}_state.json"
        convert_for_playwright(session_file, playwright_file)
        state = json.load(open(playwright_file))

        if user_id not in users_data:
            users_data[user_id] = {
                'accounts': [],
                'default': None,
                'pairs': None,
                'switch_minutes': 10,
                'threads': 1,
            }
            save_user_data(user_id, users_data[user_id])

        data = users_data[user_id]
        found = False
        for i, acc in enumerate(data['accounts']):
            if acc.get('ig_username', '').strip().lower() == username:
                acc['password'] = None
                acc['storage_state'] = state
                data['default'] = i
                found = True
                break

        if not found:
            data['accounts'].append({
                'ig_username': username,
                'password': None,
                'storage_state': state,
            })
            data['default'] = len(data['accounts']) - 1

        save_user_data(user_id, data)

        await update.message.reply_text("✅ Session login successful! Sessions saved. 🎉")

    except Exception as e:
        await update.message.reply_text(f"❌ Login failed: {str(e)}")

    return ConversationHandler.END

async def psid_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return ConversationHandler.END

    await update.message.reply_text("🔑 Enter proxy session ID: 🔑")
    return PSID_SESSION

async def psid_get_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['psid_session_id'] = update.message.text.strip()
    await update.message.reply_text("📱 Enter Instagram username: 📱")
    return PSID_USERNAME

async def psid_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    username = update.message.text.strip().lower()
    session_id = context.user_data['psid_session_id']

    await update.message.reply_text("🔄 Starting proxy session login...")

    try:
        cl = Client(proxy="http://proxy_url_here")  # Replace with actual proxy if needed
        cl.login_by_sessionid(session_id)
        session_file = f"sessions\\{user_id}_{username}_session.json"
        cl.dump_settings(session_file)

        playwright_file = f"sessions\\{user_id}_{username}_state.json"
        convert_for_playwright(session_file, playwright_file)
        state = json.load(open(playwright_file))

        if user_id not in users_data:
            users_data[user_id] = {
                'accounts': [],
                'default': None,
                'pairs': None,
                'switch_minutes': 10,
                'threads': 1,
            }
            save_user_data(user_id, users_data[user_id])

        data = users_data[user_id]
        found = False
        for i, acc in enumerate(data['accounts']):
            if acc.get('ig_username', '').strip().lower() == username:
                acc['password'] = None
                acc['storage_state'] = state
                data['default'] = i
                found = True
                break

        if not found:
            data['accounts'].append({
                'ig_username': username,
                'password': None,
                'storage_state': state,
            })
            data['default'] = len(data['accounts']) - 1

        save_user_data(user_id, data)

        await update.message.reply_text("✅ Proxy session login successful! Sessions saved. 🎉")

    except Exception as e:
        await update.message.reply_text(f"❌ Login failed: {str(e)}")

    return ConversationHandler.END

async def viewmyac(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    if user_id not in users_data or not users_data[user_id]['accounts']:
        await update.message.reply_text("❌ No accounts saved. Use /login to add. ❌")
        return
    data = users_data[user_id]
    msg = "📱 Your accounts: 📱\n"
    for i, acc in enumerate(data['accounts']):
        star = "⭐" if i == data['default'] else ""
        msg += f"{i+1}. @{acc['ig_username']} {star}\n"
    await update.message.reply_text(msg)

async def setig(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /setig <number> ❗")
        return
    num = int(context.args[0]) - 1
    if user_id not in users_data or num < 0 or num >= len(users_data[user_id]['accounts']):
        await update.message.reply_text("⚠️ Invalid number. ⚠️")
        return
    users_data[user_id]['default'] = num
    save_user_data(user_id, users_data[user_id])
    await update.message.reply_text("✅ Default account set! ⭐")

async def pair_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /pair ig1-ig2-ig3... ❗")
        return
    pair_str = context.args[0].lower()
    pair_list = [u.strip() for u in pair_str.split('-') if u.strip()]
    if len(pair_list) < 2:
        await update.message.reply_text("⚠️ At least 2 accounts needed for pair. ⚠️")
        return
    data = users_data.get(user_id)
    if not data or not data['accounts']:
        await update.message.reply_text("❌ No accounts. Use /login first. ❌")
        return
    valid_accounts = {acc['ig_username'].lower(): acc for acc in data['accounts']}
    invalid = [u for u in pair_list if u not in valid_accounts]
    if invalid:
        await update.message.reply_text(f"⚠️ Invalid accounts: {', '.join(invalid)} ⚠️")
        return
    data['pairs'] = {
        'accounts': pair_list,
        'default_index': 0
    }
    save_user_data(user_id, data)
    await update.message.reply_text(f"✅ Pair created: {pair_str} 📦")

async def unpair_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    data = users_data.get(user_id)
    if not data or not data.get('pairs'):
        await update.message.reply_text("❌ No pairs set. ❌")
        return
    if context.args and context.args[0].lower() == 'all':
        data['pairs'] = None
        save_user_data(user_id, data)
        await update.message.reply_text("✅ All pairs removed! ✨")
        return
    elif context.args:
        acc_to_remove = context.args[0].lower()
        if acc_to_remove in data['pairs']['accounts']:
            data['pairs']['accounts'].remove(acc_to_remove)
            if not data['pairs']['accounts']:
                data['pairs'] = None
            save_user_data(user_id, data)
            await update.message.reply_text(f"✅ Removed {acc_to_remove} from pair! ✨")
        else:
            await update.message.reply_text("⚠️ Account not in pair. ⚠️")
    else:
        await update.message.reply_text("❗ Usage: /unpair all or /unpair <account> ❗")

async def switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /switch <minutes> (min 5) ❗")
        return
    minutes = int(context.args[0])
    if minutes < 5:
        await update.message.reply_text("⚠️ Minimum 5 minutes. ⚠️")
        return
    data = users_data.get(user_id, {})
    data['switch_minutes'] = minutes
    save_user_data(user_id, data)
    await update.message.reply_text(f"✅ Switch interval set to {minutes} min! ⏱️")

async def threads_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /threads <1-5> ❗")
        return
    threads_n = int(context.args[0])
    if threads_n < 1 or threads_n > 5:
        await update.message.reply_text("⚠️ Between 1-5 only. ⚠️")
        return
    data = users_data.get(user_id, {})
    data['threads'] = threads_n
    save_user_data(user_id, data)
    await update.message.reply_text(f"✅ Threads set to {threads_n}! 🔢")

async def viewpref(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    data = users_data.get(user_id, {})
    msg = "⚙️ Preferences: ⚙️\n"
    msg += f"Switch: {data.get('switch_minutes', 10)} min ⏱️\n"
    msg += f"Threads: {data.get('threads', 1)} 🔢\n"
    if data.get('pairs'):
        msg += f"Pair: {'-'.join(data['pairs']['accounts'])} 📦\n"
    await update.message.reply_text(msg)

async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /logout <username> ❗")
        return
    username = context.args[0].strip().lower()
    data = users_data.get(user_id)
    if not data or not data['accounts']:
        await update.message.reply_text("❌ No accounts. ❌")
        return
    found = False
    for i, acc in enumerate(data['accounts'][:]):
        if acc['ig_username'].lower() == username:
            del data['accounts'][i]
            found = True
            if data['default'] == i:
                data['default'] = 0 if data['accounts'] else None
            elif data['default'] > i:
                data['default'] -= 1
            # Remove files
            session_file = f"sessions\\{user_id}_{username}_session.json"
            state_file = f"sessions\\{user_id}_{username}_state.json"
            if os.path.exists(session_file):
                os.remove(session_file)
            if os.path.exists(state_file):
                os.remove(state_file)
            break
    if found:
        if data.get('pairs'):
            data['pairs']['accounts'] = [u for u in data['pairs']['accounts'] if u != username]
            if not data['pairs']['accounts']:
                data['pairs'] = None
        save_user_data(user_id, data)
        await update.message.reply_text(f"✅ Logged out and removed @{username}! 🚪")
    else:
        await update.message.reply_text("⚠️ Account not found. ⚠️")

async def cmd_kill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⚠️ you are not an admin ⚠️")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /kill <pid> ❗")
        return
    pid = int(context.args[0])
    proc = running_processes.get(pid)
    if proc:
        try:
            proc.terminate()
        except Exception:
            pass
        await asyncio.sleep(2)
        if proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass
        running_processes.pop(pid, None)
        for t in persistent_tasks:
            if t.get('pid') == pid:
                mark_task_stopped_persistent(t['id'])
                break
        await update.message.reply_text(f"🔪 Killed PID {pid}!")
    else:
        await update.message.reply_text("⚠️ PID not found. ⚠️")

async def attack_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return ConversationHandler.END
    data = users_data.get(user_id)
    if not data or not data['accounts']:
        await update.message.reply_text("❌ No accounts. Use /login first. ❌")
        return ConversationHandler.END
    await update.message.reply_text("💥 Attack mode: gc (group chat) or dm? 💥")
    return MODE

async def get_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    mode = update.message.text.strip().lower()
    if mode not in ['gc', 'dm']:
        await update.message.reply_text("⚠️ Invalid: gc or dm only. ⚠️")
        return MODE
    context.user_data['mode'] = mode
    user_id = update.effective_user.id
    data = users_data[user_id]
    default_idx = data['default']
    acc = data['accounts'][default_idx]
    username = acc['ig_username']
    password = acc.get('password')
    storage_state = acc['storage_state']
    await update.message.reply_text("🔄 Fetching chats...")
    try:
        groups, new_state = list_group_chats(user_id, storage_state, username, password)
        if new_state:
            data['accounts'][default_idx]['storage_state'] = new_state
            save_user_data(user_id, data)
        if not groups:
            await update.message.reply_text("❌ No group chats found. ❌")
            return ConversationHandler.END
        msg = "📁 Select group chat: 📁\n"
        for i, g in enumerate(groups, 1):
            msg += f"{i}. {g['display']}\n"
        await update.message.reply_text(msg)
        context.user_data['groups'] = groups
        return SELECT_GC
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching: {str(e)}")
        return ConversationHandler.END

async def select_gc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("⚠️ Enter number only. ⚠️")
        return SELECT_GC
    num = int(text) - 1
    groups = context.user_data.get('groups')
    if num < 0 or num >= len(groups):
        await update.message.reply_text("⚠️ Invalid number. ⚠️")
        return SELECT_GC
    context.user_data['thread_url'] = groups[num]['url']
    context.user_data['target_display'] = groups[num]['display']
    await update.message.reply_text("📝 Enter messages (txt file or text separated by |): 📝")
    return MESSAGES

async def get_target_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    target = update.message.text.strip().lower()
    user_id = update.effective_user.id
    data = users_data[user_id]
    default_idx = data['default']
    acc = data['accounts'][default_idx]
    username = acc['ig_username']
    password = acc.get('password')
    await update.message.reply_text("🔄 Fetching DM thread...")
    try:
        thread_url = get_dm_thread_url(user_id, username, password, target)
        if not thread_url:
            await update.message.reply_text("❌ DM thread not found. ❌")
            return ConversationHandler.END
        context.user_data['thread_url'] = thread_url
        context.user_data['target_display'] = target
        await update.message.reply_text("📝 Enter messages (txt file or text separated by |): 📝")
        return MESSAGES
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        return ConversationHandler.END

async def get_messages_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    document = update.message.document
    file = await document.get_file()
    names_file = f"names_{user_id}_{uuid.uuid4()}.txt"
    await file.download_to_drive(names_file)
    return await launch_attack(update, context, names_file)

async def get_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    messages = [m.strip() for m in update.message.text.split('|') if m.strip()]
    if not messages:
        await update.message.reply_text("⚠️ No messages provided. ⚠️")
        return MESSAGES
    names_file = f"names_{user_id}_{uuid.uuid4()}.txt"
    with open(names_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(messages))
    return await launch_attack(update, context, names_file)

async def launch_attack(update: Update, context: ContextTypes.DEFAULT_TYPE, names_file: str) -> int:
    user_id = update.effective_user.id
    data = users_data[user_id]
    pairs = data.get('pairs')
    pair_list = pairs['accounts'] if pairs else [data['accounts'][data['default']]['ig_username']]
    switch_minutes = data.get('switch_minutes', 10)
    threads_n = data.get('threads', 1)
    warning = "⚠️ Warning: Use at own risk! ⚠️\n"
    tasks = users_tasks.get(user_id, [])
    running_msg = [t for t in tasks if t.get('type') == 'message_attack' and t['status'] == 'running' and t['proc'].poll() is None]
    if len(running_msg) >= 5:
        await update.message.reply_text("⚠️ Max 5 message attacks running. Stop one first. ⚠️")
        if os.path.exists(names_file):
            os.remove(names_file)
        return ConversationHandler.END

    thread_url = context.user_data['thread_url']
    target_display = context.user_data['target_display']
    target_mode = context.user_data['mode']
    start_idx = pairs['default_index'] if pairs else 0
    start_u = pair_list[start_idx]
    start_acc = next(acc for acc in data['accounts'] if acc['ig_username'] == start_u)
    start_pass = start_acc['password']
    start_u = start_u.strip().lower()
    state_file = f"sessions\\{user_id}_{start_u}_state.json"
    if not os.path.exists(state_file):
        with open(state_file, 'w') as f:
            json.dump(start_acc['storage_state'], f)

    cmd = [
        "python", "msg.py",
        "--username", start_u,
        "--password", start_pass,
        "--thread-url", thread_url,
        "--names", names_file,
        "--tabs", str(threads_n),
        "--headless", "true",
        "--storage-state", state_file
    ]
    proc = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    running_processes[proc.pid] = proc
    pid = proc.pid
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "user_id": user_id,
        "type": "message_attack",
        "pair_list": pair_list,
        "pair_index": start_idx,
        "switch_minutes": switch_minutes,
        "threads": threads_n,
        "names_file": names_file,
        "target_thread_url": thread_url,
        "target_type": target_mode,
        "target_display": target_display,
        "last_switch_time": time.time(),
        "status": "running",
        "cmd": cmd,
        "pid": pid,
        "display_pid": pid,
        "proc_list": [pid],
        "proc": proc,
        "start_time": time.time()
    }
    persistent_tasks.append(task)
    save_persistent_tasks()
    tasks.append(task)
    users_tasks[user_id] = tasks
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Message attack start user={user_id} task={task_id} target={target_display} pid={pid}")

    status = "Spamming...!\n"
    curr_u = pair_list[task['pair_index']]
    for u in pair_list:
        if u == curr_u:
            status += f"using - {u}\n"
        else:
            status += f"cooldown - {u}\n"
    status += f"To stop 🛑 type /stop {task['display_pid']} or /stop all to stop all processes."

    sent_msg = await update.message.reply_text(warning + status)
    task['status_chat_id'] = update.message.chat_id
    task['status_msg_id'] = sent_msg.message_id
    return ConversationHandler.END

async def pattack_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return ConversationHandler.END
    data = users_data.get(user_id)
    if not data or not data['accounts']:
        await update.message.reply_text("❌ No accounts. Use /login first. ❌")
        return ConversationHandler.END
    await update.message.reply_text("💥 Proxy attack mode: gc (group chat) or dm? 💥")
    return P_MODE

async def p_get_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    mode = update.message.text.strip().lower()
    if mode not in ['gc', 'dm']:
        await update.message.reply_text("⚠️ Invalid: gc or dm only. ⚠️")
        return P_MODE
    context.user_data['mode'] = mode
    await update.message.reply_text("📛 Enter target display name: 📛")
    return P_TARGET_DISPLAY

async def p_get_target_display(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['target_display'] = update.message.text.strip()
    await update.message.reply_text("🔗 Enter thread URL: 🔗")
    return P_THREAD_URL

async def p_get_thread_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    thread_url = update.message.text.strip()
    if not thread_url.startswith('https://www.instagram.com/direct/t/'):
        await update.message.reply_text("⚠️ Invalid URL format. ⚠️")
        return P_THREAD_URL
    context.user_data['thread_url'] = thread_url
    await update.message.reply_text("📝 Enter messages (txt file or text separated by |): 📝")
    return P_MESSAGES

async def p_get_messages_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    document = update.message.document
    file = await document.get_file()
    names_file = f"names_{user_id}_{uuid.uuid4()}.txt"
    await file.download_to_drive(names_file)
    return await launch_attack(update, context, names_file)

async def p_get_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    messages = [m.strip() for m in update.message.text.split('|') if m.strip()]
    if not messages:
        await update.message.reply_text("⚠️ No messages provided. ⚠️")
        return P_MESSAGES
    names_file = f"names_{user_id}_{uuid.uuid4()}.txt"
    with open(names_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(messages))
    return await launch_attack(update, context, names_file)

def load_persistent_tasks():
    global persistent_tasks
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            persistent_tasks = json.load(f)
    else:
        persistent_tasks = []

def save_persistent_tasks():
    """
    Safely write persistent_tasks to TASKS_FILE.
    Removes runtime-only values (like 'proc') and ensures JSON-safe data.
    """
    safe_list = []
    for t in persistent_tasks:
        cleaned = {}
        for k, v in t.items():
            if k == 'proc':
                continue
            if isinstance(v, (int, float, str, bool, dict, list, type(None))):
                cleaned[k] = v
            else:
                try:
                    json.dumps(v)
                    cleaned[k] = v
                except Exception:
                    cleaned[k] = str(v)
        safe_list.append(cleaned)

    temp_file = TASKS_FILE + '.tmp'
    with open(temp_file, 'w') as f:
        json.dump(safe_list, f, indent=2)
    os.replace(temp_file, TASKS_FILE)

def mark_task_stopped_persistent(task_id: str):
    global persistent_tasks
    for task in persistent_tasks:
        if task['id'] == task_id:
            task['status'] = 'stopped'
            save_persistent_tasks()
            break

def update_task_pid_persistent(task_id: str, new_pid: int):
    global persistent_tasks
    for task in persistent_tasks:
        if task['id'] == task_id:
            task['pid'] = new_pid
            save_persistent_tasks()
            break

def mark_task_completed_persistent(task_id: str):
    global persistent_tasks
    for task in persistent_tasks:
        if task['id'] == task_id:
            task['status'] = 'completed'
            save_persistent_tasks()
            break

def restore_tasks_on_start():
    load_persistent_tasks()
    print(f"🔄 Restoring {len([t for t in persistent_tasks if t.get('type') == 'message_attack' and t['status'] == 'running'])} running message attacks...")
    for task in persistent_tasks[:]:
        if task.get('type') == 'message_attack' and task['status'] == 'running':
            old_pid = task['pid']
            try:
                import signal
                os.kill(old_pid, signal.SIGTERM)
                time.sleep(1)
            except (OSError, AttributeError):
                try:
                    import ctypes
                    ctypes.windll.kernel32.TerminateProcess(old_pid, 0)
                except:
                    pass
            user_id = task['user_id']
            data = users_data.get(user_id)
            if not data:
                mark_task_stopped_persistent(task['id'])
                continue
            pair_list = task['pair_list']
            curr_idx = task['pair_index']
            curr_u = pair_list[curr_idx]
            curr_acc = None
            for acc in data['accounts']:
                if acc['ig_username'] == curr_u:
                    curr_acc = acc
                    break
            if not curr_acc:
                mark_task_stopped_persistent(task['id'])
                continue
            curr_pass = curr_acc['password']
            curr_u = curr_u.strip().lower()
            state_file = f"sessions\\{user_id}_{curr_u}_state.json"
            if not os.path.exists(state_file):
                with open(state_file, 'w') as f:
                    json.dump(curr_acc['storage_state'], f)
            names_file = task['names_file']
            if not os.path.exists(names_file):
                mark_task_stopped_persistent(task['id'])
                continue
            cmd = [
                "python", "msg.py",
                "--username", curr_u,
                "--password", curr_pass,
                "--thread-url", task['target_thread_url'],
                "--names", names_file,
                "--tabs", str(task['threads']),
                "--headless", "true",
                "--storage-state", state_file
            ]
            try:
                proc = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
                running_processes[proc.pid] = proc
                new_pid = proc.pid
                update_task_pid_persistent(task['id'], new_pid)
                mem_task = task.copy()
                mem_task['proc'] = proc
                mem_task['proc_list'] = [proc.pid]
                mem_task['display_pid'] = task.get('display_pid', proc.pid)
                if user_id not in users_tasks:
                    users_tasks[user_id] = []
                users_tasks[user_id].append(mem_task)
                print(f"✅ Restored message attack {task['id']} for {task['target_display']} | New PID: {new_pid}")
            except Exception as e:
                logging.error(f"❌ Failed to restore message attack {task['id']}: {e}")
                mark_task_stopped_persistent(task['id'])
    save_persistent_tasks()
    print("✅ Task restoration complete!")

async def send_resume_notification(user_id: int, task: Dict):
    ttype = task['target_type']
    tdisplay = task['target_display']
    disp = f"dm -> @{tdisplay}" if ttype == 'dm' else tdisplay
    msg = f"🔄 Attack auto resumed! New PID: {task['pid']} ({disp})\n"
    pair_list = task['pair_list']
    curr_idx = task['pair_index']
    curr_u = pair_list[curr_idx]
    for u in pair_list:
        if u == curr_u:
            msg += f"using - {u}\n"
        else:
            msg += f"cooldown - {u}\n"
    await APP.bot.send_message(chat_id=user_id, text=msg)

def get_switch_update(task: Dict) -> str:
    pair_list = task['pair_list']
    curr_idx = task['pair_index']
    curr_u = pair_list[curr_idx]
    lines = []
    for u in pair_list:
        if u == curr_u:
            lines.append(f"using - {u}")
        else:
            lines.append(f"cooldown - {u}")
    return '\n'.join(lines)

def switch_task_sync(task: Dict):
    user_id = task['user_id']

    try:
        old_proc = task.get('proc')
        old_pid = task.get('pid')
    except Exception:
        old_proc = None
        old_pid = task.get('pid')

    task['pair_index'] = (task['pair_index'] + 1) % len(task['pair_list'])
    next_u = task['pair_list'][task['pair_index']]
    data = users_data.get(user_id)
    if not data:
        logging.error(f"No users_data for user {user_id} during switch")
        return

    next_acc = next((a for a in data['accounts'] if a['ig_username'] == next_u), None)
    if not next_acc:
        logging.error(f"Can't find account {next_u} for switch")
        try:
            asyncio.run_coroutine_threadsafe(
                APP.bot.send_message(user_id, f"can't find thread Id - {next_u}"),
                LOOP
            )
        except Exception:
            pass
        return

    next_pass = next_acc['password']
    next_state_file = f"sessions\\{user_id}_{next_u}_state.json"
    if not os.path.exists(next_state_file):
        try:
            with open(next_state_file, 'w') as f:
                json.dump(next_acc.get('storage_state', {}), f)
        except Exception as e:
            logging.error(f"Failed to write state file for {next_u}: {e}")

    new_cmd = [
        "python", "msg.py",
        "--username", next_u,
        "--password", next_pass,
        "--thread-url", task['target_thread_url'],
        "--names", task['names_file'],
        "--tabs", str(task['threads']),
        "--headless", "true",
        "--storage-state", next_state_file
    ]
    try:
        new_proc = subprocess.Popen(new_cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        logging.error(f"Failed to launch new proc for switch to {next_u}: {e}")
        return

    task['proc_list'].append(new_proc.pid)
    running_processes[new_proc.pid] = new_proc
    task['cmd'] = new_cmd
    task['pid'] = new_proc.pid
    task['proc'] = new_proc
    task['last_switch_time'] = time.time()
    try:
        update_task_pid_persistent(task['id'], task['pid'])
    except Exception as e:
        logging.error(f"Failed to update persistent pid for task {task.get('id')}: {e}")

    if old_proc and old_pid != new_proc.pid:
        try:
            time.sleep(5)
            try:
                old_proc.terminate()
            except Exception:
                pass
            time.sleep(2)
            if old_proc.poll() is None:
                try:
                    old_proc.kill()
                except Exception:
                    pass
            if old_pid in task['proc_list']:
                task['proc_list'].remove(old_pid)
            if old_pid in running_processes:
                running_processes.pop(old_pid, None)
        except Exception as e:
            logging.error(f"Error while stopping old proc after switch: {e}")

    try:
        chat_id = task.get('status_chat_id', user_id)
        msg_id = task.get('status_msg_id')
        text = "Spamming...!\n" + get_switch_update(task)
        text += f"\nTo stop 🛑 type /stop {task['display_pid']} or /stop all to stop all processes."
        if msg_id:
            asyncio.run_coroutine_threadsafe(
                APP.bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text),
                LOOP
            )
        else:
            asyncio.run_coroutine_threadsafe(
                APP.bot.send_message(chat_id=chat_id, text=text),
                LOOP
            )
    except Exception as e:
        logging.error(f"Failed to update status message: {e}")

def switch_monitor():
    while True:
        time.sleep(30)
        for user_id in list(users_tasks):
            if user_id not in users_tasks:
                continue
            for task in users_tasks[user_id]:
                if task.get('type') == 'message_attack' and task['status'] == 'running' and task['proc'].poll() is None:
                    due_time = task['last_switch_time'] + task['switch_minutes'] * 60
                    if time.time() >= due_time:
                        if len(task['pair_list']) > 1:
                            switch_task_sync(task)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    if not context.args:
        await update.message.reply_text("❗ Usage: /stop <PID> or /stop all ❗")
        return
    arg = context.args[0]
    if user_id not in users_tasks or not users_tasks[user_id]:
        await update.message.reply_text("❌ No tasks running. ❌")
        return
    tasks = users_tasks[user_id]
    if arg == 'all':
        stopped_count = 0
        for task in tasks[:]:
            proc = task['proc']
            proc.terminate()
            await asyncio.sleep(3)
            if proc.poll() is None:
                proc.kill()
            pid = task.get('pid')
            if pid in running_processes:
                running_processes.pop(pid, None)
            if task.get('type') == 'message_attack' and 'names_file' in task:
                names_file = task['names_file']
                if os.path.exists(names_file):
                    os.remove(names_file)
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Task stop user={user_id} task={task['id']}")
            mark_task_stopped_persistent(task['id'])
            tasks.remove(task)
            stopped_count += 1
        await update.message.reply_text(f"🛑 Stopped all your tasks! ({stopped_count}) 🛑")
    elif arg.isdigit():
        pid_to_stop = int(arg)
        stopped_task = None

        for task in tasks[:]:
            if task.get('display_pid') == pid_to_stop:
                proc_list = task.get('proc_list', [])
                for backend_pid in proc_list:
                    backend_proc = running_processes.get(backend_pid)
                    if backend_proc:
                        try:
                            backend_proc.terminate()
                        except Exception:
                            pass
                        await asyncio.sleep(3)
                        if backend_proc.poll() is None:
                            try:
                                backend_proc.kill()
                            except Exception:
                                pass
                    else:
                        try:
                            import ctypes
                            ctypes.windll.kernel32.TerminateProcess(backend_pid, 0)
                        except:
                            pass
                for backend_pid in proc_list:
                    running_processes.pop(backend_pid, None)
                mark_task_stopped_persistent(task['id'])
                if 'names_file' in task and os.path.exists(task['names_file']):
                    os.remove(task['names_file'])
                stopped_task = task
                tasks.remove(task)
                await update.message.reply_text(f"🛑 Stopped task {pid_to_stop}!")
                break

        if not stopped_task:
            proc = running_processes.get(pid_to_stop)
            if proc:
                try: 
                    proc.terminate()
                except Exception: 
                    pass
                await asyncio.sleep(2)
                if proc.poll() is None:
                    try: 
                        proc.kill()
                    except Exception: 
                        pass
                running_processes.pop(pid_to_stop, None)
                for t in persistent_tasks:
                    if t.get('pid') == pid_to_stop:
                        mark_task_stopped_persistent(t['id'])
                        break
                await update.message.reply_text(f"🛑 Stopped task {pid_to_stop}!")
                return

        if not stopped_task:
            await update.message.reply_text("⚠️ Task not found. ⚠️")
    else:
        await update.message.reply_text("❗ Usage: /stop <PID> or /stop all ❗")
    users_tasks[user_id] = tasks

async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    if user_id not in users_tasks or not users_tasks[user_id]:
        await update.message.reply_text("❌ No ongoing tasks. ❌")
        return
    tasks = users_tasks[user_id]
    active_tasks = []
    for t in tasks:
        if t['proc'].poll() is None:
            active_tasks.append(t)
        else:
            mark_task_completed_persistent(t['id'])
    users_tasks[user_id] = active_tasks
    if not active_tasks:
        await update.message.reply_text("❌ No active tasks. ❌")
        return
    msg = "📋 Ongoing tasks 📋\n"
    for task in active_tasks:
        tdisplay = task.get('target_display', 'Unknown')
        ttype = task.get('type', 'unknown')
        preview = tdisplay[:20] + '...' if len(tdisplay) > 20 else tdisplay
        display_pid = task.get('display_pid', task['pid'])
        msg += f"PID {display_pid} — {preview} ({ttype})\n"
    await update.message.reply_text(msg)

async def usg_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("⚠️ You are not authorised to use, dm owner to gain access! @spyther ⚠️")
        return
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    ram_used = mem.used / (1024 ** 3)
    ram_total = mem.total / (1024 ** 3)
    msg = f"🖥️ CPU Usage: {cpu:.1f}%\n💾 RAM: {ram_used:.1f}GB / {ram_total:.1f}GB ({mem.percent:.1f}%)"
    await update.message.reply_text(msg)

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id in user_fetching:
        user_fetching.discard(user_id)
        await update.message.reply_text("❌ Fetching cancelled! 🚫")
    else:
        await update.message.reply_text("No active fetching to cancel. 😊")

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⚠️ you are not an admin ⚠️")
        return
    if len(context.args) != 1:
        await update.message.reply_text("❗ Usage: /add <tg_id> ❗")
        return
    try:
        tg_id = int(context.args[0])
        if any(u['id'] == tg_id for u in authorized_users):
            await update.message.reply_text("❗ User already added. ❗")
            return
        authorized_users.append({'id': tg_id, 'username': ''})
        save_authorized()
        await update.message.reply_text(f"➕ Added {tg_id} as authorized user. ➕")
    except:
        await update.message.reply_text("⚠️ Invalid tg_id. ⚠️")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⚠️ you are not an admin ⚠️")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❗ Usage: /remove <tg_id> ❗")
        return
    tg_id = int(context.args[0])
    global authorized_users
    authorized_users = [u for u in authorized_users if u['id'] != tg_id]
    save_authorized()
    await update.message.reply_text(f"➖ Removed {tg_id} from authorized users. ➖")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⚠️ you are not an admin ⚠️")
        return
    if not authorized_users:
        await update.message.reply_text("❌ No authorized users. ❌")
        return
    msg = "📜 Authorized users: 📜\n"
    for i, u in enumerate(authorized_users, 1):
        if u['id'] == OWNER_TG_ID:
            msg += f"{i}.(tg id {u['id']}) owner\n"
        elif u['username']:
            msg += f"{i}.(tg id {u['id']}) @{u['username']}\n"
        else:
            msg += f"{i}.(tg id {u['id']})\n"
    await update.message.reply_text(msg)

async def flush(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⚠️ you are not an admin ⚠️")
        return
    global users_tasks, persistent_tasks
    for uid, tasks in users_tasks.items():
        for task in tasks[:]:
            proc = task['proc']
            proc.terminate()
            await asyncio.sleep(3)
            if proc.poll() is None:
                proc.kill()
            pid = task.get('pid')
            if pid in running_processes:
                running_processes.pop(pid, None)
            if task.get('type') == 'message_attack' and 'names_file' in task:
                names_file = task['names_file']
                if os.path.exists(names_file):
                    os.remove(names_file)
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} Task stop user={uid} task={task['id']} by flush")
            mark_task_stopped_persistent(task['id'])
            tasks.remove(task)
        users_tasks[uid] = tasks
    await update.message.reply_text("🛑 All tasks globally stopped! 🛑")

def main_bot():
    from telegram.request import HTTPXRequest
    request = HTTPXRequest(connect_timeout=30, read_timeout=30, write_timeout=30)
    application = Application.builder().token(BOT_TOKEN).request(request).build()
    global APP, LOOP
    APP = application
    LOOP = asyncio.get_event_loop()
    
    # Restore tasks
    restore_tasks_on_start()
    
    # Start switch monitor
    monitor_thread = threading.Thread(target=switch_monitor, daemon=True)
    monitor_thread.start()
    
    # Post init for notifications
    async def post_init(app):
        for user_id, tasks_list in list(users_tasks.items()):
            for task in tasks_list:
                if task.get('type') == 'message_attack' and task['status'] == 'running':
                    await send_resume_notification(user_id, task)
    
    application.post_init = post_init

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("viewmyac", viewmyac))
    application.add_handler(CommandHandler("setig", setig))
    application.add_handler(CommandHandler("pair", pair_command))
    application.add_handler(CommandHandler("unpair", unpair_command))
    application.add_handler(CommandHandler("switch", switch_command))
    application.add_handler(CommandHandler("threads", threads_command))
    application.add_handler(CommandHandler("viewpref", viewpref))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("task", task_command))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("logout", logout_command))
    application.add_handler(CommandHandler("kill", cmd_kill))
    application.add_handler(CommandHandler("flush", flush))
    application.add_handler(CommandHandler("usg", usg_command))
    application.add_handler(CommandHandler("cancel", cancel_handler))

    conv_login = ConversationHandler(
        entry_points=[CommandHandler("login", login_start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_login)

    conv_plogin = ConversationHandler(
        entry_points=[CommandHandler("plogin", plogin_start)],
        states={
            PLO_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, plogin_get_username)],
            PLO_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, plogin_get_password)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_plogin)

    conv_slogin = ConversationHandler(
        entry_points=[CommandHandler("slogin", slogin_start)],
        states={
            SLOG_SESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, slogin_get_session)],
            SLOG_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, slogin_get_username)],
        },
        fallbacks=[],
    )
    application.add_handler(conv_slogin)
    
    psid_handler = ConversationHandler(
    entry_points=[CommandHandler("psid", psid_start)],
    states={
        PSID_SESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, psid_get_session)],
        PSID_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, psid_get_username)],
    },
    fallbacks=[]
)

    application.add_handler(psid_handler)

    conv_attack = ConversationHandler(
        entry_points=[CommandHandler("attack", attack_start)],
        states={
            MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mode)],
            SELECT_GC: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_gc_handler)],
            TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_target_handler)],
            MESSAGES: [
                MessageHandler(filters.Document.FileExtension("txt"), get_messages_file),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_messages),
            ],
        },
        fallbacks=[],
    )
    application.add_handler(conv_attack)

    conv_pattack = ConversationHandler(
        entry_points=[CommandHandler("pattack", pattack_start)],
        states={
            P_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_get_mode)],
            P_TARGET_DISPLAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_get_target_display)],
            P_THREAD_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, p_get_thread_url)],
            P_MESSAGES: [
                MessageHandler(filters.Document.FileExtension("txt"), p_get_messages_file),
                MessageHandler(filters.TEXT & ~filters.COMMAND, p_get_messages),
            ],
        },
        fallbacks=[],
    )
    application.add_handler(conv_pattack)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🚀 Bot starting with message attack system!")
    application.run_polling()

if __name__ == "__main__":
    main_bot()