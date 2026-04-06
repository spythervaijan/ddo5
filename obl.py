#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   NIGGA SYSTEM v8.0 – TELEGRAM + IG DUAL CONTROL · SMARTSPAM · PWSPAM     ║
║   uvloop · orjson · asyncio.Queue · ProxyRotation · Playwright · STATS     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  INSTALL  (run once)                                                         ║
║    pip install instagrapi aiohttp uvloop orjson psutil fastapi uvicorn      ║
║               edge-tts gtts requests pillow playwright                       ║
║               python-telegram-bot                                            ║
║    playwright install chromium --with-deps                                   ║
║                                                                               ║
║  RUN                                                                          ║
║    python bot.py                   ← forever, no browser, no GUI            ║
║    python bot.py --api             ← FastAPI gateway mode on :8080          ║
║    nohup python bot.py &           ← VPS background                          ║
║    screen -S bot python bot.py     ← screen/tmux session                    ║
║                                                                               ║
║  COMMANDS                                                                     ║
║  /help   /owner   /stats   /proxystats                                        ║
║  /authenticate @user   /allow @user   /remove @user   /allowed               ║
║  /login <user> <pass>   /logout <user>   /accounts                           ║
║  /loginsession <user> <sessionid>                                             ║
║  /scangcs  /listgcs  /addgc <id> [name]  /switchgc <id|name>                ║
║  /addgroup <name> <id1,id2>   /listgroups                                    ║
║  /gcaddbots                   ← auto-detect GC + add all bot accounts        ║
║  /gcadd <user1,user2,...>     ← auto-detect GC + add users                  ║
║  /raid <gc_name> [users]      ← create GC + add bots + start smartspam      ║
║  /smartspam <targets> <speed> [text]  speed: slow|medium|fast                ║
║  /pwspam <targets> <speed> [text]     playwright human-sim spam               ║
║  /multispam  <targets> <mode> [text]  mode: sequential|parallel              ║
║  /multinc    <targets> <mode> [names]                                         ║
║  /multipicspam <targets> <mode>                                               ║
║  /stopmulti <id|all>   /listmulti                                             ║
║  /spam [text]   /gcnc [name]   /godspam [text]   /picspam   /stop            ║
║  /startspam [text]   /stopspam                                                ║
║  /startgcnc [name]   /stopgcnc                                                ║
║  /startpicspam       /stoppicspam   /stopgodspam                             ║
║  /startnc [names]    /stopnc                                                  ║
║  /animevoice [male|female|robot|anime|girl] <text>                            ║
║  /search <username>   /setdelay <sec>   /setncdelay <sec>                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
TELEGRAM_BOT_TOKEN = "7676994337:AAH_CsiojGCaqJMt7ubA1s511Jm6Xy4WsXU"          #paste your bot token from @BotFather here
OWNER_TELEGRAM_ID  = 5193826370          # paste your Telegram numeric user ID here
#

import os, sys, re, time, json, threading, random, logging, uuid, asyncio, signal
import concurrent.futures, collections, math, getpass, argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# ORJSON
# ─────────────────────────────────────────────────────────────────────────────
try:
    import orjson as _json_lib
    HAS_ORJSON = True
    def _json_loads(s): return _json_lib.loads(s)
    def _json_dumps(obj, **kw) -> str:
        opts = _json_lib.OPT_INDENT_2 if kw.get("indent") else 0
        return _json_lib.dumps(obj, option=opts).decode()
except ImportError:
    import json as _json_lib  # type: ignore
    HAS_ORJSON = False
    def _json_loads(s): return _json_lib.loads(s)
    def _json_dumps(obj, **kw) -> str:
        return _json_lib.dumps(obj, **kw, ensure_ascii=False)

try:
    import psutil; HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    HAS_UVLOOP = True
except ImportError:
    HAS_UVLOOP = False

try:
    from instagrapi import Client as InstaClient
    from instagrapi.exceptions import (
        LoginRequired, TwoFactorRequired, ChallengeRequired,
        BadPassword, UserNotFound, ClientError
    )
except ImportError:
    print("❌  Install: pip install instagrapi")
    sys.exit(1)

try:
    import aiohttp; HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import edge_tts; HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    from gtts import gTTS; HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

try:
    import requests as _req; HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

try:
    from telegram import (
        Update, InlineKeyboardButton, InlineKeyboardMarkup,
        BotCommand, constants as tg_const,
    )
    from telegram.ext import (
        Application, ApplicationBuilder, CommandHandler as TGCommandHandler,
        MessageHandler as TGMessageHandler, CallbackQueryHandler,
        ContextTypes, filters as tg_filters,
    )
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False

# ─────────────────────────────────────────────────────────────────────────────
# EXECUTOR POOLS
# ─────────────────────────────────────────────────────────────────────────────
_IO_POOL = concurrent.futures.ThreadPoolExecutor(
    max_workers=256, thread_name_prefix="ig-io")
try:
    _CPU_POOL: concurrent.futures.Executor = concurrent.futures.ProcessPoolExecutor(
        max_workers=max(2, (os.cpu_count() or 2))
    )
    _cpu_test = _CPU_POOL.submit(os.getpid)
    _cpu_test.result(timeout=3)
    HAS_PROCESS_POOL = True
except Exception:
    _CPU_POOL = _IO_POOL  # type: ignore
    HAS_PROCESS_POOL = False

_POOL = _IO_POOL

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING — show only SUCCESS, ERROR, LOGIN, SEND events
# ─────────────────────────────────────────────────────────────────────────────
class _CleanFilter(logging.Filter):
    _SUPPRESS = (
        "login_required", "loginrequired", "challengerequired",
        "igsessionid", "bad request", "not json",
        "got an unexpected keyword", "connectionresetbyremotepeer",
        "private_request", "direct_v2/inbox", "pending_inbox",
        "direct_v2/threads", "i.instagram.com",
        "get /api/v1", "post /api/v1", "rupload",
        "x-ig-app-id", "x-ig-capabilities",
        "200 ok", "201 created",
        "https://i.instagram", "http://i.instagram",
        "/api/v1/direct_v2", "/api/v1/accounts",
        "csrftoken", "sessionid", "ds_user_id",
        "private api", "public api",
    )
    def filter(self, record):
        msg = record.getMessage()
        stripped = msg.strip()
        if stripped.startswith("http://") or stripped.startswith("https://"):
            return False
        return not any(s in msg.lower() for s in self._SUPPRESS)

class _ConsoleFilter(logging.Filter):
    _IMPORTANT = (
        "✅", "❌", "🔐", "🔑", "⚠️", "🚀", "🛑", "♻️", "👂", "📩",
        "✔", "⚡", "🔄", "ALIVE", "LOGIN", "SEND", "ERROR", "SUCCESS",
        "login", "reconnect", "started", "stopped", "session",
        "sent", "failed", "switched", "playwright",
    )
    def filter(self, record):
        if record.levelno >= logging.WARNING:
            return True
        msg = record.getMessage()
        return any(kw in msg for kw in self._IMPORTANT)

_fmt = "%(asctime)s | %(levelname)-8s | %(message)s"
_dfmt = "%H:%M:%S"

_file_handler    = logging.FileHandler("bot.log", encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(logging.Formatter(_fmt, _dfmt))
_file_handler.addFilter(_CleanFilter())

_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setLevel(logging.INFO)
_console_handler.setFormatter(logging.Formatter(_fmt, _dfmt))
_console_handler.addFilter(_CleanFilter())
_console_handler.addFilter(_ConsoleFilter())

logging.root.setLevel(logging.DEBUG)
logging.root.handlers.clear()
logging.root.addHandler(_file_handler)
logging.root.addHandler(_console_handler)
logging.root.addFilter(_CleanFilter())

log = logging.getLogger("NS")

for _quiet in (
    "urllib3", "requests", "httpx", "playwright", "asyncio",
    "aiohttp", "aiohttp.client", "aiohttp.access",
    "aiohttp.web", "aiohttp.server", "aiohttp.connector",
    "instagrapi", "instagrapi.mixins", "instagrapi.utils",
    "instagrapi.mixins.private", "instagrapi.mixins.public",
    "instagrapi.mixins.direct", "instagrapi.mixins.account",
    "instagrapi.mixins.auth", "instagrapi.mixins.challenge",
    "uvicorn", "uvicorn.access", "uvicorn.error",
    "fastapi", "starlette", "multipart",
    "PIL", "chardet",
):
    _lg = logging.getLogger(_quiet)
    _lg.setLevel(logging.CRITICAL)
    _lg.propagate = False

BOT_START = datetime.now()
_URL_RE   = re.compile(r'https?://\S+', re.IGNORECASE)

def _clean_exc(e: Exception) -> str:
    msg = str(e)
    msg = _URL_RE.sub("[url]", msg)
    return msg[:120]

# ─────────────────────────────────────────────────────────────────────────────
# DEVICE PROFILES
# ─────────────────────────────────────────────────────────────────────────────
_DEVICE_PROFILES = [
    {
        "user_agent": "Instagram 269.0.0.18.75 Android (30/11; 420dpi; 1080x2340; samsung; SM-G998B; p3s; exynos2100; en_US; 269.0.0.18.75)",
        "device_id":  "android-{hex}",
        "android_version": 30,
        "android_release": "11.0.0",
        "model": "SM-G998B",
    },
    {
        "user_agent": "Instagram 269.0.0.18.75 Android (29/10; 440dpi; 1080x2400; xiaomi; Mi 11; venus; qcom; en_US; 269.0.0.18.75)",
        "device_id":  "android-{hex}",
        "android_version": 29,
        "android_release": "10.0.0",
        "model": "Mi 11",
    },
    {
        "user_agent": "Instagram 269.0.0.18.75 Android (31/12; 480dpi; 1080x2400; OnePlus; OnePlus 9; lemonade; qcom; en_US; 269.0.0.18.75)",
        "device_id":  "android-{hex}",
        "android_version": 31,
        "android_release": "12.0.0",
        "model": "OnePlus 9",
    },
    {
        "user_agent": "Instagram 269.0.0.18.75 Android (30/11; 420dpi; 1080x2280; samsung; SM-A525F; a52q; qcom; en_US; 269.0.0.18.75)",
        "device_id":  "android-{hex}",
        "android_version": 30,
        "android_release": "11.0.0",
        "model": "SM-A525F",
    },
    {
        "user_agent": "Instagram 269.0.0.18.75 Android (32/12; 560dpi; 1440x3200; samsung; SM-S908B; b0q; exynos2200; en_US; 269.0.0.18.75)",
        "device_id":  "android-{hex}",
        "android_version": 32,
        "android_release": "12.0.0",
        "model": "SM-S908B",
    },
    {
        "user_agent": "Instagram 269.0.0.18.75 Android (29/10; 420dpi; 1080x2280; realme; RMX3085; RMX3085; helio; en_US; 269.0.0.18.75)",
        "device_id":  "android-{hex}",
        "android_version": 29,
        "android_release": "10.0.0",
        "model": "RMX3085",
    },
]

def _random_device() -> dict:
    p = random.choice(_DEVICE_PROFILES)
    return {
        "user_agent": p["user_agent"],
        "device_id":  p["device_id"].format(hex=uuid.uuid4().hex[:16]),
        "android_version": p["android_version"],
        "android_release": p["android_release"],
        "model": p["model"],
    }

# ─────────────────────────────────────────────────────────────────────────────
# PROXY ROTATOR
# ─────────────────────────────────────────────────────────────────────────────
class ProxyRotator:
    _SOFT_FAIL_THRESHOLD = 5
    _HARD_FAIL_THRESHOLD = 15
    _COOLDOWN_SEC        = 120

    def __init__(self, proxy_list: List[str]):
        self._lock       = threading.Lock()
        self.proxy_list  = list(proxy_list)
        self._failed: Dict[str, int]     = {}
        self._success: Dict[str, int]    = {}
        self._cooldown: Dict[str, float] = {}
        for p in proxy_list:
            self._failed[p]  = 0
            self._success[p] = 0

    @classmethod
    def from_file(cls, path: str = "proxies.txt") -> "ProxyRotator":
        proxies: List[str] = []
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        proxies.append(line)
        if proxies:
            log.info(f"🌐 Loaded {len(proxies)} proxies from {path}")
        else:
            log.warning(f"⚠️  No proxies found in {path} — running direct")
        return cls(proxies)

    def get_proxy(self, exclude: Optional[str] = None) -> Optional[str]:
        with self._lock:
            now = time.time()
            available = [p for p in self.proxy_list
                         if self._cooldown.get(p, 0) <= now and p != exclude]
            if not available:
                if self.proxy_list:
                    self._cooldown.clear()
                    log.warning("♻️  All proxies on cooldown — resetting")
                    available = [p for p in self.proxy_list if p != exclude] or self.proxy_list
                else:
                    return None
            return min(available, key=lambda p: self._failed[p] / max(1, self._success[p]))

    def mark_success(self, proxy: str):
        with self._lock:
            self._success[proxy] = self._success.get(proxy, 0) + 1
            self._failed[proxy]  = max(0, self._failed.get(proxy, 0) - 1)
            self._cooldown.pop(proxy, None)

    def mark_failure(self, proxy: str):
        with self._lock:
            self._failed[proxy] = self._failed.get(proxy, 0) + 1
            failures = self._failed[proxy]
            if failures >= self._SOFT_FAIL_THRESHOLD:
                cooldown = min(
                    self._COOLDOWN_SEC * (2 ** (failures - self._SOFT_FAIL_THRESHOLD)),
                    3600
                )
                self._cooldown[proxy] = time.time() + cooldown
            if failures >= self._HARD_FAIL_THRESHOLD and proxy in self.proxy_list:
                self.proxy_list.remove(proxy)
                log.warning(f"🗑  Removed dead proxy {proxy}")

    async def health_check(self, proxy: str, timeout: float = 5.0) -> bool:
        if not HAS_AIOHTTP:
            return True
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as s:
                async with s.get("https://httpbin.org/ip", proxy=proxy) as r:
                    if r.status == 200:
                        self.mark_success(proxy)
                        return True
                    self.mark_failure(proxy)
                    return False
        except Exception:
            self.mark_failure(proxy)
            return False

    def get_stats(self) -> dict:
        with self._lock:
            return {
                "total":       len(self.proxy_list),
                "on_cooldown": sum(1 for p, t in self._cooldown.items() if t > time.time()),
                "by_proxy":    {
                    p: {"ok": self._success.get(p, 0), "fail": self._failed.get(p, 0)}
                    for p in self.proxy_list[:10]
                },
            }

    def __len__(self):
        return len(self.proxy_list)

# ─────────────────────────────────────────────────────────────────────────────
# ACCOUNT MANAGER — central pool with load balancing + failover
# ─────────────────────────────────────────────────────────────────────────────
class AccountManager:
    """Round-robin account pool with error tracking and cooldown."""

    def __init__(self):
        self._lock       = threading.Lock()
        self._accounts:  List["IGClient"] = []
        self._rr_idx     = 0
        self._errors:    Dict[str, int]   = {}
        self._cooldown:  Dict[str, float] = {}
        self._busy:      Dict[str, bool]  = {}

    def register(self, cl: "IGClient"):
        with self._lock:
            if cl not in self._accounts:
                self._accounts.append(cl)
                self._errors[cl.username]   = 0
                self._busy[cl.username]     = False

    def unregister(self, cl: "IGClient"):
        with self._lock:
            try: self._accounts.remove(cl)
            except ValueError: pass

    def get_next(self, exclude: Optional[str] = None) -> Optional["IGClient"]:
        with self._lock:
            now = time.time()
            available = [
                a for a in self._accounts
                if self._cooldown.get(a.username, 0) <= now
                and a.username != exclude
            ]
            if not available:
                available = [a for a in self._accounts if a.username != exclude]
            if not available:
                return None
            # round-robin weighted by error count
            best = min(available, key=lambda a: self._errors.get(a.username, 0))
            self._rr_idx = (self._rr_idx + 1) % max(1, len(available))
            return best

    def mark_error(self, username: str):
        with self._lock:
            self._errors[username] = self._errors.get(username, 0) + 1
            if self._errors[username] >= 5:
                cooldown_sec = min(300, 60 * self._errors[username])
                self._cooldown[username] = time.time() + cooldown_sec
                log.warning(f"⚠️  @{username} on cooldown {cooldown_sec}s (errors={self._errors[username]})")

    def mark_success(self, username: str):
        with self._lock:
            prev = self._errors.get(username, 0)
            self._errors[username] = max(0, prev - 1)
            self._cooldown.pop(username, None)

    def get_error_rate(self, username: str, total: int) -> float:
        if total == 0:
            return 0.0
        return self._errors.get(username, 0) / total

    def list_active(self) -> List["IGClient"]:
        with self._lock:
            return list(self._accounts)

    def __len__(self):
        with self._lock:
            return len(self._accounts)

ACCOUNT_MANAGER = AccountManager()

# ─────────────────────────────────────────────────────────────────────────────
# PLAYWRIGHT — fully headless, persistent browser, background exec
# ─────────────────────────────────────────────────────────────────────────────
class PlaywrightEngine:
    """
    Headless Playwright engine. One browser shared globally.
    One context per account, multiple pages (tabs) per context.
    Runs headless=True, never opens a browser window.
    """
    _MAX_CONTEXTS = 8
    _sem: Optional[asyncio.Semaphore] = None

    def __init__(self):
        self._pw       = None
        self._browser  = None
        self._contexts: Dict[str, object] = {}
        self._pages:    Dict[str, Dict[str, object]] = {}  # username -> {tid: page}
        self._ready    = False
        self._lock     = asyncio.Lock()

    async def start(self):
        if not HAS_PLAYWRIGHT:
            return
        try:
            pw = await async_playwright().__aenter__()
            self._pw = pw
            self._browser = await pw.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-setuid-sandbox",
                    "--no-zygote",
                    "--single-process",
                ],
            )
            if PlaywrightEngine._sem is None:
                PlaywrightEngine._sem = asyncio.Semaphore(self._MAX_CONTEXTS)
            self._ready = True
            log.info("🎭 Playwright headless browser ready")
        except Exception as e:
            log.warning(f"Playwright init failed: {e}")
            self._ready = False

    async def _get_or_create_context(self, username: str, sessionid: str) -> Optional[object]:
        if not self._ready or not self._browser:
            return None
        if username not in self._contexts:
            ctx = await self._browser.new_context(
                viewport={"width": 375, "height": 812},
                user_agent=_random_device()["user_agent"].replace(
                    "Instagram", "Mozilla/5.0 (Linux; Android 11; "
                ).replace(" Android ", " ; rv=90.0) Gecko/90.0 Firefox/90.0 Instagram"),
                locale="en-US",
                timezone_id="America/New_York",
            )
            await ctx.add_cookies([{
                "name":     "sessionid",
                "value":    sessionid,
                "domain":   ".instagram.com",
                "path":     "/",
                "secure":   True,
                "httpOnly": True,
                "sameSite": "Lax",
            }])
            self._contexts[username] = ctx
            self._pages[username]    = {}
        return self._contexts[username]

    async def _get_or_create_page(self, username: str, tid: str, sessionid: str) -> Optional[object]:
        ctx = await self._get_or_create_context(username, sessionid)
        if not ctx:
            return None
        pages = self._pages.get(username, {})
        if tid in pages:
            page = pages[tid]
            try:
                if not page.is_closed():
                    return page
            except Exception:
                pass
        page = await ctx.new_page()
        self._pages[username][tid] = page
        return page

    async def send_message_human(self, username: str, tid: str,
                                  text: str, sessionid: str,
                                  typing_delay_ms: int = 40) -> bool:
        """
        Send a message via Playwright with human-like typing simulation.
        """
        if not self._ready or not HAS_PLAYWRIGHT:
            return False
        sem = PlaywrightEngine._sem
        if sem is None:
            return False

        async with sem:
            for attempt in range(3):
                try:
                    page = await self._get_or_create_page(username, tid, sessionid)
                    if not page:
                        return False

                    url = f"https://www.instagram.com/direct/t/{tid}/"

                    if page.url != url or attempt > 0:
                        await page.goto(url, wait_until="networkidle", timeout=30000)
                        await asyncio.sleep(random.uniform(0.5, 1.5))

                    # Random scroll before typing
                    await page.mouse.wheel(0, random.randint(-100, 100))
                    await asyncio.sleep(random.uniform(0.2, 0.5))

                    # Click message input
                    box = page.locator("textarea, [contenteditable='true'], [aria-label='Message']").first
                    await box.click()
                    await asyncio.sleep(random.uniform(0.2, 0.6))

                    # Type each character with randomized delay
                    for char in text:
                        await page.keyboard.type(char, delay=random.randint(20, typing_delay_ms))

                    await asyncio.sleep(random.uniform(0.3, 1.0))
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(0.4)

                    log.info(f"✔ sent via playwright @{username} → {tid[:12]}…")
                    return True
                except Exception as e:
                    log.debug(f"Playwright send attempt {attempt+1} @{username}: {e}")
                    # Recreate page on failure
                    try:
                        if username in self._pages and tid in self._pages[username]:
                            await self._pages[username][tid].close()
                            del self._pages[username][tid]
                    except Exception:
                        pass
                    if attempt == 2:
                        log.info(f"❌ failed playwright @{username} after 3 tries")
                        return False
                    await asyncio.sleep(1.0)
        return False

    async def close_account(self, username: str):
        for page in list(self._pages.get(username, {}).values()):
            try:
                await page.close()
            except Exception:
                pass
        self._pages.pop(username, None)
        ctx = self._contexts.pop(username, None)
        if ctx:
            try:
                await ctx.close()
            except Exception:
                pass

    async def stop(self):
        for uname in list(self._contexts.keys()):
            await self.close_account(uname)
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
        if self._pw:
            try:
                await self._pw.__aexit__(None, None, None)
            except Exception:
                pass
        self._ready = False

_PW_ENGINE = PlaywrightEngine()

# ─────────────────────────────────────────────────────────────────────────────
# PLAYWRIGHT SPAM ENGINE V2 — multi-GC multi-tab, page reuse, 0.2-0.3s delay
# ─────────────────────────────────────────────────────────────────────────────
class PlaywrightSpamEngine:
    """
    High-speed Playwright spam engine — V2 multi-GC edition.
    - headless=True, no browser window ever opens.
    - Blocks images/media/fonts/stylesheets for maximum throughput.
    - Accepts a list of GC URLs — opens one page (tab) per GC.
    - Pages are reused across sends; only recreated on error.
    - Delay: 0.2-0.3s per send cycle across all GC tabs.
    - Stopped instantly via asyncio.Event.
    """

    DELAY_MIN   = 0.2
    DELAY_MAX   = 0.3

    def __init__(self, engine_id: int, sid: str, urls: list):
        self.engine_id = engine_id
        self.sid       = sid
        # urls can be a list (multi-GC) or a single string (backwards-compat)
        self.urls      = urls if isinstance(urls, list) else [urls]
        self._user_data = f"./pw_engine_session_{engine_id}"

    @staticmethod
    async def _block_media(route):
        if route.request.resource_type in ("image", "media", "font", "stylesheet"):
            await route.abort()
        else:
            await route.continue_()

    async def run(self, text: str, stop_event: asyncio.Event,
                  eng: "Engine", on_send=None):
        """
        Multi-GC loop. Opens one page per URL, then cycles through all pages
        sending messages until stop_event is set.
        """
        if not HAS_PLAYWRIGHT:
            log.warning(f"[E-{self.engine_id}] Playwright not installed")
            return

        while not stop_event.is_set():
            async with async_playwright() as pw:
                browser = None
                try:
                    browser = await pw.chromium.launch_persistent_context(
                        self._user_data,
                        headless=True,
                        args=[
                            "--no-sandbox", "--disable-gpu",
                            "--disable-dev-shm-usage",
                            "--disable-setuid-sandbox",
                            "--no-zygote",
                        ],
                    )
                    await browser.add_cookies([{
                        "name": "sessionid", "value": self.sid,
                        "domain": ".instagram.com", "path": "/",
                        "secure": True, "httpOnly": True, "sameSite": "Lax",
                    }])

                    # Open one tab per GC URL
                    pages = []
                    msg_boxes = []
                    for url in self.urls:
                        if stop_event.is_set():
                            break
                        try:
                            page = await browser.new_page()
                            await page.route("**/*", self._block_media)
                            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                            box = page.locator(
                                'div[role="textbox"], div[aria-label="Message"]'
                            ).first
                            pages.append(page)
                            msg_boxes.append(box)
                        except Exception as e:
                            log.debug(f"[E-{self.engine_id}] tab open fail: {_clean_exc(e)}")

                    if not pages:
                        await asyncio.sleep(2.0)
                        continue

                    count = 0
                    while not stop_event.is_set():
                        for idx, (page, box) in enumerate(zip(pages, msg_boxes)):
                            if stop_event.is_set():
                                break
                            try:
                                await box.focus()
                                await box.fill(_vary_message(text))
                                await page.keyboard.press("Enter")
                                count += 1
                                eng.inc("msgs")
                                METRICS.playwright_sends += 1
                                if on_send:
                                    try:
                                        await on_send(self.engine_id, count)
                                    except Exception:
                                        pass
                            except Exception as e:
                                # Recreate the page if the tab died
                                try:
                                    url = self.urls[idx]
                                    page = await browser.new_page()
                                    await page.route("**/*", self._block_media)
                                    await page.goto(url, wait_until="domcontentloaded",
                                                    timeout=60000)
                                    box = page.locator(
                                        'div[role="textbox"], div[aria-label="Message"]'
                                    ).first
                                    pages[idx]    = page
                                    msg_boxes[idx] = box
                                except Exception:
                                    pass

                        delay = random.uniform(self.DELAY_MIN, self.DELAY_MAX)
                        await asyncio.sleep(delay)

                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.debug(f"[E-{self.engine_id}] restart: {_clean_exc(e)}")
                    await asyncio.sleep(1.0)
                finally:
                    if browser:
                        try:
                            await browser.close()
                        except Exception:
                            pass
                    # Wipe session dir so next restart is clean
                    if not stop_event.is_set():
                        try:
                            import shutil as _sh
                            _sh.rmtree(self._user_data, ignore_errors=True)
                        except Exception:
                            pass


# Active /pwgo tasks: key="pwgo:{user_key}" -> (stop_event, [asyncio.Task, ...])
_ACTIVE_PWGO: Dict[str, Tuple[asyncio.Event, List[asyncio.Task]]] = {}
_PWGO_LOCK = asyncio.Lock()    # protects _ACTIVE_PWGO


# ─────────────────────────────────────────────────────────────────────────────
# TRUE ULTRA ENGINE — PlaywrightSpamEngine V3 (UPGRADE)
# Features: 3-5 tabs per GC, 0.01s zero-jitter, burst=3 msgs/cycle,
#           multi-account round-robin, auto speed adjust by fail rate
# ─────────────────────────────────────────────────────────────────────────────
class UltraPlaywrightSpamEngine:
    """
    TRUE ULTRA ENGINE — V3.1 (STABLE ACCOUNT ASSIGNMENT)
    - TABS_PER_GC: 3–5 parallel tabs per GC URL (saturates IG endpoint).
    - BURST_SIZE: sends 3 messages per tab per cycle (zero delay between bursts).
    - DELAY: exactly 0.01s between full cycles — true zero-jitter.
    - STABLE ACCOUNT MAPPING: one account per GC URL, all tabs for same GC share
      the same session → stable behavior, less detection, smoother speed.
    - MULTI-GC DISTRIBUTION: accounts distributed across GCs, not across tabs.
    - FAILOVER: if account fails for a GC, switches to next account for that GC.
    - Auto speed adjust: if fail_rate > FAIL_THRESHOLD → slow to 0.1s; else 0.01s.
    """

    DELAY_NORMAL   = 0.01
    DELAY_SLOWDOWN = 0.10
    BURST_SIZE     = 3
    TABS_PER_GC    = 4       # default tabs per GC URL
    FAIL_THRESHOLD = 0.30    # if 30%+ fails → auto-slowdown
    FAILOVER_THRESHOLD = 3   # consecutive fails before switching account for a GC

    def __init__(self, engine_id: int, urls: list,
                 tabs_per_gc: int = 4, burst: int = 3):
        self.engine_id   = engine_id
        self.urls        = urls if isinstance(urls, list) else [urls]
        self.tabs_per_gc = max(1, min(5, tabs_per_gc))
        self.burst       = max(1, burst)
        self._user_data  = f"./pw_ultra_session_{engine_id}"
        self._sends      = 0
        self._fails      = 0
        # GC → account mapping (populated in run())
        self._gc_account_map: Dict[str, int] = {}  # url → account_index
        self._gc_fail_count: Dict[str, int]  = {}  # url → consecutive fail count

    @staticmethod
    async def _block_media(route):
        if route.request.resource_type in ("image", "media", "font", "stylesheet"):
            await route.abort()
        else:
            await route.continue_()

    def _current_delay(self) -> float:
        total = self._sends + self._fails
        if total < 10:
            return self.DELAY_NORMAL
        fail_rate = self._fails / total
        if fail_rate > self.FAIL_THRESHOLD:
            return self.DELAY_SLOWDOWN
        return self.DELAY_NORMAL

    def _build_gc_account_map(self) -> Dict[str, "IGClient"]:
        """
        Stable GC → account mapping.
        Each GC URL is assigned exactly one account.
        Accounts distributed across GCs (not across tabs).
        All tabs for the same GC share the same account session.
        """
        clients = ACCOUNT_MANAGER.list_active()
        if not clients:
            return {}
        gc_map: Dict[str, "IGClient"] = {}
        for i, url in enumerate(self.urls):
            # Initialize account index if not already tracked
            acct_idx = self._gc_account_map.get(url, i % len(clients))
            self._gc_account_map[url] = acct_idx
            gc_map[url] = clients[acct_idx % len(clients)]
        return gc_map

    def _failover_account(self, url: str) -> Optional[str]:
        """
        On repeated failure for a GC URL, switch to the next available account.
        Returns the new session ID, or None if no accounts available.
        """
        clients = ACCOUNT_MANAGER.list_active()
        if not clients:
            return None
        current_idx = self._gc_account_map.get(url, 0)
        next_idx = (current_idx + 1) % len(clients)
        self._gc_account_map[url] = next_idx
        self._gc_fail_count[url]  = 0
        new_cl = clients[next_idx]
        log.info(f"[ULTRA-{self.engine_id}] Failover GC {url[-20:]} → @{new_cl.username}")
        return new_cl._sessionid or ""

    async def run(self, text: str, stop_event: asyncio.Event,
                  eng: "Engine", on_send=None):
        """
        Ultra engine main loop — STABLE ACCOUNT ASSIGNMENT.
        One account per GC. All tabs on same GC use same session.
        Accounts distributed across GCs, not across tabs.
        Failover: switch account per GC after FAILOVER_THRESHOLD consecutive fails.
        """
        if not HAS_PLAYWRIGHT:
            log.warning(f"[ULTRA-{self.engine_id}] Playwright not installed")
            return

        while not stop_event.is_set():
            async with async_playwright() as pw:
                browser = None
                try:
                    browser = await pw.chromium.launch_persistent_context(
                        self._user_data,
                        headless=True,
                        args=[
                            "--no-sandbox", "--disable-gpu",
                            "--disable-dev-shm-usage",
                            "--disable-setuid-sandbox",
                            "--no-zygote",
                            "--disable-background-networking",
                            "--disable-extensions",
                            "--disable-sync",
                            "--disable-translate",
                        ],
                    )

                    # Build stable GC → account map
                    gc_account_map = self._build_gc_account_map()

                    # Open tabs: tabs_per_gc tabs per URL, ALL tabs of a GC share same session
                    # pages: list of (page, box, url, gc_sid)
                    pages: List[Tuple] = []
                    for url in self.urls:
                        if stop_event.is_set():
                            break
                        cl  = gc_account_map.get(url)
                        sid = cl._sessionid if cl else ""
                        if not sid:
                            continue
                        for tab_num in range(self.tabs_per_gc):
                            if stop_event.is_set():
                                break
                            try:
                                page = await browser.new_page()
                                await page.route("**/*", self._block_media)
                                # All tabs for this GC use the same session
                                await page.context.add_cookies([{
                                    "name": "sessionid", "value": sid,
                                    "domain": ".instagram.com", "path": "/",
                                    "secure": True, "httpOnly": True, "sameSite": "Lax",
                                }])
                                await page.goto(url, wait_until="domcontentloaded",
                                                timeout=60000)
                                box = page.locator(
                                    'div[role="textbox"], div[aria-label="Message"]'
                                ).first
                                pages.append((page, box, url, sid))
                            except Exception as e:
                                log.debug(f"[ULTRA-{self.engine_id}] tab open fail "
                                          f"({url[-20:]}, tab {tab_num}): {_clean_exc(e)}")

                    if not pages:
                        await asyncio.sleep(2.0)
                        continue

                    log.info(f"[ULTRA-{self.engine_id}] {len(pages)} tabs ready "
                             f"({len(self.urls)} GCs x {self.tabs_per_gc} tabs) "
                             f"| burst={self.burst} | stable-account-map")

                    count = 0
                    while not stop_event.is_set():
                        cycle_tasks = []
                        for idx, (page, box, url, gc_sid) in enumerate(pages):
                            if stop_event.is_set():
                                break

                            async def _tab_burst(page=page, box=box, url=url,
                                                  idx=idx, gc_sid=gc_sid):
                                """Send burst_size messages on one tab (stable account)."""
                                for b in range(self.burst):
                                    if stop_event.is_set():
                                        return
                                    try:
                                        msg = _vary_message(text)
                                        await box.focus()
                                        await box.fill(msg)
                                        await page.keyboard.press("Enter")
                                        self._sends += 1
                                        self._gc_fail_count[url] = 0
                                        eng.inc("msgs")
                                        METRICS.playwright_sends += 1
                                        if on_send:
                                            try:
                                                await on_send(self.engine_id, self._sends)
                                            except Exception:
                                                pass
                                    except Exception as e:
                                        self._fails += 1
                                        self._gc_fail_count[url] = \
                                            self._gc_fail_count.get(url, 0) + 1
                                        # Failover: switch account for this GC if too many fails
                                        new_sid = gc_sid
                                        if self._gc_fail_count.get(url, 0) >= self.FAILOVER_THRESHOLD:
                                            new_sid = self._failover_account(url) or gc_sid
                                        # Recreate tab with (possibly new) session
                                        try:
                                            new_page = await browser.new_page()
                                            await new_page.route("**/*", self._block_media)
                                            await new_page.context.add_cookies([{
                                                "name": "sessionid", "value": new_sid,
                                                "domain": ".instagram.com", "path": "/",
                                                "secure": True, "httpOnly": True,
                                                "sameSite": "Lax",
                                            }])
                                            await new_page.goto(url,
                                                                wait_until="domcontentloaded",
                                                                timeout=60000)
                                            new_box = new_page.locator(
                                                'div[role="textbox"], div[aria-label="Message"]'
                                            ).first
                                            pages[idx] = (new_page, new_box, url, new_sid)
                                        except Exception:
                                            pass
                                        break

                            cycle_tasks.append(_tab_burst())

                        if cycle_tasks:
                            await asyncio.gather(*cycle_tasks, return_exceptions=True)

                        count += 1
                        await asyncio.sleep(self._current_delay())

                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.debug(f"[ULTRA-{self.engine_id}] restart: {_clean_exc(e)}")
                    await asyncio.sleep(1.0)
                finally:
                    if browser:
                        try:
                            await browser.close()
                        except Exception:
                            pass
                    if not stop_event.is_set():
                        try:
                            import shutil as _sh
                            _sh.rmtree(self._user_data, ignore_errors=True)
                        except Exception:
                            pass


# ─────────────────────────────────────────────────────────────────────────────
# OBLIVION SPAM ENGINE — based on Oblivion Titan V44 script
# Fast Playwright spam: target injection, 160-line gap messages, DOM soft-purge,
# name-lock engine, multi-session support. Zero rate-limit approach.
# ─────────────────────────────────────────────────────────────────────────────

_OBLIVION_MESSAGES = [
    "[{target}] 𝟗-𝟐-𝟏𝟏 𝐓𝐔𝐌𝐇𝐀𝐑𝐈 माँ 𝐊𝐎 𝐏𝐑𝐄𝐆𝐍𝐀𝐍𝐓 𝐊𝐀𝐑 𝐃𝐀𝐋𝐀",
    "[{target}] 𝐓𝐔𝐌𝐇𝐀𝐑𝐈 𝐌𝐀𝐀 𝐊𝐎 𝐂𝐇𝐎𝐃 𝐃𝐀𝐀𝐋𝐄𝐍𝐆𝐄 //~ 🔥",
    "[{target}] 𝐓𝐔𝐌𝐇𝐀𝐑𝐈 𝐌𝐌𝐘 𝐊𝐎 𝐊𝐈𝐍𝐍𝐄𝐑 𝐆𝐑𝐎𝐔𝐏 𝐖𝐀𝐋𝐄 𝐂𝐇𝐎𝐃𝐄𝐍𝐆𝐄 𝐘𝐀𝐀𝐃 𝐑𝐀𝐊𝐇𝐍𝐀 😝🤲🏻",
    "[{target}] 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐄 𝐁𝐇𝐎𝐒𝐃𝐄 𝐌𝐀𝐈 𝐈𝐓𝐍𝐄 𝐂𝐇𝐀𝐍𝐓𝐄 𝐌𝐀𝐑𝐔𝐍𝐆𝐀 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐀 𝐁𝐇𝐎𝐒𝐃𝐀 𝐅𝐀𝐀𝐓 𝐉𝐘𝐆𝐀 🤪🐒🤣🔥",
    "[{target}] 𝐇𝐀𝐓 𝐌𝐀𝐃𝐑𝐂𝐇𝐎𝐃 𝐌𝐀𝐑𝐄 𝐒𝐄 𝐃𝐇𝐔𝐑 𝐕𝐀𝐑𝐍𝐀 𝐓𝐀𝐑𝐈 𝐌𝐔𝐌𝐌𝐘 𝐗𝐇𝐎𝐃𝐔𝐍𝐆𝐀𝐀𝐀 🤣🔥",
    "⚡ [{target}] 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐆𝐀𝐍𝐃 𝐌𝐀𝐑𝐃𝐔𝐍𝐆𝐀 ⚡",
    "🔱 [{target}] 𝐎𝐁𝐋𝐈𝐕𝐈𝐎𝐍 𝐓𝐈𝐓𝐀𝐍 𝐖𝐀𝐒 𝐇𝐄𝐑𝐄 — 𝐓𝐄𝐑𝐈 𝐆𝐂 𝐎𝐖𝐍𝐄𝐃 🔱",
    "💀 [{target}] 𝐍𝐈𝐆𝐆𝐀 𝐒𝐘𝐒𝐓𝐄𝐌 × 𝐎𝐁𝐋𝐈𝐕𝐈𝐎𝐍 𝐓𝐈𝐓𝐀𝐍 — 𝐓𝐔𝐌 𝐇𝐀𝐑 𝐆𝐀𝐘𝐄 💀",
]

def _oblivion_payload(target: str) -> str:
    """
    Generates a gap-message payload with target name injection.
    Uses 160 blank lines between copies to flood the chat viewport.
    """
    rand_id   = random.randint(1000, 9999)
    gap_lines = "\n" * 160
    core      = random.choice(_OBLIVION_MESSAGES).replace("{target}", target)
    return f"{core}{gap_lines}{core}{gap_lines}{core}\n🔱 NIGGA SYSTEM × OBLIVION [{rand_id}] 🔱"


class OblivionSpamEngine:
    """
    OBLIVION SPAM ENGINE — fast Playwright spam, no rate-limit approach.
    Based on Oblivion Titan V44 script logic.

    Features:
    - Target name injection ({target} in all messages)
    - 160-line gap payload (floods chat viewport)
    - DOM soft-purge: page.reload() every 30 messages (keeps tab fresh)
    - Locker engine: engine_id==1 does name-lock every 19 messages
    - Multi-session: each engine uses its own session ID
    - Fast: configurable DELAY (default 0.01s), no rate-limit buildup
    - Stop via asyncio.Event
    """

    DELAY             = 0.01    # seconds between messages — near-zero
    SOFT_PURGE_EVERY  = 30      # reload DOM every N messages
    LOCK_EVERY        = 19      # locker engine changes GC name every N messages

    def __init__(self, engine_id: int, sid: str, url: str,
                 target: str, gc_name: str, delay: float = 0.01,
                 custom_text: Optional[str] = None):
        self.engine_id   = engine_id
        self.sid         = sid
        self.url         = url
        self.target      = target
        self.gc_name     = gc_name
        self.delay       = max(0.001, delay)
        self.custom_text = custom_text   # if set, overrides _OBLIVION_MESSAGES
        self._user_data  = f"./oblivion_session_{engine_id}"
        self.is_locker   = (engine_id == 1)   # first engine is the name-locker

    def _build_payload(self) -> str:
        """Build message payload. Uses custom_text if set, else Oblivion 160-gap messages."""
        rand_id   = random.randint(1000, 9999)
        gap_lines = "\n" * 160
        if self.custom_text:
            core = self.custom_text.replace("{target}", self.target)
        else:
            core = random.choice(_OBLIVION_MESSAGES).replace("{target}", self.target)
        return f"{core}{gap_lines}{core}{gap_lines}{core}\n🔱 NIGGA SYSTEM × OBLIVION [{rand_id}] 🔱"

    @staticmethod
    async def _block_media(route):
        if route.request.resource_type in ("image", "media", "font", "stylesheet"):
            await route.abort()
        else:
            await route.continue_()

    async def _force_name_lock(self, page, gc_name: str):
        """Reset GC name to gc_name — locker engine only."""
        try:
            gear = page.locator('svg[aria-label="Conversation information"]')
            await gear.click(timeout=5000)
            await asyncio.sleep(0.3)
            change_btn   = page.locator('div[aria-label="Change group name"][role="button"]')
            group_input  = page.locator('input[aria-label="Group name"][name="change-group-name"]')
            save_btn     = page.locator('div[role="button"]:has-text("Save")')
            await change_btn.click(timeout=5000)
            await group_input.fill(gc_name, timeout=5000)
            if await save_btn.is_enabled(timeout=3000):
                await save_btn.click(timeout=5000)
                log.info(f"[OBV-{self.engine_id}] 🔒 Name locked: {gc_name}")
            await gear.click(timeout=5000)
        except Exception as e:
            log.debug(f"[OBV-{self.engine_id}] name-lock fail: {_clean_exc(e)}")
            try:
                await page.reload(wait_until="domcontentloaded", timeout=30000)
            except Exception:
                pass

    async def run(self, stop_event: asyncio.Event, eng: Optional["Engine"] = None):
        """
        Main Oblivion engine loop.
        Sends gap-messages with target injection at near-zero delay.
        Engine 1 additionally locks the GC name periodically.
        """
        if not HAS_PLAYWRIGHT:
            log.warning(f"[OBV-{self.engine_id}] Playwright not installed")
            return

        while not stop_event.is_set():
            async with async_playwright() as pw:
                browser = None
                try:
                    browser = await pw.chromium.launch_persistent_context(
                        self._user_data,
                        headless=True,
                        args=[
                            "--no-sandbox", "--disable-gpu",
                            "--disable-dev-shm-usage",
                            "--disable-setuid-sandbox",
                            "--no-zygote",
                        ],
                    )
                    await browser.add_cookies([{
                        "name": "sessionid", "value": self.sid,
                        "domain": ".instagram.com", "path": "/",
                        "secure": True, "httpOnly": True, "sameSite": "Lax",
                    }])
                    page = await browser.new_page()
                    await page.route("**/*", self._block_media)
                    await page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                    box = page.locator('div[role="textbox"], div[aria-label="Message"]').first

                    msg_count = 0
                    while not stop_event.is_set():
                        # DOM soft-purge every SOFT_PURGE_EVERY messages
                        if msg_count > 0 and msg_count % self.SOFT_PURGE_EVERY == 0:
                            log.debug(f"[OBV-{self.engine_id}] soft-purge at {msg_count}")
                            await page.reload(wait_until="domcontentloaded", timeout=30000)
                            box = page.locator(
                                'div[role="textbox"], div[aria-label="Message"]'
                            ).first
                            await box.focus()

                        # Locker engine: reset GC name every LOCK_EVERY messages
                        if self.is_locker and msg_count > 0 and msg_count % self.LOCK_EVERY == 0:
                            await self._force_name_lock(page, self.gc_name)
                            box = page.locator(
                                'div[role="textbox"], div[aria-label="Message"]'
                            ).first

                        try:
                            await box.focus()
                            payload = self._build_payload()
                            await box.fill(payload)
                            await page.keyboard.press("Enter")
                            msg_count += 1
                            if eng:
                                eng.inc("msgs")
                            METRICS.playwright_sends += 1
                            log.debug(f"[OBV-{self.engine_id}] strike {msg_count} | "
                                      f"{'LOCKER' if self.is_locker else 'SLAMMER'}")
                        except Exception as e:
                            log.debug(f"[OBV-{self.engine_id}] send fail: {_clean_exc(e)}")
                            try:
                                await page.reload(wait_until="domcontentloaded", timeout=30000)
                                box = page.locator(
                                    'div[role="textbox"], div[aria-label="Message"]'
                                ).first
                            except Exception:
                                break

                        await asyncio.sleep(self.delay)

                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.debug(f"[OBV-{self.engine_id}] restart: {_clean_exc(e)}")
                    await asyncio.sleep(1.0)
                finally:
                    if browser:
                        try:
                            await browser.close()
                        except Exception:
                            pass
                    if not stop_event.is_set():
                        try:
                            import shutil as _sh
                            _sh.rmtree(self._user_data, ignore_errors=True)
                        except Exception:
                            pass


# Active /oblivion tasks: key → (stop_event, [tasks])
_ACTIVE_OBLIVION: Dict[str, Tuple[asyncio.Event, List[asyncio.Task]]] = {}
_OBLIVION_LOCK = asyncio.Lock()


async def worker_oblivion(
    eng: "Engine",
    url: str,
    target: str,
    gc_name: str,
    user_key: str,
    engine_count: int = 4,
    delay: float = 0.01,
    sids: Optional[List[str]] = None,
    custom_text: Optional[str] = None,
):
    """
    Launch OblivionSpamEngine instances in parallel.
    Engine 1 = LOCKER (locks GC name every 19 msgs).
    Engines 2+ = SLAMMERS (pure spam).
    sids: explicit session IDs list (optional, auto-detected from ACCOUNT_MANAGER).
    url:  Instagram direct GC URL.
    target: opponent/target name injected into messages.
    gc_name: GC name for the locker engine to reset to.
    custom_text: if set, uses this as message body instead of built-in messages.
    """
    if not HAS_PLAYWRIGHT:
        log.warning("⚠️  Playwright not installed — /sasukespam unavailable")
        return

    # Get session IDs: from explicit sids or from active accounts
    if not sids:
        clients = ACCOUNT_MANAGER.list_active()
        sids    = [cl._sessionid for cl in clients if cl._sessionid]
    if not sids:
        log.warning("⚠️  No session IDs for /sasukespam")
        return

    stop_event = asyncio.Event()
    async with _OBLIVION_LOCK:
        _ACTIVE_OBLIVION[user_key] = (stop_event, [])

    tasks = []
    for i in range(engine_count):
        sid    = sids[i % len(sids)]
        engine = OblivionSpamEngine(
            engine_id=i + 1,
            sid=sid,
            url=url,
            target=target,
            gc_name=gc_name,
            delay=delay,
            custom_text=custom_text,
        )
        task = asyncio.create_task(engine.run(stop_event, eng))
        tasks.append(task)

    async with _OBLIVION_LOCK:
        _ACTIVE_OBLIVION[user_key] = (stop_event, tasks)

    log.info(
        f"🔱 OBLIVION launched {len(tasks)} engines | "
        f"target={target} | locker=E1 | delay={delay}s | key={user_key}"
    )

    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        stop_event.set()
        raise
    finally:
        async with _OBLIVION_LOCK:
            _ACTIVE_OBLIVION.pop(user_key, None)
        log.info(f"🛑 OBLIVION stopped | key={user_key}")


async def stop_oblivion(user_key: str) -> bool:
    """Stop a running /oblivion session. Returns True if found."""
    async with _OBLIVION_LOCK:
        entry = _ACTIVE_OBLIVION.get(user_key)
        if not entry:
            return False
        ev, tasks = entry
        ev.set()
        for t in tasks:
            t.cancel()
        return True


# ─────────────────────────────────────────────────────────────────────────────
# COMMAND EXECUTOR — central backend for all commands + panel UI
# Provides a single unified API used by both text commands and inline buttons.
# ─────────────────────────────────────────────────────────────────────────────
class CommandExecutor:
    """
    Central command backend.
    All spam / stop / NC / stats operations go through here.
    Used by TelegramController commands AND inline panel buttons.
    """

    def __init__(self, eng: "Engine", regs: dict):
        self.eng  = eng
        self.regs = regs

    def _primary_cl(self) -> Optional["IGClient"]:
        return self.eng.next_client()

    def _reg_for(self, cl: "IGClient") -> "TaskReg":
        return self.regs.get(cl.username, TaskReg())

    # ── get GC list ───────────────────────────────────────────────────────────
    def get_gcs(self, cl: Optional["IGClient"] = None) -> list:
        if cl is None:
            cl = self._primary_cl()
        if cl is None:
            return []
        return self.eng.get_gcs(cl.username) or []

    # ── launch ultra pwgo ─────────────────────────────────────────────────────
    async def start_ultra(
        self,
        user_key: str,
        urls: list,
        text: str,
        engine_count: int = 4,
        tabs_per_gc: int = 4,
        burst: int = 3,
    ) -> Tuple[int, str]:
        """
        Launch UltraPlaywrightSpamEngine.
        Returns (engines_launched, status_message).
        """
        if not HAS_PLAYWRIGHT:
            return 0, "❌ Playwright not installed."
        clients = ACCOUNT_MANAGER.list_active()
        if not clients:
            return 0, "❌ No active IG accounts."

        url_list   = urls if isinstance(urls, list) else [urls]
        stop_event = asyncio.Event()

        async with _PWGO_LOCK:
            _ACTIVE_PWGO[user_key] = (stop_event, [])

        tasks = []
        for i in range(engine_count):
            engine = UltraPlaywrightSpamEngine(
                engine_id=i + 1,
                urls=url_list,
                tabs_per_gc=tabs_per_gc,
                burst=burst,
            )
            task = asyncio.create_task(engine.run(text, stop_event, self.eng))
            tasks.append(task)

        async with _PWGO_LOCK:
            _ACTIVE_PWGO[user_key] = (stop_event, tasks)

        msg = (
            f"⚡ ULTRA ENGINE LAUNCHED\n"
            f"Engines  : {len(tasks)}\n"
            f"GC URLs  : {len(url_list)}\n"
            f"Tabs/GC  : {tabs_per_gc}\n"
            f"Burst    : {burst} msgs/tab\n"
            f"Delay    : 0.01s (auto-adjusts)\n"
            f"Accounts : {len(clients)} round-robin\n"
            f"Key      : {user_key}\n"
            f"Stop with /stopgo"
        )
        log.info(f"🔥 ULTRA /pwgo launched {len(tasks)} engines | key={user_key}")
        return len(tasks), msg

    # ── stop ultra ────────────────────────────────────────────────────────────
    async def stop_ultra(self, user_key: str) -> str:
        stopped = await stop_pwgo(user_key)
        if stopped:
            return f"🛑 Ultra engine stopped. (key={user_key})"
        return "⚠️ No running ultra engine found."

    # ── start smartspam ───────────────────────────────────────────────────────
    async def start_smartspam(
        self,
        user_id: int,
        target_gcs: list,
        speed: str = "fast",
        custom: Optional[str] = None,
        burst_count: int = 3,
        label: str = "panel",
    ) -> Optional[asyncio.Task]:
        cl  = self._primary_cl()
        if not cl:
            return None
        reg = self._reg_for(cl)
        reg.stop_key(f"{label}_{user_id}")
        t = asyncio.create_task(
            worker_smartspam(self.eng, target_gcs,
                             speed=speed, custom=custom, burst_count=burst_count))
        reg.add(t, f"{label}_{user_id}")
        return t

    # ── start NC ──────────────────────────────────────────────────────────────
    async def start_nc(
        self,
        user_id: int,
        names: Optional[List[str]] = None,
        label: str = "panel",
    ) -> Optional[asyncio.Task]:
        cl  = self._primary_cl()
        if not cl:
            return None
        reg = self._reg_for(cl)
        reg.stop_key(f"{label}_{user_id}")
        t = asyncio.create_task(worker_nc(self.eng, cl, names))
        reg.add(t, f"{label}_{user_id}")
        return t

    # ── stop all ──────────────────────────────────────────────────────────────
    async def stop_all(self, user_id: int) -> str:
        tg_count = TG_TASKS.stop_all(user_id)
        cl = self._primary_cl()
        ig_count = 0
        if cl:
            reg = self._reg_for(cl)
            ig_count = reg.count()
            reg.stop_all()
        TASK_CTRL.stop_all()
        return (
            f"🛑 Stopped everything.\n"
            f"TG tasks: {tg_count} | IG loops: {ig_count}\n"
            f"All spam/nc/picspam cancelled."
        )

    # ── stats ─────────────────────────────────────────────────────────────────
    def get_stats_text(self) -> str:
        ts  = TASK_STATS.snapshot()
        m   = METRICS.snapshot()
        cl  = self._primary_cl()
        gcs = self.get_gcs(cl)
        active = TASK_CTRL.list_active()
        return (
            f"📊 *ULTRA STATS*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏱ Uptime    : {uptime()}\n"
            f"📡 Accounts  : {len(self.eng._clients)}\n"
            f"📂 GCs       : {len(gcs)}\n"
            f"✅ Sent      : {ts['sent']}\n"
            f"❌ Failed    : {ts['failed']}\n"
            f"📈 Msgs/sec  : {m['msgs_per_sec']}\n"
            f"📦 Queue     : {m['queue_size']}\n"
            f"🎭 PW sends  : {m['playwright_sends']}\n"
            f"🌐 Proxies   : {len(self.eng.proxy_rotator)}\n"
            f"🔥 Tasks     : {len(active)}"
        )


# Global CommandExecutor singleton — initialized after Engine is ready in main()
_CMD_EXEC: Optional[CommandExecutor] = None

# Per-user session storage (extended state beyond panel state)
# {user_id: {"account": str|None, "ultra_key": str|None, "tabs": int, "burst": int}}
_USER_SESSIONS: Dict[int, Dict] = {}

def _user_session(user_id: int) -> dict:
    if user_id not in _USER_SESSIONS:
        _USER_SESSIONS[user_id] = {
            "account":   None,
            "ultra_key": None,
            "tabs":      4,
            "burst":     3,
        }
    return _USER_SESSIONS[user_id]



# ─────────────────────────────────────────────────────────────────────────────
# RATE LIMIT BYPASS
# ─────────────────────────────────────────────────────────────────────────────
class RateLimitBypass:
    _BACKOFF_BASE   = 2.0
    _BACKOFF_MAX    = 120.0
    _WINDOW_SEC     = 60.0
    _RATE_THRESHOLD = 3

    def __init__(self, proxy_rotator: ProxyRotator):
        self._lock     = threading.Lock()
        self._hits:    Dict[str, int]    = {}
        self._last_hit: Dict[str, float] = {}
        self._backoff: Dict[str, float]  = {}
        self._proxies  = proxy_rotator

    def record_hit(self, account: str) -> float:
        with self._lock:
            now = time.time()
            last = self._last_hit.get(account, 0)
            if now - last > self._WINDOW_SEC:
                self._hits[account] = 0
            self._hits[account]     = self._hits.get(account, 0) + 1
            self._last_hit[account] = now
            n = self._hits[account]
            delay = min(self._BACKOFF_BASE ** n + random.uniform(0, 1), self._BACKOFF_MAX)
            self._backoff[account] = delay
            return delay

    def should_use_playwright(self, account: str) -> bool:
        with self._lock:
            return self._hits.get(account, 0) >= self._RATE_THRESHOLD

    def get_proxy(self, exclude: Optional[str] = None) -> Optional[str]:
        return self._proxies.get_proxy(exclude=exclude) if len(self._proxies) > 0 else None

    def mark_proxy_ok(self, proxy: str):
        self._proxies.mark_success(proxy)

    def mark_proxy_fail(self, proxy: str):
        self._proxies.mark_failure(proxy)

    def reset(self, account: str):
        with self._lock:
            self._hits.pop(account, None)
            self._backoff.pop(account, None)

# ─────────────────────────────────────────────────────────────────────────────
# SPAM TEMPLATES
# ─────────────────────────────────────────────────────────────────────────────
_RAW_TEMPLATES = [
    (
        "‎♛𝐀ʟᴇ𝐗𝖺 ⭕ ᴘʟᴀʏ - <{name}> ᴋɪ ᴍᴜᴍᴍʏ ᴋɪ ᴄʜᴜᴅᴀɪ 💽\n"
        "ㅤㅤ0:35 ━❍──────── -5:32\n"
        "↻  ⊲  Ⅱ  ⊳  ↺\n"
        "✦•┈๑⋅⋯⋯⋅๑┈•✦\n"
        "𝐒ᴜʙ𝐀ʜ 𝐊ᴀʀ𝐓ᴀ 𝐇ᴜ ʙ𝐑ᴜ𝐒ʜ 🦧 ۩{name}۩\n"
        "𝗧𝗘𝗥𝗜 𝗠𝗔 𝗥𝗡𝗗𝗜 {emoji}"
    ),
    (
        "{name} 𝑲ɪ ᴍᴀ 𝑵ᴀɴ𝑮ᴀ ᴋᴀʀᴋᴇ ᴍᴜ𝐓ᴡᴀ 𝐃ɪʏᴀ {emoji}\n"
        "═" * 50 + "\n"
        "{name} 𝑲ɪ ᴍᴀ 𝑵ᴀɴ𝑮ᴀ ᴋᴀʀᴋᴇ ᴍᴜ𝐓ᴡᴀ 𝐃ɪʏᴀ {emoji}"
    ),
    ("[{name}] ~|ᴛᴇʀɪ ᴍᴀᴀ sᴀᴛʀᴀɴɢɪ ʀᴀᴀɴᴅ {emoji}‎\n" * 10).strip(),
    (
        "⚡ 𝗔𝗧𝗧𝗘𝗡𝗧𝗜𝗢𝗡 [{name}] ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "𝐍𝐈𝐆𝐆𝐀 𝐒𝐘𝐒𝐓𝐄𝐌 𝐰𝐚𝐬 𝐡𝐞𝐫𝐞 {emoji}\n"
        "𝐲𝐨𝐮𝐫 𝐠𝐜 𝐢𝐬 𝐨𝐰𝐧𝐞𝐝 💀\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ),
    (
        "📣 {name} 📣\n"
        "𝓣𝓮𝓻𝓲 𝓶𝓪𝓪 𝓴𝓲 𝓰𝓪𝓷𝓭 {emoji}\n"
        "▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n"
        "𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 ⚡"
    ),
    (
        "【{name}】\n"
        "┌─────────────────────┐\n"
        "│  𝗡𝗜𝗚𝗚𝗔 𝗦𝗬𝗦𝗧𝗘𝗠 v7  │\n"
        "│       {emoji}        │\n"
        "└─────────────────────┘\n"
        "𝘛𝘦𝘳𝘪 𝘔𝘢𝘢 𝘒𝘪 𝘈𝘢𝘯𝘬𝘩𝘰𝘯 𝘔𝘦𝘯 💀"
    ),
    (
        "〔{name}〕 ← 𝐓𝐡𝐢𝐬 𝐆𝐂 𝐢𝐬 𝐃𝐞𝐚𝐝 {emoji}\n"
        "𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 ⚡ was here\n"
        "𝙏𝙚𝙧𝙞 𝙈𝙖𝙖 𝙆𝙞 𝙂𝙖𝙣𝙙 {emoji}"
    ),
    (
        "☠️ 𝗪𝗔𝗥 𝗗𝗘𝗖𝗟𝗔𝗥𝗘𝗗 ☠️\n"
        "Target: 〖{name}〗\n"
        "Status: OWNED {emoji}\n"
        "By: 𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 ⚡\n"
        "Teri Maa Ki Aankh 💀"
    ),
    (
        "🏆 SCOREBOARD\n"
        "┌─────────────────────┐\n"
        "│ #{name}             │\n"
        "│ Rank: 🥇 OWNED      │\n"
        "│ Score: 0 {emoji}    │\n"
        "└─────────────────────┘\n"
        "𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 ⚡"
    ),
    (
        "💻 SYSTEM ERROR\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "Process: {name}.exe\n"
        "Error:   0xDEADC0DE {emoji}\n"
        "Action:  OWNED BY 𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 ⚡\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    ),
    (
        "root@nigga:~# ./hack {name}\n"
        "[██████████] 100%\n"
        "✅ GC OWNED\n"
        "✅ Members exposed\n"
        "✅ Teri maa ki {emoji}\n"
        "𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 v7.0 ⚡"
    ),
    (
        "📓 DEATH NOTE\n"
        "╔══════════════════╗\n"
        "║ {name}           ║\n"
        "║ OWNED. {emoji}   ║\n"
        "╚══════════════════╝\n"
        "Signed: 𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 ⚡"
    ),
    (
        "📰 BREAKING NEWS\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "GC \"{name}\" OWNED TODAY {emoji}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Full story: Teri maa ki 💀\n"
        "𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 ⚡"
    ),
    (
        "🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨\n"
        "GC [{name}] HACKED\n"
        "BY 𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 {emoji}\n"
        "TERI MAA KI AANKH 💀\n"
        "🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨"
    ),
]

random.shuffle(_RAW_TEMPLATES)
SPAM_TEMPLATES = _RAW_TEMPLATES

NC_TEXT = [
    "{text}┕━☽【🇦🇨】☾━┙𝐂𝐇𝐔𝐃 {emoji}",
    "{text}┕━☽【🇦🇫】☾━┙𝐂𝐇𝐔𝐃 {emoji}",
    "{text}┕━☽【🇦🇷】☾━┙𝐂𝐇𝐔𝐃 {emoji}",
    "{text}┕━☽【🇧🇷】☾━┙𝐂𝐇𝐔𝐃 {emoji}",
    "𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 ⚡ {emoji}",
    "〔{text}〕⚡ 𝐆𝐎𝐃 𝐌𝐎𝐃𝐄 {emoji}",
    "❰{text}❱ ☠ 𝐊𝐈𝐍𝐆 {emoji}",
    "꧁{text}꧂ 💀 {emoji}",
    "⚔️{text}⚔️ 𝐒𝐋𝐀𝐘𝐄𝐑 {emoji}",
    "「{text}」𝗕𝗢𝗦𝗦 {emoji}",
    "〖{text}〗👑 {emoji}",
    "★{text}★ 𝐆𝐎𝐃 {emoji}",
    "💀{text}💀 CHUD {emoji}",
]

GCNC_TEXT = [
    "꧁𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴꧂ {emoji}",
    "〔𝐎𝐖𝐍𝐄𝐃 𝐁𝐘 𝐍𝐒〕⚡ {emoji}",
    "❰𝗚𝗢𝗗 𝗠𝗢𝗗𝗘 𝗔𝗖𝗧𝗜𝗩𝗘❱ {emoji}",
    "【𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 v7】 💀",
    "⚡{text}⚡ 𝗢𝗪𝗡𝗘𝗗 {emoji}",
    "☠️ {text} ☠️ 𝐍𝐒 𝐖𝐀𝐒 𝐇𝐄𝐑𝐄",
    "𝗚𝗖 𝗛𝗔𝗖𝗞𝗘𝗗 💀 {emoji}",
    "〖𝑵𝑰𝑮𝑮𝑨〗👑 {emoji}",
    "★ {text} ★ 𝐊𝐈𝐍𝐆 {emoji}",
    "𝕹𝖎𝖌𝖌𝖆 𝕾𝖞𝖘𝖙𝖊𝖒 ⚡ {emoji}",
    "【𝐎𝐖𝐍𝐄𝐃】{text} {emoji}",
    "🔥{text}🔥 𝗡𝗦 {emoji}",
    "💀{text}💀 CHUD {emoji}",
]

VOICE_MAP = {
    "male":    "en-IN-PrabhatNeural",
    "female":  "en-IN-NeerjaNeural",
    "robot":   "en-US-GuyNeural",
    "anime":   "ja-JP-KeitaNeural",
    "girl":    "ja-JP-NanamiNeural",
    "default": "en-US-AriaNeural",
}

# Speed mode delays
SPEED_MODES = {
    "slow":      (2.0, 4.0),
    "medium":    (1.0, 2.0),
    "fast":      (0.5, 1.0),
    "unlimited": (0.0, 0.05),   # zero-delay burst — maximum throughput
}

# Parallel GC limits per speed mode
SPEED_PARALLEL = {
    "slow":      3,
    "medium":    6,
    "fast":      10,
    "unlimited": 32,
}

# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT CONFIG
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_CFG = {
    "owner_username":         "",
    "allowed_users":          [],
    "private_mode":           True,
    "max_gcs":                200,
    "spam_delay_min":         0.0,
    "spam_delay_max":         0.0,
    "nc_delay":               4.0,
    "cmd_poll_interval":      1.0,
    "heartbeat_interval":     30,
    "reconnect_delay":        30,
    "inbox_limit":            100,
    "base_name":              "𝑵𝑰𝑮𝑮𝑨 𝑺𝒀𝑺𝑻𝑬𝑴 <👑>",
    "pic_spam_url":           "",
    "listen_in_groups":       True,
    "burst_size":             64,
    "send_concurrency":       64,
    "use_aiohttp":            True,
    "use_proxy_rotation":     True,
    "proxy_file":             "proxies.txt",
    "use_playwright_fallback": True,
    "use_hikerapi":           False,
    "hikerapi_key":           "",
    "api_gateway_mode":       False,
    "api_gateway_port":       8080,
    "messages_per_minute":    0,
    "delay_range":            [0, 0],
    "rotate_device_per_send": True,
    "session_refresh_interval": 300,
    "smartspam_burst_count":  2,
    "gc_cooldown_sec":        30,
    "telegram_bot_token":     "",
    "emoji_pool": [
        "🤮","😜","😄","🤪","😖","👿","⚡","💀","🔥",
        "👑","🦧","☠️","🖕","💣","🤡","🤬","😈","🫵"
    ],
    "accounts": [],
}

HELP_MSG = """╔══════════ NIGGA SYSTEM v7.0 ══════════╗
🔐 /authenticate @user  /owner  /stats

━━━━━━ ACCESS CONTROL ━━━━━━
🔑 /allow @user        ← add allowed user (owner only)
🗑  /remove @user       ← remove allowed user (owner only)
📋 /allowed            ← list allowed users

━━━━━━ ACCOUNTS ━━━━━━
👤 /login <user> <pass>   /logout <user>   /accounts
🔑 /loginsession <user> <sessionid>

━━━━━━ SMART SPAM ━━━━━━
🚀 /smartspam <targets> <speed> [text]
   targets: all|@group|id1,id2
   speed: slow|medium|fast
🌐 /pwspam <targets> <speed> [text]   (Playwright mode)
🔱 /pwgo [engines] [text]             (ULTRA mode — max speed, no rate limit)
   /stopgo                            ← stop /pwgo engines
⚡ /sasnc <text>                       (ULTRA NC — 0.005s, stylish symbols)
   /stopsasnc                         ← stop sasnc

━━━━━━ USER ACCOUNT CONTROL ━━━━━━
👤 /loginuser <user> <sid>    ← store user session
🆕 /creategc <name> [users]   ← create new GC
🤖 /addbot [gc_id]            ← add all bots to GC
⭐ /promotebots [gc_id]       ← make all bots admin

━━━━━━ RAID & GC CONTROL ━━━━━━
💥 /raid <gc_name> [users]    ← create GC + bots + spam
🤖 /gcaddbots                  ← auto-detect GC, add bots
👥 /gcadd <user1,user2,...>    ← auto-detect GC, add users

━━━━━━ CURRENT GC COMMANDS ━━━━━━
🔥 /spam [text]          ← spam this GC
🏷️  /gcnc [name]          ← superfast name change loop
⚡ /godspam [text]       ← MAX-SPEED spam, never stops
🖼️  /picspam              ← pic spam this GC
🛑 /stop                 ← stop all tasks in this GC

━━━━━━ GLOBAL COMMANDS ━━━━━━
🔥 /startspam [text]     /stopspam
🏷️  /startgcnc [name]     /stopgcnc
🖼️  /startpicspam         /stoppicspam
⚙️  /stopgodspam
⚙️  /startnc [names]      /stopnc

━━━━━━ MULTI TARGETING ━━━━━━
🔥 /multispam  <targets> <mode> [text]
🏷️  /multinc    <targets> <mode> [names]
🖼️  /multipicspam <targets> <mode>
🛑 /stopmulti  <id|all>   📋 /listmulti

━━━━━━ GC MANAGEMENT ━━━━━━
🔍 /scangcs     /listgcs
➕ /addgc <id> [name]   🔀 /switchgc <id|name>
📦 /addgroup <name> <id1,id2>   /listgroups

━━━━━━ OTHER ━━━━━━
🎤 /animevoice [voice] <text>
🔎 /search <username>
⏱  /setdelay <sec>    /setncdelay <sec>
🌐 /proxystats
╚═══════════════════════════════════════╝"""

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt(t: str, **kw) -> str:
    try:    return t.format(**kw)
    except: return t

def rand_emoji(pool: list) -> str:
    return random.choice(pool) if pool else "⚡"

def oid() -> str:
    return uuid.uuid4().hex[:8]

def uptime() -> str:
    s = int((datetime.now() - BOT_START).total_seconds())
    return f"{s//3600:02d}h {s%3600//60:02d}m {s%60:02d}s"

def _vary_message(text: str) -> str:
    """Add slight variation to a message to reduce detection."""
    variations = [
        text,
        text + " ",
        " " + text,
        text + "\u200b",
    ]
    return random.choice(variations)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
def load_cfg() -> dict:
    p = "config.json"
    if os.path.exists(p):
        try:
            raw = Path(p).read_bytes() if HAS_ORJSON else Path(p).read_text(encoding="utf-8")
            d   = _json_loads(raw)
            for k, v in DEFAULT_CFG.items():
                d.setdefault(k, v)
            return d
        except Exception as e:
            log.error(f"Config load: {e}")
    Path(p).write_text(_json_dumps(DEFAULT_CFG, indent=2), encoding="utf-8")
    log.warning("⚠️  config.json created with defaults")
    return dict(DEFAULT_CFG)

def save_cfg(cfg: dict):
    try:
        Path("config.json").write_text(_json_dumps(cfg, indent=2), encoding="utf-8")
    except Exception as e:
        log.error(f"Config save: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# ACCESS CONTROL
# ─────────────────────────────────────────────────────────────────────────────
def _normalize_username(u: str) -> str:
    return u.lstrip("@").lower().strip()

def is_authorized(cfg: dict, sender: str) -> bool:
    """Return True if sender is owner or in allowed_users."""
    sender = _normalize_username(sender)
    owner  = _normalize_username(cfg.get("owner_username", ""))
    if owner and sender == owner:
        return True
    allowed = [_normalize_username(u) for u in cfg.get("allowed_users", [])]
    return sender in allowed

def is_owner(cfg: dict, sender: str) -> bool:
    sender = _normalize_username(sender)
    owner  = _normalize_username(cfg.get("owner_username", ""))
    return bool(owner) and sender == owner

# ─────────────────────────────────────────────────────────────────────────────
# SESSION LOGIN HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _list_saved_sessions() -> List[str]:
    return sorted(str(p) for p in Path(".").glob("*_session.json"))

def _console_login_menu(cfg: dict) -> List[dict]:
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║        NIGGA SYSTEM v7.0 — LOGIN MENU       ║")
    print("╠══════════════════════════════════════════════╣")
    saved = _list_saved_sessions()
    print("║  [1] Login using saved session               ║")
    print("║  [2] Login using username and password       ║")
    print("║  [3] Login using sessionid cookie            ║")
    print("╚══════════════════════════════════════════════╝")
    accounts = []
    while True:
        try:
            choice = input("\nSelect option [1/2/3]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(0)

        if choice == "1":
            if not saved:
                print("⚠️  No saved sessions found. Switching to option 2.")
                choice = "2"
            else:
                print("\nSaved sessions:")
                for i, s in enumerate(saved, 1):
                    print(f"  [{i}] {s}")
                print("  [a] Load ALL sessions")
                sel = input("Select session(s) [number/a]: ").strip().lower()
                if sel == "a":
                    chosen = saved
                else:
                    try:
                        idx = int(sel) - 1
                        chosen = [saved[idx]]
                    except (ValueError, IndexError):
                        print("❌ Invalid choice. Try again.")
                        continue
                for sf in chosen:
                    username = sf.replace("_session.json", "")
                    accounts.append({
                        "username":     username,
                        "password":     "",
                        "session_file": sf,
                        "enabled":      True,
                    })
                break

        if choice == "2":
            print("\nEnter account details (leave username blank to finish):")
            while True:
                try:
                    uname = input("  Username: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not uname:
                    break
                try:
                    passwd = getpass.getpass(f"  Password for @{uname}: ")
                except Exception:
                    passwd = input(f"  Password for @{uname}: ")
                accounts.append({"username": uname, "password": passwd, "enabled": True})
            if accounts:
                break
            print("⚠️  No accounts entered. Try again.")
            continue

        if choice == "3":
            print("\nSessionid login (leave username blank to finish):")
            while True:
                try:
                    uname = input("  Instagram username: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not uname:
                    break
                try:
                    sid = input(f"  sessionid cookie for @{uname}: ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not sid:
                    print("❌ sessionid cannot be empty.")
                    continue
                accounts.append({
                    "username":  uname,
                    "password":  "",
                    "sessionid": sid,
                    "enabled":   True,
                })
                print(f"✅ @{uname} queued for sessionid login.")
            if accounts:
                break
            print("⚠️  No accounts entered. Try again.")
            continue

        if choice not in ("1", "2", "3"):
            print("❌ Invalid option. Enter 1, 2, or 3.")
    return accounts

# ─────────────────────────────────────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────────────────────────────────────
class Engine:
    def __init__(self, cfg: dict, proxy_rotator: ProxyRotator):
        self.cfg          = cfg
        self.running      = True
        self._lock        = threading.Lock()
        self.groups:      Dict[str, List[dict]] = {}
        self.gc_groups:   Dict[str, List[str]]  = {}
        self.active_gc:   Dict[str, Optional[dict]] = {}
        self.stats        = dict(msgs=0, nc=0, errors=0, reconnects=0, logins=0, rl_hits=0)
        self._clients:    List["IGClient"] = []
        self._rr_idx      = 0
        self._account_threads: Dict[str, threading.Thread] = {}
        self._account_regs:    Dict[str, "TaskReg"] = {}
        self.proxy_rotator = proxy_rotator
        self.rate_bypass   = RateLimitBypass(proxy_rotator)
        # GC cooldown tracker (for smart spam)
        self._gc_cooldown: Dict[str, float] = {}
        # Last active GC per account (for auto-detection)
        self._last_active_gc: Dict[str, Optional[dict]] = {}

    def register_client(self, cl: "IGClient"):
        with self._lock:
            if cl not in self._clients:
                self._clients.append(cl)
        ACCOUNT_MANAGER.register(cl)

    def unregister_client(self, cl: "IGClient"):
        with self._lock:
            try: self._clients.remove(cl)
            except ValueError: pass
        ACCOUNT_MANAGER.unregister(cl)

    def next_client(self) -> Optional["IGClient"]:
        with self._lock:
            if not self._clients:
                return None
            cl = self._clients[self._rr_idx % len(self._clients)]
            self._rr_idx += 1
            return cl

    def get_client(self, username: str) -> Optional["IGClient"]:
        with self._lock:
            for cl in self._clients:
                if cl.username.lower() == username.lower():
                    return cl
            return None

    def list_usernames(self) -> List[str]:
        with self._lock:
            return [cl.username for cl in self._clients]

    def inc(self, k: str, n=1):
        with self._lock:
            self.stats[k] = self.stats.get(k, 0) + n

    def stats_str(self):
        with self._lock: s = dict(self.stats)
        return (f"Msgs:{s['msgs']} NC:{s['nc']} "
                f"RL:{s['rl_hits']} Reconnects:{s['reconnects']} Errs:{s['errors']}")

    def get_gcs(self, u):
        with self._lock: return list(self.groups.get(u, []))

    def set_gcs(self, u, gcs):
        with self._lock: self.groups[u] = gcs
        self._save_groups()

    def _save_groups(self):
        try:
            with self._lock:
                data = {u: {"groups": g} for u, g in self.groups.items()}
            Path("groups.json").write_text(_json_dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            log.error(f"Groups save: {e}")

    def load_groups(self):
        try:
            p = Path("groups.json")
            if not p.exists(): return
            raw = p.read_bytes() if HAS_ORJSON else p.read_text(encoding="utf-8")
            d   = _json_loads(raw)
            with self._lock:
                for u, v in d.items():
                    raw2 = v.get("groups", [])
                    self.groups[u] = [
                        {"id": e, "name": "Unknown"} if isinstance(e, str) else e
                        for e in raw2
                    ]
        except Exception as e:
            log.error(f"Groups load: {e}")

    def save_gcgroups(self):
        try:
            Path("gc_groups.json").write_text(
                _json_dumps(self.gc_groups, indent=2), encoding="utf-8")
        except Exception as e:
            log.error(f"GC groups save: {e}")

    def load_gcgroups(self):
        try:
            p = Path("gc_groups.json")
            if not p.exists(): return
            raw = p.read_bytes() if HAS_ORJSON else p.read_text(encoding="utf-8")
            self.gc_groups = _json_loads(raw)
        except Exception as e:
            log.error(f"GC groups load: {e}")

    def all_gcs(self) -> list:
        with self._lock:
            seen, out = set(), []
            for gcs in self.groups.values():
                for g in gcs:
                    if g["id"] not in seen:
                        seen.add(g["id"])
                        out.append(g)
            return out

    def add_account_thread(self, acct: dict, regs: dict):
        uname = acct["username"]
        if uname in self._account_threads and self._account_threads[uname].is_alive():
            log.warning(f"@{uname} already running.")
            return False
        reg = TaskReg()
        regs[uname] = reg
        self._account_regs[uname] = reg
        t = threading.Thread(
            target=thread_account,
            args=(self, acct, reg, regs),
            name=f"acct-{uname}",
            daemon=True,
        )
        self._account_threads[uname] = t
        t.start()
        return True

    def remove_account(self, username: str) -> bool:
        cl = self.get_client(username)
        if not cl:
            return False
        self.unregister_client(cl)
        return True

    def set_gc_cooldown(self, gc_id: str, sec: float):
        with self._lock:
            self._gc_cooldown[gc_id] = time.time() + sec

    def is_gc_on_cooldown(self, gc_id: str) -> bool:
        with self._lock:
            return self._gc_cooldown.get(gc_id, 0) > time.time()

    def update_last_active_gc(self, username: str, gc: dict):
        with self._lock:
            self._last_active_gc[username] = gc

    def get_last_active_gc(self, username: str) -> Optional[dict]:
        with self._lock:
            return self._last_active_gc.get(username)

# ─────────────────────────────────────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────────────────────────────────────
class Metrics:
    def __init__(self, window: int = 10):
        self._lock            = threading.Lock()
        self._window          = window
        self._ts_deque:       collections.deque = collections.deque()
        self.queue_size       = 0
        self.workers_active   = 0
        self.workers_total    = 0
        self.errors_total     = 0
        self.proxy_switches   = 0
        self.playwright_sends = 0
        self.hikerapi_sends   = 0

    def record_send(self, count: int = 1):
        now = time.monotonic()
        with self._lock:
            for _ in range(count):
                self._ts_deque.append(now)
            cutoff = now - self._window
            while self._ts_deque and self._ts_deque[0] < cutoff:
                self._ts_deque.popleft()

    def msgs_per_sec(self) -> float:
        now = time.monotonic()
        with self._lock:
            cutoff = now - self._window
            while self._ts_deque and self._ts_deque[0] < cutoff:
                self._ts_deque.popleft()
            return round(len(self._ts_deque) / self._window, 2)

    def worker_utilization(self) -> float:
        if not self.workers_total:
            return 0.0
        return round(self.workers_active / self.workers_total * 100, 1)

    def snapshot(self) -> dict:
        cpu = psutil.cpu_percent() if HAS_PSUTIL else None
        mem = psutil.virtual_memory().percent if HAS_PSUTIL else None
        return {
            "msgs_per_sec":       self.msgs_per_sec(),
            "queue_size":         self.queue_size,
            "worker_utilization": f"{self.worker_utilization()}%",
            "workers_active":     self.workers_active,
            "workers_total":      self.workers_total,
            "errors_total":       self.errors_total,
            "proxy_switches":     self.proxy_switches,
            "playwright_sends":   self.playwright_sends,
            "hikerapi_sends":     self.hikerapi_sends,
            "cpu_percent":        cpu,
            "mem_percent":        mem,
        }

METRICS = Metrics()

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL TASK STATS — updated by every send(), readable from anywhere
# ─────────────────────────────────────────────────────────────────────────────
class TaskStats:
    def __init__(self):
        self._lock  = threading.Lock()
        self.sent   = 0
        self.failed = 0
        # Per-task stats: task_id -> {"sent": int, "failed": int, "running": bool}
        self._tasks: Dict[str, dict] = {}

    def record(self, ok: bool, task_id: Optional[str] = None):
        with self._lock:
            if ok:
                self.sent += 1
            else:
                self.failed += 1
            if task_id and task_id in self._tasks:
                if ok:
                    self._tasks[task_id]["sent"] += 1
                else:
                    self._tasks[task_id]["failed"] += 1

    def register_task(self, task_id: str):
        with self._lock:
            self._tasks[task_id] = {"sent": 0, "failed": 0, "running": True}

    def finish_task(self, task_id: str):
        with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id]["running"] = False

    def get_task(self, task_id: str) -> dict:
        with self._lock:
            return dict(self._tasks.get(task_id, {}))

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "sent":   self.sent,
                "failed": self.failed,
                "tasks":  {k: dict(v) for k, v in self._tasks.items()},
            }

TASK_STATS = TaskStats()

# ─────────────────────────────────────────────────────────────────────────────
# STATUS WRITER
# ─────────────────────────────────────────────────────────────────────────────
def _status_writer(eng: "Engine", regs: dict, interval: int = 10):
    while eng.running:
        try:
            ops  = sum(r.count() for r in regs.values())
            snap = METRICS.snapshot()
            doc  = {
                "version":    "v7.0",
                "uptime":     uptime(),
                "accounts":   len(eng._clients),
                "proxies":    len(eng.proxy_rotator),
                "active_ops": ops,
                "stats":      dict(eng.stats),
                "metrics":    snap,
                "timestamp":  datetime.now().isoformat(timespec="seconds"),
            }
            Path("status.json").write_text(_json_dumps(doc, indent=2), encoding="utf-8")
        except Exception as e:
            log.debug(f"Status write: {e}")
        time.sleep(interval)

# ─────────────────────────────────────────────────────────────────────────────
# CPU BATCH MESSAGE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def _cpu_batch_messages(templates: list, emoji_pool: list,
                        gc_name: str, burst: int,
                        custom: Optional[str] = None) -> List[str]:
    import random as _r
    def _fmt(t: str, **kw) -> str:
        try:    return t.format(**kw)
        except: return t
    msgs = []
    for _ in range(burst):
        em  = _r.choice(emoji_pool) if emoji_pool else "⚡"
        msg = (_fmt(custom, name=gc_name, emoji=em)
               if custom else
               _fmt(_r.choice(templates), name=gc_name, emoji=em))
        msgs.append(msg)
    return msgs

# ─────────────────────────────────────────────────────────────────────────────
# INSTAGRAM CLIENT
# ─────────────────────────────────────────────────────────────────────────────
_IG_API    = "https://i.instagram.com/api/v1"
_IG_APP_ID = "936619743392459"

class IGClient:
    def __init__(self, username: str, password: str, cfg: dict,
                 session_file: Optional[str] = None,
                 eng: Optional[Engine] = None):
        self.username      = username
        self.password      = password
        self.cfg           = cfg
        self._eng          = eng
        self._cl           = InstaClient()
        self._cl.delay_range = [0, 0]
        self._session_file = session_file or f"{username}_session.json"
        self._aio_session: Optional["aiohttp.ClientSession"] = None
        self._cookie_str   = ""
        self._logged_in    = False
        self._sessionid    = ""
        self._device       = _random_device()
        self._last_refresh = time.time()
        self._send_count   = 0
        self._send_errors  = 0

    def _rotate_device(self):
        if self.cfg.get("rotate_device_per_send", True):
            self._device = _random_device()

    # ── login ─────────────────────────────────────────────────────────────────
    def login(self) -> bool:
        if self._logged_in:
            return True
        log.info(f"🔐 LOGIN @{self.username}…")
        if os.path.exists(self._session_file):
            try:
                self._cl.load_settings(self._session_file)
                if self.password:
                    self._cl.login(self.username, self.password)
                else:
                    self._cl.login(self.username, self.password or "")
                self._cl.account_info()
                log.info(f"✅ @{self.username} session restored")
                self._build_cookie_str()
                self._logged_in = True
                return True
            except Exception as e:
                log.warning(f"⚠️  Session restore @{self.username}: {e}")
                self._cl = InstaClient()
                self._cl.delay_range = [0, 0]
        if not self.password:
            log.error(f"❌ No password for @{self.username} and no valid session.")
            return False
        try:
            self._cl.login(self.username, self.password)
            self._cl.dump_settings(self._session_file)
            log.info(f"✅ @{self.username} logged in → session saved")
            self._build_cookie_str()
            self._logged_in = True
            return True
        except TwoFactorRequired:
            return self._handle_2fa()
        except ChallengeRequired:
            return self._handle_challenge()
        except BadPassword:
            log.error(f"❌ Bad password @{self.username}")
            return False
        except Exception as e:
            log.error(f"❌ Login ERROR @{self.username}: {_clean_exc(e)}")
            return False

    def _handle_2fa(self) -> bool:
        try:
            print(f"\n🔑 2FA required for @{self.username}")
            code = input(f"   Enter 2FA code: ").strip()
            self._cl.login(self.username, self.password, verification_code=code)
            self._cl.dump_settings(self._session_file)
            log.info(f"✅ @{self.username} 2FA OK → session saved")
            self._build_cookie_str()
            self._logged_in = True
            return True
        except Exception as e:
            log.error(f"❌ 2FA failed @{self.username}: {_clean_exc(e)}")
            return False

    def _handle_challenge(self) -> bool:
        log.warning(f"⚠️  Challenge required @{self.username}")
        print(f"\n⚠️  Instagram requires identity verification for @{self.username}")
        try:
            self._cl.challenge_resolve(self._cl.last_json)
        except Exception:
            pass
        method = input("   Choose verification method:\n   [0] Email  [1] SMS: ").strip()
        try:
            self._cl.challenge_send_code(int(method))
        except Exception as e:
            log.warning(f"challenge_send_code: {e}")
        code = input(f"   Enter verification code for @{self.username}: ").strip()
        try:
            self._cl.challenge_resolve(self._cl.last_json, code)
            self._cl.dump_settings(self._session_file)
            log.info(f"✅ @{self.username} challenge passed → session saved")
            self._build_cookie_str()
            self._logged_in = True
            return True
        except Exception as e:
            log.error(f"❌ Challenge failed @{self.username}: {_clean_exc(e)}")
            return False

    def login_sessionid(self, sessionid: str) -> bool:
        if self._logged_in:
            return True
        log.info(f"🔑 SESSION LOGIN @{self.username}…")
        try:
            self._cl = InstaClient()
            self._cl.delay_range = [0, 0]
            ok = self._cl.login_by_sessionid(sessionid)
            if not ok:
                raise RuntimeError("login_by_sessionid returned False")
            try:
                info = self._cl.account_info()
                uid  = info.pk
            except Exception:
                uid = self._cl.user_id_from_username(self.username)
            log.info(f"✅ @{self.username} sessionid login OK (uid={uid}) → session saved")
            self._cl.dump_settings(self._session_file)
            self._sessionid = sessionid
            self._build_cookie_str()
            self._logged_in = True
            return True
        except Exception as e:
            log.error(f"❌ Session login ERROR @{self.username}: {_clean_exc(e)}")
            return False

    # ── cookie / auth helpers ─────────────────────────────────────────────────
    def _build_cookie_str(self):
        try:
            settings = self._cl.get_settings()
            cookies  = settings.get("cookies", {})
            self._cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items() if v)
            sid = cookies.get("sessionid", "")
            if sid and not self._sessionid:
                self._sessionid = sid
        except Exception:
            self._cookie_str = ""

    def _get_csrf(self) -> str:
        try:
            return self._cl.get_settings().get("cookies", {}).get("csrftoken", "")
        except Exception:
            return ""

    def _get_uuid(self) -> str:
        try:
            return self._cl.get_settings().get("uuid", "") or str(uuid.uuid4())
        except Exception:
            return str(uuid.uuid4())

    def _get_device_id(self) -> str:
        return self._device.get("device_id", f"android-{uuid.uuid4().hex[:16]}")

    def _build_post_headers(self, device: Optional[dict] = None) -> dict:
        d    = device or self._device
        csrf = self._get_csrf()
        return {
            "User-Agent":           d["user_agent"],
            "X-IG-App-ID":          _IG_APP_ID,
            "X-IG-Capabilities":    "3brTvwE=",
            "X-IG-Connection-Type": "WIFI",
            "Content-Type":         "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept-Language":      "en-US",
            "Accept-Encoding":      "gzip, deflate",
            "X-CSRFToken":          csrf,
            "X-MID":                uuid.uuid4().hex,
            "Cookie":               self._cookie_str,
        }

    def _build_get_headers(self) -> dict:
        h = self._build_post_headers()
        h.pop("Content-Type", None)
        return h

    # ── aiohttp session ────────────────────────────────────────────────────────
    async def _ensure_aio(self, force_rebuild: bool = False,
                          proxy: Optional[str] = None):
        if not HAS_AIOHTTP or not self.cfg.get("use_aiohttp", True):
            return
        if force_rebuild and self._aio_session and not self._aio_session.closed:
            try:
                await self._aio_session.close()
            except Exception:
                pass
            self._aio_session = None
        if self._aio_session is None or self._aio_session.closed:
            connector = aiohttp.TCPConnector(
                limit=2048, ttl_dns_cache=600, use_dns_cache=True,
                ssl=False, keepalive_timeout=120, enable_cleanup_closed=True,
            )
            self._aio_session = aiohttp.ClientSession(
                connector=connector,
                connector_owner=True,
                cookie_jar=aiohttp.DummyCookieJar(),
            )

    async def close(self):
        if self._aio_session and not self._aio_session.closed:
            await self._aio_session.close()

    # ── session refresh (every 5 min or on demand) ────────────────────────────
    async def _refresh_auth(self) -> bool:
        try:
            self._build_cookie_str()
            if self._cookie_str:
                await self._ensure_aio(force_rebuild=True)
                self._last_refresh = time.time()
                return True
        except Exception:
            pass
        try:
            loop = asyncio.get_running_loop()
            ok   = await loop.run_in_executor(_POOL, self._try_refresh_session)
            if ok:
                self._build_cookie_str()
                await self._ensure_aio(force_rebuild=True)
                self._last_refresh = time.time()
                log.info(f"✅ @{self.username} session refreshed")
            return ok
        except Exception as e:
            log.debug(f"_refresh_auth @{self.username}: {e}")
            return False

    async def _maybe_refresh_session(self):
        """Auto-refresh session every N seconds."""
        interval = self.cfg.get("session_refresh_interval", 300)
        if time.time() - self._last_refresh > interval:
            await self._refresh_auth()

    # ── send text with 3-retry + exponential backoff ──────────────────────────
    async def send(self, tid: str, text: str) -> bool:
        eng       = self._eng
        rl_bypass = eng.rate_bypass if eng else None

        # Auto-refresh session if stale
        await self._maybe_refresh_session()

        self._send_count += 1

        # ── Step 1: aiohttp with retry (3 attempts, exponential backoff) ──────
        if HAS_AIOHTTP and self.cfg.get("use_aiohttp", True):
            proxy   = rl_bypass.get_proxy() if rl_bypass else None
            backoff = 1.0

            for attempt in range(4):
                try:
                    if attempt > 0:
                        self._rotate_device()
                        await self._ensure_aio(force_rebuild=True)
                        await asyncio.sleep(backoff + random.uniform(0, 0.5))
                        backoff = min(backoff * 2, 16.0)
                    else:
                        await self._ensure_aio()

                    if not self._aio_session or self._aio_session.closed:
                        break

                    url  = f"{_IG_API}/direct_v2/threads/{tid}/broadcast/text/"
                    data = {
                        "client_context": str(random.randint(10**18, 10**19 - 1)),
                        "text":           text,
                        "mutation_token": str(random.randint(10**18, 10**19 - 1)),
                        "_uuid":          self._get_uuid(),
                        "_csrftoken":     self._get_csrf(),
                        "device_id":      self._get_device_id(),
                    }
                    hdrs = self._build_post_headers()
                    kw   = dict(data=data, headers=hdrs,
                                timeout=aiohttp.ClientTimeout(total=12))
                    if proxy:
                        kw["proxy"] = proxy

                    async with self._aio_session.post(url, **kw) as resp:
                        if resp.status in (200, 201):
                            try:
                                r = await resp.json(content_type=None)
                            except Exception:
                                r = {}

                            status_ok = r.get("status") == "ok" or "item_id" in r
                            # Also check for item_ack fail
                            if status_ok:
                                if proxy and rl_bypass:
                                    rl_bypass.mark_proxy_ok(proxy)
                                if rl_bypass:
                                    rl_bypass.reset(self.username)
                                if eng:
                                    ACCOUNT_MANAGER.mark_success(self.username)
                                log.info(f"✔ sent @{self.username} → {tid[:12]}…")
                                TASK_STATS.record(True)
                                return True

                            # item_ack fail or status fail — refresh and retry
                            err_msg = str(r).lower()
                            if "fail" in err_msg or "item_ack" in err_msg:
                                log.debug(f"item_ack fail @{self.username} → refreshing auth")
                                await self._refresh_auth()
                                continue

                            break  # other 200 non-ok, fall to instagrapi

                        elif resp.status == 429:
                            if eng: eng.inc("rl_hits")
                            METRICS.proxy_switches += 1
                            delay = rl_bypass.record_hit(self.username) if rl_bypass else 4.0
                            log.debug(f"⚠️  429 @{self.username} → backoff {delay:.1f}s")
                            if proxy and rl_bypass:
                                rl_bypass.mark_proxy_fail(proxy)
                            proxy = rl_bypass.get_proxy(exclude=proxy) if rl_bypass else None
                            await asyncio.sleep(min(delay, 30.0))
                            continue

                        elif resp.status in (403, 401):
                            try:
                                body_txt = await resp.text()
                            except Exception:
                                body_txt = ""
                            log.debug(f"⚠️  {resp.status} @{self.username} → refreshing auth")
                            refreshed = await self._refresh_auth()
                            if refreshed and attempt < 3:
                                continue
                            break
                        else:
                            break

                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    log.debug(f"aiohttp send err @{self.username}: {e}")
                    if attempt < 3:
                        await asyncio.sleep(backoff)
                        backoff = min(backoff * 2, 16.0)

        # ── Step 2: Playwright fallback after 3 API failures ──────────────────
        if (self.cfg.get("use_playwright_fallback", True) and HAS_PLAYWRIGHT
                and _PW_ENGINE._ready and self._sessionid):
            if rl_bypass and rl_bypass.should_use_playwright(self.username):
                ok = await _PW_ENGINE.send_message_human(
                    self.username, tid, text, self._sessionid)
                if ok:
                    if eng: eng.inc("msgs")
                    METRICS.playwright_sends += 1
                    log.info(f"⚡ playwright used @{self.username} → {tid[:12]}…")
                    TASK_STATS.record(True)
                    return True

        # ── Step 3: instagrapi sync fallback ──────────────────────────────────
        try:
            loop    = asyncio.get_running_loop()
            tid_int = int(tid) if str(tid).lstrip("-").isdigit() else tid
            await loop.run_in_executor(
                _POOL, lambda: self._cl.direct_send(text, thread_ids=[tid_int]))
            log.info(f"✔ sent (fallback) @{self.username} → {tid[:12]}…")
            TASK_STATS.record(True)
            return True
        except asyncio.CancelledError:
            raise
        except Exception as e:
            self._send_errors += 1
            if eng:
                ACCOUNT_MANAGER.mark_error(self.username)
            log.info(f"❌ failed @{self.username}: {_clean_exc(e)}")
            TASK_STATS.record(False)
            return False

    # ── send photo ────────────────────────────────────────────────────────────
    async def send_photo(self, tid: str, path: Path) -> bool:
        if HAS_AIOHTTP and self.cfg.get("use_aiohttp", True):
            try:
                await self._ensure_aio(force_rebuild=False)
                url       = f"{_IG_API}/direct_v2/threads/{tid}/broadcast/configure_photo/"
                upload_id = str(int(time.time() * 1000))
                upload_url = (
                    f"{_IG_API.replace('/api/v1','')}/rupload/"
                    f"instagram_direct_photo/{upload_id}_0"
                )
                hdrs = self._build_post_headers()
                hdrs.update({
                    "X-Entity-Type":   "image/jpeg",
                    "X-Instagram-Rupload-Params": '{"media_type":1,"upload_media_height":1080,"upload_media_width":1080}',
                    "X-Entity-Name":   f"{upload_id}_0",
                    "X-Entity-Length": str(path.stat().st_size),
                    "Offset":          "0",
                    "Content-Type":    "application/octet-stream",
                })
                photo_bytes = path.read_bytes()
                async with self._aio_session.post(
                    upload_url, data=photo_bytes, headers=hdrs,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status in (200, 201):
                        r = await resp.json(content_type=None)
                        upload_id = r.get("upload_id", upload_id)
                        conf_data = {
                            "upload_id":      upload_id,
                            "thread_id":      tid,
                            "client_context": str(random.randint(10**18, 10**19-1)),
                            "_uuid":          self._get_uuid(),
                            "_csrftoken":     self._get_csrf(),
                        }
                        async with self._aio_session.post(
                            url, data=conf_data,
                            headers=self._build_post_headers(),
                            timeout=aiohttp.ClientTimeout(total=15)
                        ) as r2:
                            if r2.status in (200, 201):
                                return True
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.debug(f"aiohttp send_photo fail @{self.username}: {e}")
        try:
            loop    = asyncio.get_running_loop()
            tid_int = int(tid) if str(tid).lstrip("-").isdigit() else tid
            await loop.run_in_executor(
                _POOL, lambda: self._cl.direct_send_photo(path, thread_ids=[tid_int]))
            return True
        except Exception as e:
            log.error(f"❌ send_photo @{self.username}: {_clean_exc(e)}")
            return False

    # ── name change ────────────────────────────────────────────────────────────
    async def change_name(self, name: str) -> bool:
        if HAS_AIOHTTP and self.cfg.get("use_aiohttp", True):
            try:
                await self._ensure_aio()
                url  = f"{_IG_API}/accounts/edit_profile/"
                data = {
                    "first_name": name,
                    "_uuid":      self._get_uuid(),
                    "_csrftoken": self._get_csrf(),
                }
                async with self._aio_session.post(
                    url, data=data, headers=self._build_post_headers(),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status in (403, 401):
                        await self._refresh_auth()
                    elif resp.status in (200, 201):
                        r = await resp.json(content_type=None)
                        if r.get("status") == "ok":
                            return True
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.debug(f"aiohttp change_name fail @{self.username}: {e}")
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(_POOL, lambda: self._cl.account_edit(full_name=name))
            return True
        except Exception:
            return False

    # ── GC name change ─────────────────────────────────────────────────────────
    async def change_gc_name(self, thread_id: str, title: str) -> bool:
        if HAS_AIOHTTP and self.cfg.get("use_aiohttp", True):
            try:
                await self._ensure_aio()
                url  = f"{_IG_API}/direct_v2/threads/{thread_id}/update_title/"
                data = {
                    "title":      title,
                    "_uuid":      self._get_uuid(),
                    "_csrftoken": self._get_csrf(),
                }
                async with self._aio_session.post(
                    url, data=data, headers=self._build_post_headers(),
                    timeout=aiohttp.ClientTimeout(total=8)
                ) as resp:
                    if resp.status in (403, 401):
                        await self._refresh_auth()
                    elif resp.status in (200, 201):
                        r = await resp.json(content_type=None)
                        if r.get("status") == "ok":
                            return True
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.debug(f"aiohttp change_gc_name fail @{self.username}: {e}")
        try:
            loop    = asyncio.get_running_loop()
            tid_val = int(thread_id) if str(thread_id).lstrip("-").isdigit() else thread_id
            await loop.run_in_executor(
                _POOL, lambda: self._cl.direct_thread_update_title(tid_val, title))
            return True
        except Exception:
            return False

    # ── add user to thread ─────────────────────────────────────────────────────
    async def add_users_to_thread(self, thread_id: str, user_ids: List[str]) -> bool:
        try:
            loop    = asyncio.get_running_loop()
            tid_int = int(thread_id) if str(thread_id).lstrip("-").isdigit() else thread_id
            uid_ints = []
            for uid in user_ids:
                try:
                    uid_ints.append(int(uid))
                except ValueError:
                    pass
            if not uid_ints:
                return False
            await loop.run_in_executor(
                _POOL, lambda: self._cl.direct_thread_add_user(tid_int, uid_ints))
            return True
        except Exception as e:
            log.debug(f"add_users_to_thread @{self.username}: {e}")
            return False

    # ── create GC ─────────────────────────────────────────────────────────────
    async def create_group_thread(self, user_ids: List[str], title: str = "") -> Optional[str]:
        try:
            loop = asyncio.get_running_loop()
            uid_ints = [int(u) for u in user_ids if u.isdigit()]
            thread = await loop.run_in_executor(
                _POOL, lambda: self._cl.direct_thread_create(uid_ints))
            tid = str(thread.id)
            if title:
                await asyncio.sleep(2)
                await self.change_gc_name(tid, title)
            return tid
        except Exception as e:
            log.error(f"❌ create_group_thread @{self.username}: {_clean_exc(e)}")
            return None

    # ── resolve username to user_id ───────────────────────────────────────────
    async def get_user_id(self, username: str) -> Optional[str]:
        try:
            loop = asyncio.get_running_loop()
            uid  = await loop.run_in_executor(
                _POOL, lambda: self._cl.user_id_from_username(username))
            return str(uid)
        except Exception as e:
            log.debug(f"get_user_id {username}: {e}")
            return None

    # ── search ────────────────────────────────────────────────────────────────
    async def search(self, q: str) -> list:
        try:
            loop    = asyncio.get_running_loop()
            results = await loop.run_in_executor(
                _POOL, lambda: self._cl.search_users(q, count=5))
            return [{"username": u.username, "full_name": u.full_name} for u in results]
        except Exception as e:
            log.error(f"❌ search @{self.username}: {_clean_exc(e)}")
            return []

    # ── session refresh (sync) ────────────────────────────────────────────────
    def _try_refresh_session(self) -> bool:
        try:
            if os.path.exists(self._session_file):
                self._cl = InstaClient()
                self._cl.delay_range = [0, 0]
                self._cl.load_settings(self._session_file)
                self._cl.login(self.username, self.password or "")
                self._cl.dump_settings(self._session_file)
                self._build_cookie_str()
                self._logged_in = True
                return True
        except Exception:
            pass
        return False

    # ── get inbox ─────────────────────────────────────────────────────────────
    async def get_inbox(self, limit: int = 30) -> list:
        result: list = []
        aio_threads = await self._fetch_inbox_url(
            f"{_IG_API}/direct_v2/inbox/"
            f"?visual_message_return_type=unseen&limit={limit}"
            f"&persistentBadging=true&is_prefetching=false",
            "inbox",
        )
        if aio_threads:
            result.extend(aio_threads)
        else:
            try:
                loop    = asyncio.get_running_loop()
                threads = await loop.run_in_executor(
                    _POOL, lambda: self._cl.direct_threads(amount=limit))
                for t in threads:
                    users = [{"username": u.username, "pk": str(u.pk)} for u in t.users]
                    items = [{"item_id": str(it.id), "text": it.text or "",
                              "user_id": str(it.user_id)} for it in t.messages]
                    result.append({
                        "thread_id":    str(t.id),
                        "is_group":     t.is_group,
                        "thread_title": t.thread_title or "",
                        "users":        users,
                        "items":        items,
                    })
            except asyncio.CancelledError:
                raise
            except LoginRequired:
                try:
                    loop = asyncio.get_running_loop()
                    refreshed = await loop.run_in_executor(_POOL, self._try_refresh_session)
                    if refreshed:
                        await self._ensure_aio(force_rebuild=True)
                except Exception:
                    pass
            except Exception as e:
                log.debug(f"Inbox fallback @{self.username}: {e}")
        pending = await self._get_pending_inbox(limit)
        for t in pending:
            tid = t.get("thread_id", "")
            if tid:
                asyncio.create_task(self._approve_thread(tid))
        result.extend(pending)
        return result

    async def _get_pending_inbox(self, limit: int = 30) -> list:
        result = await self._fetch_inbox_url(
            f"{_IG_API}/direct_v2/pending_inbox/"
            f"?visual_message_return_type=unseen&limit={limit}",
            "inbox",
        )
        if result:
            return result
        try:
            loop = asyncio.get_running_loop()
            if hasattr(self._cl, "direct_pending_inbox"):
                threads = await loop.run_in_executor(_POOL, self._cl.direct_pending_inbox)
                out = []
                for t in threads:
                    users = [{"username": u.username, "pk": str(u.pk)} for u in t.users]
                    items = [{"item_id": str(it.id), "text": it.text or "",
                              "user_id": str(it.user_id)} for it in t.messages]
                    out.append({
                        "thread_id":    str(t.id),
                        "is_group":     t.is_group,
                        "thread_title": t.thread_title or "",
                        "users":        users,
                        "items":        items,
                    })
                return out
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        return []

    async def _approve_thread(self, thread_id: str) -> None:
        try:
            await self._ensure_aio()
            if self._aio_session and not self._aio_session.closed:
                url  = f"{_IG_API}/direct_v2/threads/{thread_id}/approve/"
                data = {"_uuid": self._get_uuid(), "_csrftoken": self._get_csrf()}
                async with self._aio_session.post(
                    url, data=data, headers=self._build_post_headers(),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        return
                    if resp.status in (403, 401):
                        await self._refresh_auth()
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        try:
            loop = asyncio.get_running_loop()
            if hasattr(self._cl, "direct_thread_approve"):
                await loop.run_in_executor(
                    _POOL, lambda: self._cl.direct_thread_approve(thread_id))
        except Exception:
            pass

    async def _fetch_inbox_url(self, url: str, wrapper_key: str) -> list:
        if not HAS_AIOHTTP:
            return []
        for _attempt in range(2):
            try:
                await self._ensure_aio()
                if not self._aio_session or self._aio_session.closed:
                    return []
                async with self._aio_session.get(
                    url,
                    headers=self._build_get_headers(),
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status in (403, 401):
                        refreshed = await self._refresh_auth()
                        if refreshed and _attempt == 0:
                            continue
                        return []
                    if resp.status != 200:
                        return []
                    data = await resp.json(content_type=None)
                raw_threads = data.get(wrapper_key, {}).get("threads", [])
                result = []
                for t in raw_threads:
                    tid   = str(t.get("thread_id", t.get("id", "")))
                    title = t.get("thread_title", "") or tid
                    users = [{"username": u.get("username", ""),
                              "pk": str(u.get("pk", u.get("id", "")))}
                             for u in t.get("users", [])]
                    raw_items = t.get("items", []) or t.get("last_permanent_item", [])
                    if isinstance(raw_items, dict):
                        raw_items = [raw_items]
                    items = []
                    for it in raw_items:
                        text = ""
                        if it.get("item_type") == "text":
                            text = it.get("text", "")
                        elif "text" in it:
                            text = it.get("text", "")
                        items.append({
                            "item_id": str(it.get("item_id", it.get("id", ""))),
                            "text":    text,
                            "user_id": str(it.get("user_id", "")),
                        })
                    is_group = t.get("is_group", len(users) > 1)
                    if tid:
                        result.append({
                            "thread_id":    tid,
                            "is_group":     is_group,
                            "thread_title": title,
                            "users":        users,
                            "items":        items,
                        })
                return result
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.debug(f"_fetch_inbox_url @{self.username}: {e}")
                return []
        return []

    async def discover_gcs(self, limit: int = 200) -> list:
        gcs = []
        log.info(f"🔍 Scanning GCs @{self.username}…")
        try:
            loop    = asyncio.get_running_loop()
            threads = await loop.run_in_executor(
                _POOL, lambda: self._cl.direct_threads(amount=limit))
            for t in threads:
                if t.is_group or len(t.users) > 1:
                    tid  = str(t.id)
                    name = t.thread_title or tid
                    if tid:
                        gcs.append({"id": tid, "name": name})
            log.info(f"✅ @{self.username}: {len(gcs)} GCs found")
        except LoginRequired:
            log.warning(f"⚠️  @{self.username}: GC scan blocked — try again later")
        except Exception as e:
            log.warning(f"⚠️  discover_gcs @{self.username}: {e}")
        return gcs

    async def auto_detect_gc(self, limit: int = 20) -> Optional[dict]:
        """
        Auto-detect the most recently active group chat.
        Priority: 1. last_permanent thread  2. last known GC in memory
        """
        try:
            inbox = await self._fetch_inbox_url(
                f"{_IG_API}/direct_v2/inbox/?limit={limit}",
                "inbox"
            )
            for thread in inbox:
                if thread.get("is_group") or len(thread.get("users", [])) > 1:
                    return {
                        "id":   thread["thread_id"],
                        "name": thread.get("thread_title", thread["thread_id"]),
                    }
        except Exception as e:
            log.debug(f"auto_detect_gc inbox @{self.username}: {e}")

        # Fallback: instagrapi threads
        try:
            loop    = asyncio.get_running_loop()
            threads = await loop.run_in_executor(
                _POOL, lambda: self._cl.direct_threads(amount=limit))
            for t in threads:
                if t.is_group or len(t.users) > 1:
                    return {"id": str(t.id), "name": t.thread_title or str(t.id)}
        except Exception as e:
            log.debug(f"auto_detect_gc fallback @{self.username}: {e}")

        return None

# ─────────────────────────────────────────────────────────────────────────────
# SEND QUEUE — per-account, 10+ workers, fully async, non-blocking
# ─────────────────────────────────────────────────────────────────────────────
class SendQueue:
    _MIN_WORKERS = 10
    _MAX_WORKERS = 512

    def __init__(self, cl: IGClient, eng: Engine, workers: int = 64):
        self._cl       = cl
        self._eng      = eng
        self._q:       asyncio.Queue = asyncio.Queue(maxsize=100000)
        self._workers  = max(self._MIN_WORKERS, min(workers, self._MAX_WORKERS))
        self._tasks:   List[asyncio.Task] = []
        self._scaler:  Optional[asyncio.Task] = None
        self._running  = False
        self._total_sent   = 0
        self._total_errors = 0

    async def start(self):
        self._running = True
        for _ in range(self._workers):
            t = asyncio.create_task(self._worker())
            self._tasks.append(t)
        self._scaler = asyncio.create_task(self._auto_scale())
        METRICS.workers_total = self._workers

    async def stop(self):
        self._running = False
        if self._scaler:
            self._scaler.cancel()
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def push(self, tid: str, text: str):
        try:
            self._q.put_nowait((tid, text))
            METRICS.queue_size = self._q.qsize()
        except asyncio.QueueFull:
            pass

    def error_rate(self) -> float:
        total = self._total_sent + self._total_errors
        if total == 0:
            return 0.0
        return self._total_errors / total

    async def _worker(self):
        while self._running:
            try:
                tid, text = await asyncio.wait_for(self._q.get(), timeout=1.0)
                METRICS.workers_active += 1
                METRICS.queue_size = self._q.qsize()
                ok = await self._cl.send(tid, text)
                if ok:
                    self._eng.inc("msgs")
                    METRICS.record_send(1)
                    self._total_sent += 1
                else:
                    self._eng.inc("errors")
                    METRICS.errors_total += 1
                    self._total_errors += 1
                METRICS.workers_active = max(0, METRICS.workers_active - 1)
                self._q.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.debug(f"Worker error: {e}")
                METRICS.workers_active = max(0, METRICS.workers_active - 1)

    async def _auto_scale(self):
        while self._running:
            try:
                await asyncio.sleep(5)
                # Auto slow down if error rate > 30%
                if self.error_rate() > 0.30:
                    log.warning(f"⚠️  @{self._cl.username} error rate > 30% — slowing down")
                    await asyncio.sleep(10)
                    continue

                qsize = self._q.qsize()
                alive = sum(1 for t in self._tasks if not t.done())
                target = alive
                if qsize > alive * 50 and alive < self._MAX_WORKERS:
                    target = min(alive + 32, self._MAX_WORKERS)
                elif qsize < alive * 5 and alive > self._MIN_WORKERS:
                    target = max(alive - 8, self._MIN_WORKERS)
                if target > alive:
                    for _ in range(target - alive):
                        t = asyncio.create_task(self._worker())
                        self._tasks.append(t)
                    METRICS.workers_total = target
            except asyncio.CancelledError:
                break
            except Exception:
                pass

# ─────────────────────────────────────────────────────────────────────────────
# TASK REGISTRY
# ─────────────────────────────────────────────────────────────────────────────
class TaskReg:
    def __init__(self):
        self._t: Dict[str, asyncio.Task] = {}
        self._l: Dict[str, str]          = {}

    def add(self, task: asyncio.Task, label: str) -> str:
        i = oid()
        self._t[i] = task
        self._l[i] = label
        return i

    def stop(self, i: str):
        if i in self._t and not self._t[i].done():
            self._t[i].cancel()

    def stop_key(self, key: str):
        for i, l in list(self._l.items()):
            if l == key: self.stop(i)

    def stop_all(self):
        for t in self._t.values():
            if not t.done(): t.cancel()

    def list(self) -> List[Tuple[str, str]]:
        dead = [k for k, t in self._t.items() if t.done()]
        for k in dead:
            self._t.pop(k, None)
            self._l.pop(k, None)
        return list(self._l.items())

    def count(self) -> int:
        return sum(1 for t in self._t.values() if not t.done())

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL TASK CONTROLLER — centralized stop-event management for every task
# ─────────────────────────────────────────────────────────────────────────────
class TaskController:
    """
    Central registry for all long-running asyncio tasks.
    Every task gets its own asyncio.Event so /stop is guaranteed.
    """

    def __init__(self):
        self._lock   = threading.Lock()
        self._events: Dict[str, asyncio.Event] = {}
        self._tasks:  Dict[str, asyncio.Task]  = {}

    def start(self, task_id: str, coro,
              stop_event: Optional[asyncio.Event] = None) -> Tuple[asyncio.Event, asyncio.Task]:
        """Create a task with a dedicated stop_event. Returns (event, task)."""
        ev   = stop_event or asyncio.Event()
        task = asyncio.create_task(coro)
        with self._lock:
            self._events[task_id] = ev
            self._tasks[task_id]  = task
        task.add_done_callback(lambda _: self._cleanup(task_id))
        return ev, task

    def _cleanup(self, task_id: str):
        with self._lock:
            self._events.pop(task_id, None)
            self._tasks.pop(task_id, None)

    def stop(self, task_id: str):
        with self._lock:
            ev   = self._events.get(task_id)
            task = self._tasks.get(task_id)
        if ev:
            ev.set()
        if task and not task.done():
            task.cancel()

    def stop_prefix(self, prefix: str):
        """Stop all tasks whose ID starts with prefix."""
        with self._lock:
            ids = [tid for tid in self._tasks if tid.startswith(prefix)]
        for tid in ids:
            self.stop(tid)

    def stop_all(self):
        with self._lock:
            evs   = list(self._events.values())
            tasks = list(self._tasks.values())
        for ev in evs:
            ev.set()
        for t in tasks:
            if not t.done():
                t.cancel()

    def get_event(self, task_id: str) -> Optional[asyncio.Event]:
        return self._events.get(task_id)

    def list_active(self) -> List[str]:
        with self._lock:
            return [tid for tid, t in self._tasks.items() if not t.done()]

    def count(self) -> int:
        with self._lock:
            return sum(1 for t in self._tasks.values() if not t.done())


TASK_CTRL = TaskController()   # global singleton

# ─────────────────────────────────────────────────────────────────────────────
# WORKERS
# ─────────────────────────────────────────────────────────────────────────────
async def worker_spam(eng: Engine, cl: IGClient,
                      gcs: list, custom: Optional[str] = None,
                      sq: Optional[SendQueue] = None):
    pool  = eng.cfg.get("emoji_pool", ["⚡"])
    burst = max(1, eng.cfg.get("burst_size", 64))
    loop  = asyncio.get_running_loop()
    dmin  = eng.cfg.get("spam_delay_min", 0.0)
    dmax  = eng.cfg.get("spam_delay_max", 0.0)

    while True:
        try:
            tasks = []
            for gc in gcs:
                gc_name = gc.get("name", "GC")
                gc_id   = gc["id"]
                try:
                    msgs: List[str] = await loop.run_in_executor(
                        _CPU_POOL, _cpu_batch_messages,
                        SPAM_TEMPLATES, pool, gc_name, burst, custom)
                except Exception:
                    msgs = []
                    for _ in range(burst):
                        em = rand_emoji(pool)
                        msgs.append(
                            fmt(custom, name=gc_name, emoji=em) if custom else
                            fmt(random.choice(SPAM_TEMPLATES), name=gc_name, emoji=em)
                        )
                for msg in msgs:
                    if sq:
                        tasks.append(sq.push(gc_id, msg))
                    else:
                        tasks.append(cl.send(gc_id, msg))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            if not sq:
                sent = sum(1 for r in results if r is True)
                eng.inc("msgs", sent)
                METRICS.record_send(sent)
            if dmax > 0:
                await asyncio.sleep(random.uniform(dmin, dmax))
            else:
                await asyncio.sleep(0)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.debug(f"worker_spam: {e}")
            await asyncio.sleep(1.0)


async def worker_godspam(eng: Engine, cl: IGClient,
                         tid: str, gc_name: str,
                         custom: Optional[str] = None,
                         sq: Optional[SendQueue] = None):
    pool  = eng.cfg.get("emoji_pool", ["⚡"])
    burst = max(1, eng.cfg.get("burst_size", 64))
    loop  = asyncio.get_running_loop()

    while True:
        try:
            try:
                msgs: List[str] = await loop.run_in_executor(
                    _CPU_POOL, _cpu_batch_messages,
                    SPAM_TEMPLATES, pool, gc_name, burst, custom)
            except Exception:
                msgs = [
                    fmt(custom or random.choice(SPAM_TEMPLATES),
                        name=gc_name, emoji=rand_emoji(pool))
                    for _ in range(burst)
                ]
            tasks = [
                sq.push(tid, msg) if sq else cl.send(tid, msg)
                for msg in msgs
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            if not sq:
                sent = sum(1 for r in results if r is True)
                eng.inc("msgs", sent)
                METRICS.record_send(sent)
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.debug(f"worker_godspam: {e}")
            await asyncio.sleep(1.0)


# ─────────────────────────────────────────────────────────────────────────────
# STEADYNC V2 — single loop, zero-jitter, all NC commands use this
# ─────────────────────────────────────────────────────────────────────────────
async def steady_nc(
    cl: "IGClient",
    gc_id: str,
    names: List[str],
    pool: list,
    stop_event: asyncio.Event,
    delay: float = 0.01,
    use_gcnc: bool = True,
    eng: Optional["Engine"] = None,
):
    """
    SteadyNC V2: single clean loop, no jitter, no nested loops.
    use_gcnc=True  → change GC name (group chat)
    use_gcnc=False → change own username/display name
    """
    i = 0
    while not stop_event.is_set():
        try:
            em   = rand_emoji(pool)
            name = names[i % len(names)]
            styled = fmt(name, text=name, emoji=em)
            if use_gcnc:
                ok = await cl.change_gc_name(gc_id, styled)
            else:
                ok = await cl.change_name(styled)
            if ok and eng:
                eng.inc("nc")
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        i += 1
        await asyncio.sleep(delay)


async def worker_nc(eng: Engine, cl: IGClient, names: Optional[List[str]] = None):
    """Legacy wrapper — uses SteadyNC V2 internally."""
    pool  = eng.cfg.get("emoji_pool", ["⚡"])
    delay = max(0.01, eng.cfg.get("nc_delay", 0.5))
    base  = eng.cfg.get("base_name", "NIGGA SYSTEM")
    name_list = names if names else [
        fmt(tpl, text=base, emoji=rand_emoji(pool)) for tpl in NC_TEXT
    ]
    stop_event = asyncio.Event()
    tid_key = f"nc:{cl.username}:{id(stop_event)}"
    TASK_CTRL._events[tid_key] = stop_event
    try:
        await steady_nc(cl, "", name_list, pool, stop_event,
                        delay=delay, use_gcnc=False, eng=eng)
    finally:
        TASK_CTRL._events.pop(tid_key, None)


async def worker_gcnc(eng: Engine, cl: IGClient,
                      tid: str, gc_name: str,
                      names: Optional[List[str]] = None):
    """Legacy wrapper — uses SteadyNC V2 internally."""
    pool  = eng.cfg.get("emoji_pool", ["⚡"])
    delay = max(0.01, eng.cfg.get("nc_delay", 0.5))
    name_list = names if names else [
        fmt(tpl, text=gc_name, emoji=rand_emoji(pool)) for tpl in GCNC_TEXT
    ]
    stop_event = asyncio.Event()
    tid_key = f"gcnc:{cl.username}:{tid}:{id(stop_event)}"
    TASK_CTRL._events[tid_key] = stop_event
    try:
        await steady_nc(cl, tid, name_list, pool, stop_event,
                        delay=delay, use_gcnc=True, eng=eng)
    finally:
        TASK_CTRL._events.pop(tid_key, None)


# ─────────────────────────────────────────────────────────────────────────────
# WORKER SASNC — ultra-fast 0.005s stylish NC (+sasnc command)
# ─────────────────────────────────────────────────────────────────────────────
_SASNC_STYLES = [
    "꧁{text}꧂ {emoji}",
    "〔{text}〕⚡ {emoji}",
    "❰{text}❱ {emoji}",
    "「{text}」 {emoji}",
    "★{text}★ {emoji}",
    "【{text}】 {emoji}",
    "⚔️{text}⚔️ {emoji}",
    "🔥{text}🔥 {emoji}",
    "〖{text}〗👑 {emoji}",
    "💀{text}💀 {emoji}",
]

async def worker_sasnc(cl: "IGClient", gc_id: str, text: str,
                       pool: list, stop_event: asyncio.Event,
                       eng: Optional["Engine"] = None):
    """
    +sasnc: ultra-fast GC name changer at 0.005s loop.
    Cycles through stylish Unicode symbol wrappers.
    """
    i = 0
    while not stop_event.is_set():
        try:
            em    = rand_emoji(pool)
            style = _SASNC_STYLES[i % len(_SASNC_STYLES)]
            name  = fmt(style, text=text, emoji=em)
            ok    = await cl.change_gc_name(gc_id, name)
            if ok and eng:
                eng.inc("nc")
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        i += 1
        await asyncio.sleep(0.005)


async def worker_pic(eng: Engine, cl: IGClient, gcs: list):
    url      = eng.cfg.get("pic_spam_url", "")
    img_path = Path("spam_pic.jpg")
    if not img_path.exists() and HAS_REQUESTS and url:
        try: img_path.write_bytes(_req.get(url, timeout=10).content)
        except Exception as e: log.error(f"Img download: {e}")
    if not img_path.exists():
        try:
            from PIL import Image, ImageDraw
            im = Image.new("RGB", (500, 300), (10, 10, 10))
            ImageDraw.Draw(im).text((50, 130), "NIGGA SYSTEM v7.0", fill=(255, 255, 255))
            im.save(str(img_path))
        except Exception:
            log.warning("No spam_pic.jpg found — create it manually.")
            return
    while True:
        tasks = [cl.send_photo(gc["id"], img_path) for gc in gcs]
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            eng.inc("msgs", sum(1 for r in results if r is True))
        except asyncio.CancelledError:
            raise
        except Exception:
            eng.inc("errors")
        await asyncio.sleep(0)

# ─────────────────────────────────────────────────────────────────────────────
# SMART SPAM WORKER — parallel GCs, multi-account, smart rate limit bypass
# ─────────────────────────────────────────────────────────────────────────────
async def worker_smartspam(
    eng: Engine,
    gcs: list,
    speed: str = "medium",
    custom: Optional[str] = None,
    burst_count: int = 2,
):
    """
    Ultra-stable parallel GC spam with round-robin accounts,
    smart cooldown, retry, playwright fallback, and auto error slowdown.
    """
    pool        = eng.cfg.get("emoji_pool", ["⚡"])
    dmin, dmax  = SPEED_MODES.get(speed, (1.0, 2.0))
    max_parallel = SPEED_PARALLEL.get(speed, 6)
    cooldown_sec = eng.cfg.get("gc_cooldown_sec", 30)
    gc_errors: Dict[str, int] = {gc["id"]: 0 for gc in gcs}

    async def _send_to_gc(gc: dict, cl: IGClient):
        gid  = gc["id"]
        gname = gc.get("name", "GC")

        if eng.is_gc_on_cooldown(gid):
            log.debug(f"GC {gid} on cooldown — skipping")
            return

        for b in range(burst_count):
            em  = rand_emoji(pool)
            if custom:
                text = fmt(custom, name=gname, emoji=em)
            else:
                text = fmt(random.choice(SPAM_TEMPLATES), name=gname, emoji=em)

            # Micro delay between burst messages
            if b > 0:
                await asyncio.sleep(random.uniform(0.1, 0.3))

            ok = False
            # Try API first, then playwright
            for attempt in range(3):
                ok = await cl.send(gid, text)
                if ok:
                    gc_errors[gid] = max(0, gc_errors[gid] - 1)
                    eng.update_last_active_gc(cl.username, gc)
                    break
                # Retry
                if attempt < 2:
                    ACCOUNT_MANAGER.mark_error(cl.username)
                    next_cl = ACCOUNT_MANAGER.get_next(exclude=cl.username)
                    if next_cl:
                        log.info(f"⚠ switched account @{cl.username} → @{next_cl.username}")
                        cl = next_cl
                    await asyncio.sleep(1.0)

            if not ok:
                gc_errors[gid] = gc_errors.get(gid, 0) + 1
                log.info(f"❌ failed GC {gid[:12]}… (err={gc_errors[gid]})")
                if gc_errors[gid] >= 3:
                    eng.set_gc_cooldown(gid, cooldown_sec)
                    log.info(f"⚠ GC {gid[:12]}… cooldown {cooldown_sec}s")

    while True:
        try:
            # Get active GCs that aren't on cooldown
            active_gcs = [g for g in gcs if not eng.is_gc_on_cooldown(g["id"])]
            if not active_gcs:
                log.debug("All GCs on cooldown — waiting 10s")
                await asyncio.sleep(10)
                continue

            # Split GCs into parallel batches
            batches = [active_gcs[i:i+max_parallel]
                       for i in range(0, len(active_gcs), max_parallel)]

            for batch in batches:
                clients = ACCOUNT_MANAGER.list_active()
                if not clients:
                    await asyncio.sleep(5)
                    break

                # Assign GCs to accounts round-robin
                tasks = []
                for i, gc in enumerate(batch):
                    cl = clients[i % len(clients)]
                    tasks.append(_send_to_gc(gc, cl))

                await asyncio.gather(*tasks, return_exceptions=True)

                # Smart delay between batches
                delay = random.uniform(dmin, dmax) + random.uniform(-0.3, 0.3)
                await asyncio.sleep(max(0.1, delay))

        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.debug(f"worker_smartspam: {e}")
            await asyncio.sleep(2.0)

# ─────────────────────────────────────────────────────────────────────────────
# PLAYWRIGHT SPAM WORKER — /pwspam command
# ─────────────────────────────────────────────────────────────────────────────
async def worker_pwspam(
    eng: Engine,
    gcs: list,
    speed: str = "medium",
    custom: Optional[str] = None,
):
    """
    Send messages via Playwright browser in human-sim mode.
    Runs fully in background, non-blocking.
    """
    if not HAS_PLAYWRIGHT:
        log.warning("⚠️  Playwright not installed — /pwspam unavailable")
        return
    if not _PW_ENGINE._ready:
        await _PW_ENGINE.start()

    pool       = eng.cfg.get("emoji_pool", ["⚡"])
    dmin, dmax = SPEED_MODES.get(speed, (1.0, 2.0))
    typing_speed = {"slow": 60, "medium": 40, "fast": 20}.get(speed, 40)

    clients = ACCOUNT_MANAGER.list_active()
    if not clients:
        log.warning("⚠️  No active accounts for pwspam")
        return

    # Assign GCs to accounts round-robin
    gc_account: Dict[str, "IGClient"] = {}
    for i, gc in enumerate(gcs):
        gc_account[gc["id"]] = clients[i % len(clients)]

    while True:
        try:
            tasks = []
            for gc in gcs:
                gid   = gc["id"]
                gname = gc.get("name", "GC")
                cl    = gc_account.get(gid) or clients[0]

                if not cl._sessionid:
                    continue

                em   = rand_emoji(pool)
                text = fmt(custom or random.choice(SPAM_TEMPLATES), name=gname, emoji=em)

                async def _pw_send(gid=gid, text=text, cl=cl):
                    ok = await _PW_ENGINE.send_message_human(
                        cl.username, gid, text, cl._sessionid,
                        typing_delay_ms=typing_speed)
                    if ok:
                        METRICS.playwright_sends += 1
                        eng.inc("msgs")
                    else:
                        # Fallback: switch account
                        next_cl = ACCOUNT_MANAGER.get_next(exclude=cl.username)
                        if next_cl and next_cl._sessionid:
                            log.info(f"🔄 switched account @{cl.username} → @{next_cl.username}")
                            ok2 = await _PW_ENGINE.send_message_human(
                                next_cl.username, gid, text, next_cl._sessionid,
                                typing_delay_ms=typing_speed)
                            if ok2:
                                eng.inc("msgs")
                                METRICS.playwright_sends += 1
                            else:
                                log.info(f"❌ failed pwspam GC {gid[:12]}…")

                tasks.append(_pw_send())

            await asyncio.gather(*tasks, return_exceptions=True)

            delay = random.uniform(dmin, dmax)
            await asyncio.sleep(delay)

        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.debug(f"worker_pwspam: {e}")
            await asyncio.sleep(2.0)


# ─────────────────────────────────────────────────────────────────────────────
# /pwgo WORKER — TRUE ULTRA ENGINE (UPGRADED from V2 → V3)
# Now uses UltraPlaywrightSpamEngine: 3-5 tabs/GC, burst=3, 0.01s, round-robin
# ─────────────────────────────────────────────────────────────────────────────
async def worker_pwgo(
    eng: Engine,
    urls,
    text: str,
    user_key: str,
    engine_count: int = 4,
    tabs_per_gc: int = 4,
    burst: int = 3,
):
    """
    TRUE ULTRA ENGINE — V3.
    Launches engine_count UltraPlaywrightSpamEngine instances in parallel.
    Each engine: tabs_per_gc tabs per GC URL, burst msgs per tab per cycle.
    Multi-account round-robin per tab. Auto speed adjust by fail rate.
    Zero-jitter: 0.01s delay between cycles.
    urls: str (single GC URL) or list[str] (multi-GC multi-tab).
    Stop with /stopgo.
    """
    if not HAS_PLAYWRIGHT:
        log.warning("⚠️  Playwright not installed — /pwgo unavailable")
        return

    clients = ACCOUNT_MANAGER.list_active()
    if not clients:
        log.warning("⚠️  No active IG accounts for /pwgo")
        return

    url_list   = urls if isinstance(urls, list) else [urls]
    stop_event = asyncio.Event()

    async with _PWGO_LOCK:
        _ACTIVE_PWGO[user_key] = (stop_event, [])

    tasks = []
    for i in range(engine_count):
        engine = UltraPlaywrightSpamEngine(
            engine_id=i + 1,
            urls=url_list,
            tabs_per_gc=tabs_per_gc,
            burst=burst,
        )
        task = asyncio.create_task(engine.run(text, stop_event, eng))
        tasks.append(task)

    async with _PWGO_LOCK:
        _ACTIVE_PWGO[user_key] = (stop_event, tasks)

    total_tabs = engine_count * tabs_per_gc * len(url_list)
    log.info(
        f"🔥 ULTRA /pwgo launched {len(tasks)} engines "
        f"x {tabs_per_gc} tabs/GC x {len(url_list)} GCs "
        f"= {total_tabs} total tabs | burst={burst} | key={user_key}"
    )

    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        stop_event.set()
        raise
    finally:
        async with _PWGO_LOCK:
            _ACTIVE_PWGO.pop(user_key, None)
        log.info(f"🛑 ULTRA /pwgo stopped | key={user_key}")


async def stop_pwgo(user_key: str) -> bool:
    """Set the stop_event for a running /pwgo session. Returns True if found."""
    async with _PWGO_LOCK:
        entry = _ACTIVE_PWGO.get(user_key)
        if not entry:
            return False
        ev, tasks = entry
        ev.set()
        for t in tasks:
            t.cancel()
        return True

# ─────────────────────────────────────────────────────────────────────────────
# VOICE HELPER
# ─────────────────────────────────────────────────────────────────────────────
def _gen_voice(text: str, vk: str) -> Optional[Path]:
    voice = VOICE_MAP.get(vk, VOICE_MAP["default"])
    out   = Path(f"voice_{vk}.mp3")
    if HAS_EDGE_TTS:
        async def _run():
            await edge_tts.Communicate(text, voice).save(str(out))
        try:
            lp = asyncio.new_event_loop()
            try:
                lp.run_until_complete(_run())
            finally:
                lp.close()
            return out
        except Exception as e: log.error(f"edge-tts: {e}")
    if HAS_GTTS:
        try: gTTS(text=text, lang="en").save(str(out)); return out
        except Exception as e: log.error(f"gTTS: {e}")
    return None

# ─────────────────────────────────────────────────────────────────────────────
# TARGET RESOLVER
# ─────────────────────────────────────────────────────────────────────────────
def resolve(eng: Engine, user: str, target: str) -> list:
    gcs   = eng.get_gcs(user)
    by_id = {g["id"]: g for g in gcs}
    by_nm = {g["name"].lower(): g for g in gcs}
    s     = target.strip().lower()
    if s == "all":
        return gcs
    if target.startswith("@"):
        ids = eng.gc_groups.get(target[1:].lower(), [])
        return [by_id[i] for i in ids if i in by_id]
    res = []
    for tok in target.split(","):
        tok = tok.strip()
        if tok in by_id:           res.append(by_id[tok])
        elif tok.lower() in by_nm: res.append(by_nm[tok.lower()])
    return res

# ─────────────────────────────────────────────────────────────────────────────
# COMMAND HANDLER
# ─────────────────────────────────────────────────────────────────────────────
class CmdHandler:
    def __init__(self, eng: Engine, cl: IGClient, reg: TaskReg,
                 regs: dict, sq: Optional[SendQueue] = None):
        self.eng  = eng
        self.cl   = cl
        self.reg  = reg
        self.regs = regs
        self.sq   = sq

    async def reply(self, tid: str, text: str):
        try: await self.cl.send(tid, text)
        except Exception as e: log.error(f"Reply: {e}")

    async def run(self, tid: str, raw: str, sender: str = ""):
        parts = raw.strip().split()
        if not parts or not parts[0].startswith("/"): return
        cmd, args = parts[0].lower(), parts[1:]

        # ── ACCESS CONTROL ────────────────────────────────────────────────────
        cfg    = self.eng.cfg
        owner  = _normalize_username(cfg.get("owner_username", ""))
        sender = _normalize_username(sender)

        # Owner-only commands
        owner_only = {"/allow", "/remove", "/allowed", "/authenticate"}
        # Spam commands can run from GC but only from authorized users
        authorized = is_authorized(cfg, sender) if sender else True

        if not authorized:
            log.info(f"⚠ unauthorized attempt ({sender})")
            return  # Silent ignore

        if cmd in owner_only and not is_owner(cfg, sender) and sender:
            return  # Silent ignore for owner-only from non-owner

        fn = {
            "/help":          self._help,
            "/authenticate":  self._auth,
            "/allow":         self._allow,
            "/remove":        self._remove_user,
            "/allowed":       self._list_allowed,
            "/owner":         self._owner,
            "/stats":         self._stats,
            "/proxystats":    self._proxystats,
            "/login":         self._login,
            "/logout":        self._logout,
            "/accounts":      self._accounts,
            "/scangcs":       self._scangcs,
            "/listgcs":       self._listgcs,
            "/addgc":         self._addgc,
            "/switchgc":      self._switchgc,
            "/addgroup":      self._addgroup,
            "/listgroups":    self._listgroups,
            "/gcaddbots":     self._gcaddbots,
            "/gcadd":         self._gcadd,
            "/raid":          self._raid,
            "/smartspam":     self._smartspam,
            "/pwspam":        self._pwspam,
            "/pwgo":          self._pwgo_cmd,
            "/stopgo":        self._stopgo_cmd,
            "/multispam":     self._multispam,
            "/multinc":       self._multinc,
            "/multipicspam":  self._multipicspam,
            "/stopmulti":     self._stopmulti,
            "/listmulti":     self._listmulti,
            "/startnc":       self._startnc,
            "/stopnc":        self._stopnc,
            "/spam":          self._spam_local,
            "/gcnc":          self._gcnc_local,
            "/godspam":       self._godspam_local,
            "/picspam":       self._picspam_local,
            "/stop":          self._stop_local,
            "/sasnc":         self._sasnc_cmd,
            "+sasnc":         self._sasnc_cmd,
            "/stopsasnc":     self._stopsasnc_cmd,
            "/loginuser":     self._loginuser_cmd,
            "/creategc":      self._creategc_cmd,
            "/addbot":        self._addbot_cmd,
            "/promotebots":   self._promotebots_cmd,
            "/startgcnc":     self._startgcnc,
            "/stopgcnc":      self._stopgcnc,
            "/loginsession":  self._loginsession,
            "/startspam":     self._startspam,
            "/stopspam":      self._stopspam,
            "/gspam":         self._gspam,
            "/gstop":         self._gstop,
            "/stopgodspam":   self._stopgodspam,
            "/startpicspam":  self._startpicspam,
            "/stoppicspam":   self._stoppicspam,
            "/animevoice":    self._voice,
            "/search":        self._search,
            "/setdelay":      self._setdelay,
            "/setncdelay":    self._setncdelay,
        }.get(cmd)

        if fn:
            log.info(f"✔ command executed ({sender}): {cmd}")
            try: await fn(tid, args)
            except asyncio.CancelledError: raise
            except Exception as e:
                await self.reply(tid, f"❌ {cmd}: {e}")
                log.error(f"CMD {cmd}: {e}", exc_info=True)
        # Silently ignore unknown commands from unauthorized

    def _agc(self) -> Optional[dict]:
        return self.eng.active_gc.get(self.cl.username)

    # ── help / info ───────────────────────────────────────────────────────────
    async def _help(self, tid, _):   await self.reply(tid, HELP_MSG)

    async def _auth(self, tid, args):
        if not args:
            await self.reply(tid, "Usage: /authenticate @username"); return
        t = _normalize_username(args[0])
        if not self.eng.cfg.get("owner_username"):
            self.eng.cfg["owner_username"] = t
            save_cfg(self.eng.cfg)
            await self.reply(tid, f"✅ Owner set to @{t}")
        elif _normalize_username(self.eng.cfg["owner_username"]) == t:
            await self.reply(tid, f"✅ Already owner: @{t}")
        else:
            await self.reply(tid, "❌ Owner already set. Edit config.json")

    # ── access control ────────────────────────────────────────────────────────
    async def _allow(self, tid, args):
        if not args:
            await self.reply(tid, "Usage: /allow @username"); return
        uname = _normalize_username(args[0])
        allowed = self.eng.cfg.setdefault("allowed_users", [])
        normalized = [_normalize_username(u) for u in allowed]
        if uname in normalized:
            await self.reply(tid, f"⚠️  @{uname} already allowed."); return
        allowed.append(uname)
        save_cfg(self.eng.cfg)
        await self.reply(tid, f"✅ @{uname} added to allowed users.")

    async def _remove_user(self, tid, args):
        if not args:
            await self.reply(tid, "Usage: /remove @username"); return
        uname = _normalize_username(args[0])
        allowed = self.eng.cfg.get("allowed_users", [])
        new_list = [u for u in allowed if _normalize_username(u) != uname]
        if len(new_list) == len(allowed):
            await self.reply(tid, f"❌ @{uname} not found in allowed list."); return
        self.eng.cfg["allowed_users"] = new_list
        save_cfg(self.eng.cfg)
        await self.reply(tid, f"✅ @{uname} removed from allowed users.")

    async def _list_allowed(self, tid, _):
        owner   = self.eng.cfg.get("owner_username", "<not set>")
        allowed = self.eng.cfg.get("allowed_users", [])
        lines   = [f"👑 Owner: @{owner}", f"📋 Allowed users ({len(allowed)}):"]
        for u in allowed:
            lines.append(f"  • @{u}")
        if not allowed:
            lines.append("  (none)")
        await self.reply(tid, "\n".join(lines))

    async def _owner(self, tid, _):
        o = self.eng.cfg.get("owner_username") or "<not set>"
        m = METRICS.snapshot()
        await self.reply(tid,
            f"👑 Owner: @{o}\n"
            f"⏱ {uptime()}\n"
            f"{self.eng.stats_str()}\n"
            f"📈 {m['msgs_per_sec']}/s | q={m['queue_size']} | "
            f"w={m['workers_active']}/{m['workers_total']}\n"
            f"🌐 Proxies: {len(self.eng.proxy_rotator)} | "
            f"PW:{m['playwright_sends']}\n"
            f"🔧 uvloop={HAS_UVLOOP} aiohttp={HAS_AIOHTTP} "
            f"playwright={HAS_PLAYWRIGHT}")

    async def _stats(self, tid, _):
        m = METRICS.snapshot()
        cpu = f"cpu={m['cpu_percent']}%" if m["cpu_percent"] is not None else ""
        mem = f"mem={m['mem_percent']}%" if m["mem_percent"] is not None else ""
        await self.reply(tid,
            f"📊 NIGGA SYSTEM v7.0\n"
            f"⏱ Uptime: {uptime()}\n"
            f"🔥 Active ops: {self.reg.count()}\n"
            f"📡 Clients: {len(self.eng._clients)}\n"
            f"🌐 Proxies: {len(self.eng.proxy_rotator)}\n"
            f"{self.eng.stats_str()}\n"
            f"━━━━━━━━━━━━━\n"
            f"📈 Msgs/sec   : {m['msgs_per_sec']}\n"
            f"📦 Queue      : {m['queue_size']}\n"
            f"⚙️  Workers   : {m['workers_active']}/{m['workers_total']} ({m['worker_utilization']})\n"
            f"❌ Errors     : {m['errors_total']}\n"
            f"🎭 Playwright : {m['playwright_sends']}\n"
            f"🔀 Proxy swaps: {m['proxy_switches']}\n"
            f"🖥  {cpu} {mem}")

    async def _proxystats(self, tid, _):
        stats = self.eng.proxy_rotator.get_stats()
        lines = [
            f"🌐 Proxy Pool: {stats['total']} total | {stats['on_cooldown']} on cooldown",
            "━━━━━━━━━━━━━━━━━━",
        ]
        for p, s in list(stats["by_proxy"].items())[:8]:
            lines.append(f"  {p[:30]}…  ✅{s['ok']} ❌{s['fail']}")
        await self.reply(tid, "\n".join(lines))

    # ── login / logout ────────────────────────────────────────────────────────
    async def _login(self, tid, args):
        if len(args) < 2:
            await self.reply(tid, "Usage: /login <username> <password>"); return
        uname, passwd = args[0], args[1]
        if self.eng.get_client(uname):
            await self.reply(tid, f"⚠️  @{uname} is already logged in."); return
        await self.reply(tid, f"🔐 Logging in @{uname}… please wait.")
        acct = {"username": uname, "password": passwd, "enabled": True}
        loop = asyncio.get_running_loop()
        ok = await loop.run_in_executor(_POOL, lambda: self.eng.add_account_thread(acct, self.regs))
        await self.reply(tid, f"✅ @{uname} login started." if ok else f"❌ Failed to start @{uname}.")

    async def _logout(self, tid, args):
        if not args:
            await self.reply(tid, "Usage: /logout <username>"); return
        uname = args[0].lstrip("@")
        ok = self.eng.remove_account(uname)
        await self.reply(tid, f"✅ @{uname} removed." if ok else f"❌ @{uname} not found.")

    async def _loginsession(self, tid, args):
        if len(args) < 2:
            await self.reply(tid, "Usage: /loginsession <username> <sessionid>"); return
        uname, sessionid = args[0].lstrip("@"), args[1]
        if self.eng.get_client(uname):
            await self.reply(tid, f"⚠️  @{uname} already logged in."); return
        await self.reply(tid, f"🔑 Validating sessionid for @{uname}…")
        acct = {"username": uname, "password": "", "sessionid": sessionid, "enabled": True}
        loop = asyncio.get_running_loop()
        ok = await loop.run_in_executor(_POOL, lambda: self.eng.add_account_thread(acct, self.regs))
        await self.reply(tid, f"✅ @{uname} sessionid login started." if ok else f"❌ Failed @{uname}.")

    async def _accounts(self, tid, _):
        users = self.eng.list_usernames()
        if not users:
            await self.reply(tid, "❌ No accounts active."); return
        lines = [f"📡 Active accounts ({len(users)}):"]
        for u in users:
            lines.append(f"  • @{u}")
        await self.reply(tid, "\n".join(lines))

    # ── GC management ─────────────────────────────────────────────────────────
    async def _scangcs(self, tid, _):
        await self.reply(tid, "🔍 Scanning… please wait.")
        gcs = await self.cl.discover_gcs(self.eng.cfg.get("max_gcs", 200))
        self.eng.set_gcs(self.cl.username, gcs)
        await self.reply(tid, f"✅ Found {len(gcs)} GCs.")

    async def _listgcs(self, tid, _):
        gcs = self.eng.get_gcs(self.cl.username)
        if not gcs:
            await self.reply(tid, "❌ No GCs — run /scangcs first."); return
        act   = self.eng.active_gc.get(self.cl.username) or {}
        lines = [f"📋 GCs ({len(gcs)}):"]
        for i, g in enumerate(gcs[:50], 1):
            m = " ◀ ACTIVE" if g["id"] == act.get("id") else ""
            lines.append(f"  {i}. {g['name']} [{g['id'][:10]}…]{m}")
        if len(gcs) > 50:
            lines.append(f"  …and {len(gcs)-50} more")
        await self.reply(tid, "\n".join(lines))

    async def _addgc(self, tid, args):
        if not args:
            await self.reply(tid, "Usage: /addgc <id> [name]"); return
        gid  = args[0]
        name = " ".join(args[1:]) if len(args) > 1 else gid
        gcs  = self.eng.get_gcs(self.cl.username)
        if any(g["id"] == gid for g in gcs):
            await self.reply(tid, f"⚠️  Already exists: {gid}"); return
        gcs.append({"id": gid, "name": name})
        self.eng.set_gcs(self.cl.username, gcs)
        await self.reply(tid, f"✅ Added '{name}'")

    async def _switchgc(self, tid, args):
        if not args:
            await self.reply(tid, "Usage: /switchgc <id|name>"); return
        q   = " ".join(args).lower()
        gcs = self.eng.get_gcs(self.cl.username)
        m   = next((g for g in gcs
                    if g["id"].startswith(q) or g["name"].lower().startswith(q)), None)
        if not m:
            await self.reply(tid, f"❌ Not found: {q}"); return
        self.eng.active_gc[self.cl.username] = m
        await self.reply(tid, f"✅ Active GC → '{m['name']}'")

    async def _addgroup(self, tid, args):
        if len(args) < 2:
            await self.reply(tid, "Usage: /addgroup <name> <id1,id2,...>"); return
        gname = args[0].lower()
        ids   = [x.strip() for x in " ".join(args[1:]).split(",") if x.strip()]
        self.eng.gc_groups[gname] = ids
        self.eng.save_gcgroups()
        await self.reply(tid, f"✅ Group @{gname} → {len(ids)} GCs")

    async def _listgroups(self, tid, _):
        if not self.eng.gc_groups:
            await self.reply(tid, "No groups. Use /addgroup."); return
        lines = ["📦 GC Groups:"]
        for n, ids in self.eng.gc_groups.items():
            lines.append(f"  @{n} → {len(ids)} GCs")
        await self.reply(tid, "\n".join(lines))

    # ── GC add bots (auto-detect) ─────────────────────────────────────────────
    async def _gcaddbots(self, tid, args):
        """Auto-detect latest GC and add all bot accounts."""
        await self.reply(tid, "🤖 Auto-detecting GC…")
        gc = await self._auto_detect_gc(tid)
        if not gc:
            await self.reply(tid, "❌ Could not detect GC. Run /scangcs or /switchgc first.")
            return

        await self.reply(tid, f"✔ GC detected: {gc['name']}\n🤖 Adding bots…")
        clients = ACCOUNT_MANAGER.list_active()
        if not clients:
            await self.reply(tid, "❌ No bot accounts active."); return

        added, skipped, failed = 0, 0, 0
        for cl in clients:
            if cl.username == self.cl.username:
                skipped += 1
                continue
            uid = await self.cl.get_user_id(cl.username)
            if not uid:
                log.debug(f"gcaddbots: could not get uid for @{cl.username}")
                failed += 1
                continue
            ok = await self.cl.add_users_to_thread(gc["id"], [uid])
            if ok:
                log.info(f"✔ bot added: {cl.username}")
                added += 1
            else:
                log.info(f"⚠ already exists or failed: {cl.username}")
                skipped += 1
            await asyncio.sleep(random.uniform(3, 6))

        await self.reply(tid,
            f"✔ Done! added={added} skipped={skipped} failed={failed}")

    # ── GC add users (auto-detect) ────────────────────────────────────────────
    async def _gcadd(self, tid, args):
        """Auto-detect GC and add specified users."""
        if not args:
            await self.reply(tid, "Usage: /gcadd <user1,user2,...>"); return

        usernames = [u.strip().lstrip("@") for u in " ".join(args).split(",") if u.strip()]
        if not usernames:
            await self.reply(tid, "❌ No usernames given."); return

        await self.reply(tid, "👥 Auto-detecting GC…")
        gc = await self._auto_detect_gc(tid)
        if not gc:
            await self.reply(tid, "❌ Could not detect GC. Run /scangcs or /switchgc first.")
            return

        await self.reply(tid, f"✔ GC detected: {gc['name']}\n👥 Adding users…")
        added, failed = 0, 0

        # Add in batches of 2 with delays
        for i in range(0, len(usernames), 2):
            batch = usernames[i:i+2]
            uids  = []
            for uname in batch:
                uid = await self.cl.get_user_id(uname)
                if uid:
                    uids.append(uid)
                else:
                    log.info(f"⚠ already exists or not found: {uname}")
                    failed += 1

            if uids:
                ok = await self.cl.add_users_to_thread(gc["id"], uids)
                if ok:
                    for uname in batch:
                        log.info(f"✔ bot added: {uname}")
                    added += len(uids)
                else:
                    failed += len(uids)
            await asyncio.sleep(random.uniform(5, 8))

        await self.reply(tid, f"✔ Done! added={added} failed={failed}")

    async def _auto_detect_gc(self, fallback_tid: str) -> Optional[dict]:
        """Try to auto-detect the most recently active GC."""
        # 1. Last known GC in engine
        last = self.eng.get_last_active_gc(self.cl.username)
        if last:
            return last

        # 2. Active GC
        agc = self._agc()
        if agc:
            return agc

        # 3. GC where command was received
        gcs = self.eng.get_gcs(self.cl.username)
        for g in gcs:
            if g["id"] == fallback_tid:
                return g

        # 4. Auto-detect from inbox
        gc = await self.cl.auto_detect_gc()
        if gc:
            self.eng.update_last_active_gc(self.cl.username, gc)
            return gc

        return None

    # ── /raid ─────────────────────────────────────────────────────────────────
    async def _raid(self, tid, args):
        """
        Create a GC, add bots, optionally add users, warmup, then smartspam.
        Usage: /raid <gc_name> [users]
        """
        if not args:
            await self.reply(tid, "Usage: /raid <gc_name> [user1,user2,...]"); return

        gc_name  = args[0]
        users_raw = args[1] if len(args) > 1 else ""
        extra_users = [u.strip().lstrip("@") for u in users_raw.split(",") if u.strip()]

        await self.reply(tid, f"💥 RAID starting: {gc_name}")

        # Step 1: Get initial users (need at least 1 to create GC)
        clients = ACCOUNT_MANAGER.list_active()
        initial_uid = None
        for cl in clients:
            if cl.username != self.cl.username:
                uid = await self.cl.get_user_id(cl.username)
                if uid:
                    initial_uid = uid
                    break

        if not initial_uid:
            await self.reply(tid, "❌ Need at least 2 accounts to create GC."); return

        # Step 2: Create GC
        await self.reply(tid, "✔ Creating GC…")
        new_tid = await self.cl.create_group_thread([initial_uid], title=gc_name)
        if not new_tid:
            await self.reply(tid, "❌ GC creation failed."); return

        await self.reply(tid, f"✔ GC created: {gc_name} [{new_tid[:12]}…]")
        new_gc = {"id": new_tid, "name": gc_name}

        # Save to GC list
        gcs = self.eng.get_gcs(self.cl.username)
        gcs.append(new_gc)
        self.eng.set_gcs(self.cl.username, gcs)
        self.eng.active_gc[self.cl.username] = new_gc
        self.eng.update_last_active_gc(self.cl.username, new_gc)

        await asyncio.sleep(random.uniform(5, 10))

        # Step 3: Add bots
        await self.reply(tid, "🤖 Adding bots…")
        bot_added = 0
        for cl in clients:
            if cl.username in (self.cl.username,):
                continue
            uid = await self.cl.get_user_id(cl.username)
            if uid:
                ok = await self.cl.add_users_to_thread(new_tid, [uid])
                if ok:
                    log.info(f"✔ bot added: {cl.username}")
                    bot_added += 1
                else:
                    log.info(f"⚠ already exists: {cl.username}")
            await asyncio.sleep(random.uniform(3, 6))

        await self.reply(tid, f"✔ {bot_added} bots added")

        # Step 4: Add extra users
        if extra_users:
            await self.reply(tid, f"👥 Adding {len(extra_users)} users…")
            user_added = 0
            for i in range(0, len(extra_users), 2):
                batch = extra_users[i:i+2]
                uids  = []
                for uname in batch:
                    uid = await self.cl.get_user_id(uname)
                    if uid:
                        uids.append(uid)
                if uids:
                    ok = await self.cl.add_users_to_thread(new_tid, uids)
                    if ok:
                        user_added += len(uids)
                await asyncio.sleep(random.uniform(5, 8))
            await self.reply(tid, f"✔ {user_added} users added")

        # Step 5: Warmup delay
        warmup = random.randint(20, 40)
        await self.reply(tid, f"⏱ Warming up {warmup}s before spam…")
        await asyncio.sleep(warmup)

        # Step 6: Start smartspam
        await self.reply(tid, "🚀 Starting smartspam…")
        t = asyncio.create_task(
            worker_smartspam(self.eng, [new_gc], speed="medium", burst_count=2))
        self.reg.add(t, f"smartspam:{new_tid}")
        await self.reply(tid, f"🚀 Raid complete! smartspam running on {gc_name}")

    # ── /smartspam ────────────────────────────────────────────────────────────
    async def _smartspam(self, tid, args):
        """
        Fast + stable parallel GC spam.
        Usage: /smartspam <targets> <speed> [text]
        """
        if len(args) < 2:
            await self.reply(tid, "Usage: /smartspam <targets> <speed> [text]\nspeed: slow|medium|fast")
            return

        tgt    = args[0]
        speed  = args[1].lower()
        custom = " ".join(args[2:]) if len(args) > 2 else None

        if speed not in SPEED_MODES:
            await self.reply(tid, f"❌ Bad speed. Use: slow | medium | fast"); return

        gcs = resolve(self.eng, self.cl.username, tgt)
        if not gcs:
            await self.reply(tid, "❌ No GCs matched. Run /scangcs first."); return

        burst = self.eng.cfg.get("smartspam_burst_count", 2)
        label = f"smartspam:{tgt}"
        self.reg.stop_key(label)
        t = asyncio.create_task(
            worker_smartspam(self.eng, gcs, speed=speed, custom=custom, burst_count=burst))
        i = self.reg.add(t, label)
        dmin, dmax = SPEED_MODES[speed]
        await self.reply(tid,
            f"🚀 SMARTSPAM | {len(gcs)} GCs | speed={speed} ({dmin}-{dmax}s) | id: {i}\n"
            f"Stop with /stopmulti {i}")

    # ── /pwspam ───────────────────────────────────────────────────────────────
    async def _pwspam(self, tid, args):
        """
        Playwright browser-based human sim spam.
        Usage: /pwspam <targets> <speed> [text]
        """
        if not HAS_PLAYWRIGHT:
            await self.reply(tid, "❌ Playwright not installed. pip install playwright && playwright install chromium")
            return
        if len(args) < 2:
            await self.reply(tid, "Usage: /pwspam <targets> <speed> [text]\nspeed: slow|medium|fast")
            return

        tgt    = args[0]
        speed  = args[1].lower()
        custom = " ".join(args[2:]) if len(args) > 2 else None

        if speed not in SPEED_MODES:
            await self.reply(tid, f"❌ Bad speed. Use: slow | medium | fast"); return

        gcs = resolve(self.eng, self.cl.username, tgt)
        if not gcs:
            await self.reply(tid, "❌ No GCs matched. Run /scangcs first."); return

        if not _PW_ENGINE._ready:
            await self.reply(tid, "🎭 Starting Playwright browser…")
            await _PW_ENGINE.start()

        label = f"pwspam:{tgt}"
        self.reg.stop_key(label)
        t = asyncio.create_task(
            worker_pwspam(self.eng, gcs, speed=speed, custom=custom))
        i = self.reg.add(t, label)
        await self.reply(tid,
            f"⚡ PWSPAM (playwright) | {len(gcs)} GCs | speed={speed} | id: {i}\n"
            f"✔ sent via playwright\nStop with /stopmulti {i}")


    # ── /pwgo ────────────────────────────────────────────────────────────────
    async def _pwgo_cmd(self, tid, args):
        """
        Ultra-fast Playwright spam.
        Usage: /pwgo [engines] [text]
              engines = number of parallel browser engines (default 4, max 8)
              text    = custom spam message (optional, uses random template)

        Auto-detects the current GC. Stop with /stopgo or /stop.
        """
        if not HAS_PLAYWRIGHT:
            await self.reply(tid, "❌ Playwright not installed. pip install playwright && playwright install chromium")
            return

        # Parse optional engine count
        engine_count = 4
        custom_text  = None
        if args:
            if args[0].isdigit():
                engine_count = min(max(1, int(args[0])), 8)
                custom_text  = " ".join(args[1:]) if len(args) > 1 else None
            else:
                custom_text = " ".join(args)

        # Auto-detect GC: use the current thread first, then last_active_gc
        gc = self.eng.active_gc.get(self.cl.username)
        if not gc:
            gc = self.eng._last_active_gc.get(self.cl.username)
        if not gc:
            gcs = self.eng.get_gcs(self.cl.username)
            gc  = gcs[0] if gcs else None
        if not gc:
            await self.reply(tid, "❌ No GC detected. Run /scangcs or /switchgc first.")
            return

        gc_id   = gc["id"]
        gc_name = gc.get("name", gc_id)

        # Collect URLs for all known GCs (multi-GC multi-tab mode)
        all_gcs  = self.eng.get_gcs(self.cl.username)
        url_list = [f"https://www.instagram.com/direct/t/{g['id']}/" for g in all_gcs] if all_gcs else [f"https://www.instagram.com/direct/t/{gc_id}/"]

        pool   = self.eng.cfg.get("emoji_pool", ["⚡"])
        em     = rand_emoji(pool)
        text   = (fmt(custom_text, name=gc_name, emoji=em)
                  if custom_text else
                  fmt(random.choice(SPAM_TEMPLATES), name=gc_name, emoji=em))

        user_key = f"pwgo:{self.cl.username}:{tid}"

        # Kill any previous /pwgo for this user+thread
        await stop_pwgo(user_key)

        if not _PW_ENGINE._ready:
            await self.reply(tid, "🎭 Starting Playwright browser…")
            await _PW_ENGINE.start()

        label = f"pwgo:{gc_id}"
        self.reg.stop_key(label)
        task = asyncio.create_task(
            worker_pwgo(self.eng, url_list, text, user_key, engine_count=engine_count))
        self.reg.add(task, label)

        reply_text = (
            "🔱 PWGO ULTRA SPAM ACTIVE\n"
            + f"   GC      : {gc_name}\n"
            + f"   Engines : {engine_count} parallel instances\n"
            + f"   Text    : {text[:60]}{'…' if len(text) > 60 else ''}\n"
            + "   Delay   : 0.2-0.4s per engine\n"
            + "   Stop    : /stopgo or /stop"
        )
        await self.reply(tid, reply_text)

    async def _stopgo_cmd(self, tid, args):
        """Stop all /pwgo engines for this thread."""
        user_key = f"pwgo:{self.cl.username}:{tid}"
        found = await stop_pwgo(user_key)
        # Also cancel via TaskReg
        for gc in self.eng.get_gcs(self.cl.username):
            self.reg.stop_key(f"pwgo:{gc['id']}")
        if found:
            await self.reply(tid, "🛑 PWGO engines stopped.")
        else:
            await self.reply(tid, "ℹ️  No active /pwgo session found.")


    # ── /sasnc / +sasnc ──────────────────────────────────────────────────────
    async def _sasnc_cmd(self, tid, args):
        """
        Ultra-fast GC name changer — 0.005s loop, stylish symbols.
        Usage: /sasnc <text>   or   +sasnc <text>
        Auto-detects current GC. Stop with /stopsasnc or /stop.
        """
        text = " ".join(args).strip() if args else self.eng.cfg.get("base_name", "NIGGA SYSTEM")
        gc = self._agc() or self.eng._last_active_gc.get(self.cl.username)
        if not gc:
            gcs = self.eng.get_gcs(self.cl.username)
            gc  = gcs[0] if gcs else None
        if not gc:
            await self.reply(tid, "❌ No GC detected. Run /scangcs first."); return

        gc_id = gc["id"]
        pool  = self.eng.cfg.get("emoji_pool", ["⚡"])

        task_id    = f"sasnc:{self.cl.username}:{gc_id}"
        stop_event, task = TASK_CTRL.start(
            task_id,
            worker_sasnc(self.cl, gc_id, text, pool, TASK_CTRL._events.get(task_id) or asyncio.Event(), self.eng)
        )
        # Re-register with the freshly created stop_event from TASK_CTRL
        TASK_CTRL._events[task_id] = stop_event
        self.reg.add(task, f"sasnc:{gc_id}")
        await self.reply(tid,
            f"⚡ SASNC ULTRA ACTIVE\n"
            f"   GC   : {gc.get('name', gc_id)}\n"
            f"   Text : {text}\n"
            f"   Speed: 0.005s loop\n"
            f"   Stop : /stopsasnc or /stop")

    async def _stopsasnc_cmd(self, tid, args):
        gc = self._agc() or self.eng._last_active_gc.get(self.cl.username)
        gc_id = gc["id"] if gc else ""
        TASK_CTRL.stop_prefix(f"sasnc:{self.cl.username}:")
        self.reg.stop_key(f"sasnc:{gc_id}")
        await self.reply(tid, "🛑 SASNC stopped.")

    # ── /loginuser ────────────────────────────────────────────────────────────
    async def _loginuser_cmd(self, tid, args):
        """
        Login a user account via sessionid (stored in sessions.json).
        Usage: /loginuser <username> <sessionid>
        """
        if len(args) < 2:
            await self.reply(tid, "Usage: /loginuser <username> <sessionid>"); return
        uname, sid = args[0].lstrip("@"), args[1]
        sessions_path = Path("sessions.json")
        sessions = {}
        if sessions_path.exists():
            try:
                sessions = _json_loads(sessions_path.read_text(encoding="utf-8"))
            except Exception:
                sessions = {}
        sessions[uname] = {"sessionid": sid, "added": str(datetime.now())}
        sessions_path.write_text(_json_dumps(sessions, indent=2), encoding="utf-8")
        await self.reply(tid,
            f"✅ User @{uname} session stored.\n"
            f"   File: sessions.json\n"
            f"   Use /creategc, /addbot, /promotebots with this account.")

    # ── /creategc ─────────────────────────────────────────────────────────────
    async def _creategc_cmd(self, tid, args):
        """
        Create a new Instagram GC using the current active bot account.
        Usage: /creategc <gc_name> [user1,user2,...]
        """
        if not args:
            await self.reply(tid, "Usage: /creategc <gc_name> [user1,user2,...]"); return
        gc_name    = args[0]
        user_list  = [u.strip().lstrip("@") for u in args[1].split(",")] if len(args) > 1 else []
        cl = self.cl
        try:
            loop = asyncio.get_running_loop()
            # Resolve user IDs
            uids = []
            for uname in user_list[:20]:
                try:
                    uid = await loop.run_in_executor(_POOL, lambda u=uname: cl._cl.user_id_from_username(u))
                    uids.append(str(uid))
                    await asyncio.sleep(1.0)
                except Exception as e:
                    log.debug(f"uid resolve {uname}: {e}")

            # Create the thread
            result = await loop.run_in_executor(
                _POOL,
                lambda: cl._cl.direct_thread_create(uids, gc_name)
            )
            new_tid = result.id if hasattr(result, "id") else str(result)
            self.eng.add_gc(cl.username, {"id": new_tid, "name": gc_name})
            await self.reply(tid,
                f"✅ GC created: {gc_name}\n"
                f"   Thread ID: {new_tid}\n"
                f"   Members: {len(uids)} added")
        except Exception as e:
            await self.reply(tid, f"❌ /creategc failed: {_clean_exc(e)}")

    # ── /addbot ───────────────────────────────────────────────────────────────
    async def _addbot_cmd(self, tid, args):
        """
        Add bot accounts to the current (auto-detected) GC.
        Usage: /addbot [gc_id]   (uses current GC if no ID given)
        """
        gc = self._agc() if not args else {"id": args[0]}
        if not gc:
            gcs = self.eng.get_gcs(self.cl.username)
            gc  = gcs[0] if gcs else None
        if not gc:
            await self.reply(tid, "❌ No GC. Run /scangcs or specify gc_id."); return

        gc_id   = gc["id"]
        clients = ACCOUNT_MANAGER.list_active()
        added   = 0
        failed  = 0
        loop    = asyncio.get_running_loop()

        await self.reply(tid, f"⚙️ Adding {len(clients)} bot accounts to GC {gc_id[:12]}…")
        for cl in clients:
            if cl.username == self.cl.username:
                continue
            try:
                uid = await loop.run_in_executor(
                    _POOL, lambda u=cl.username: self.cl._cl.user_id_from_username(u))
                ok = await self.cl.add_users_to_thread(gc_id, [str(uid)])
                if ok:
                    added += 1
                else:
                    failed += 1
                await asyncio.sleep(2.0)
            except Exception as e:
                log.debug(f"addbot {cl.username}: {e}")
                failed += 1

        await self.reply(tid,
            f"✅ /addbot done\n"
            f"   Added : {added}\n"
            f"   Failed: {failed}")

    # ── /promotebots ──────────────────────────────────────────────────────────
    async def _promotebots_cmd(self, tid, args):
        """
        Promote all bot accounts to admin in the current GC.
        Usage: /promotebots [gc_id]
        """
        gc = self._agc() if not args else {"id": args[0]}
        if not gc:
            gcs = self.eng.get_gcs(self.cl.username)
            gc  = gcs[0] if gcs else None
        if not gc:
            await self.reply(tid, "❌ No GC. Run /scangcs or specify gc_id."); return

        gc_id   = gc["id"]
        clients = ACCOUNT_MANAGER.list_active()
        loop    = asyncio.get_running_loop()
        promoted = 0; failed = 0

        await self.reply(tid, f"⚙️ Promoting {len(clients)} bots in GC {gc_id[:12]}…")
        for cl in clients:
            try:
                uid = await loop.run_in_executor(
                    _POOL, lambda u=cl.username: self.cl._cl.user_id_from_username(u))
                await loop.run_in_executor(
                    _POOL,
                    lambda gid=gc_id, u=str(uid): self.cl._cl.direct_thread_participants_admin_promote(gid, [u])
                )
                promoted += 1
                await asyncio.sleep(2.0)
            except Exception as e:
                log.debug(f"promote {cl.username}: {e}")
                failed += 1

        await self.reply(tid,
            f"✅ /promotebots done\n"
            f"   Promoted: {promoted}\n"
            f"   Failed  : {failed}")

    # ── multi helpers ─────────────────────────────────────────────────────────
    def _parse_multi(self, args):
        if len(args) < 2: raise ValueError("Need <targets> <mode>")
        mode = args[1].lower()
        if mode not in ("sequential", "parallel"):
            raise ValueError("mode must be sequential or parallel")
        return args[0], mode, args[2:]

    def _launch(self, gcs: list, mode: str, make_coro, label: str) -> str:
        if not gcs: return ""
        if mode == "parallel":
            i = oid()
            for g in gcs:
                self.reg.add(asyncio.create_task(make_coro([g])), label)
            return i
        return self.reg.add(asyncio.create_task(make_coro(gcs)), label)

    async def _multispam(self, tid, args):
        try: tgt, mode, extra = self._parse_multi(args)
        except ValueError as e:
            await self.reply(tid, f"Usage: /multispam <targets> <mode> [text]\n{e}"); return
        gcs    = resolve(self.eng, self.cl.username, tgt)
        if not gcs: await self.reply(tid, "❌ No GCs matched."); return
        custom = " ".join(extra) if extra else None
        i = self._launch(gcs, mode,
            lambda g: worker_spam(self.eng, self.cl, g, custom, self.sq),
            f"multispam:{tgt}")
        await self.reply(tid, f"✅ Spam → {len(gcs)} GCs | id: {i}")

    async def _multinc(self, tid, args):
        try: tgt, mode, extra = self._parse_multi(args)
        except ValueError as e:
            await self.reply(tid, f"Usage: /multinc <targets> <mode> [names]\n{e}"); return
        names = extra if extra else None
        task  = asyncio.create_task(worker_nc(self.eng, self.cl, names))
        i     = self.reg.add(task, f"multinc:{tgt}")
        await self.reply(tid, f"✅ NC started | id: {i}")

    async def _multipicspam(self, tid, args):
        try: tgt, mode, _ = self._parse_multi(args)
        except ValueError as e:
            await self.reply(tid, f"Usage: /multipicspam <targets> <mode>\n{e}"); return
        gcs = resolve(self.eng, self.cl.username, tgt)
        if not gcs: await self.reply(tid, "❌ No GCs matched."); return
        i = self._launch(gcs, mode,
            lambda g: worker_pic(self.eng, self.cl, g),
            f"picspam:{tgt}")
        await self.reply(tid, f"✅ Pic-spam → {len(gcs)} GCs | id: {i}")

    async def _stopmulti(self, tid, args):
        if not args:
            await self.reply(tid, "Usage: /stopmulti <id|all>"); return
        if args[0].lower() == "all":
            self.reg.stop_all()
            await self.reply(tid, "🛑 All ops stopped.")
        else:
            self.reg.stop(args[0])
            await self.reply(tid, f"🛑 Stopped: {args[0]}")

    async def _listmulti(self, tid, _):
        ops = self.reg.list()
        if not ops:
            await self.reply(tid, "ℹ️  No active ops."); return
        lines = [f"📋 Active ops ({len(ops)}):"]
        for i, l in ops[:20]:
            lines.append(f"  {i}: {l}")
        await self.reply(tid, "\n".join(lines))

    async def _startnc(self, tid, args):
        self.reg.stop_key("nc")
        names = args if args else None
        t     = asyncio.create_task(worker_nc(self.eng, self.cl, names))
        self.reg.add(t, "nc")
        label = f": {', '.join(args)}" if args else ""
        await self.reply(tid, f"📝 NC started{label}\n   Stop with: /stopnc")

    async def _stopnc(self, tid, _):
        self.reg.stop_key("nc")
        await self.reply(tid, "🛑 NC stopped.")

    async def _spam_local(self, tid, args):
        gc     = self._agc() or {"id": tid, "name": "this GC"}
        custom = " ".join(args) if args else None
        key    = f"spam_{tid}"
        self.reg.stop_key(key)
        t = asyncio.create_task(
            worker_spam(self.eng, self.cl, [gc], custom, self.sq))
        self.reg.add(t, key)
        await self.reply(tid, "🔥 Spam started\n   Stop with: /stop")

    async def _gcnc_local(self, tid, args):
        names = args if args else None
        key   = f"gcnc_{tid}"
        self.reg.stop_key(key)
        t = asyncio.create_task(
            worker_gcnc(self.eng, self.cl, tid, "this GC", names))
        self.reg.add(t, key)
        await self.reply(tid, "🏷️  GCNC started\n   Stop with: /stop")

    async def _godspam_local(self, tid, args):
        custom = " ".join(args) if args else None
        key    = f"godspam_{tid}"
        self.reg.stop_key(key)
        t = asyncio.create_task(
            worker_godspam(self.eng, self.cl, tid, "this GC", custom, self.sq))
        self.reg.add(t, key)
        await self.reply(tid, "⚡ GODSPAM started\n   Stop with: /stop")

    async def _picspam_local(self, tid, _):
        gc  = {"id": tid, "name": "this GC"}
        key = f"picspam_{tid}"
        self.reg.stop_key(key)
        t = asyncio.create_task(worker_pic(self.eng, self.cl, [gc]))
        self.reg.add(t, key)
        await self.reply(tid, "🖼️  PIC-SPAM started\n   Stop with: /stop")

    async def _stop_local(self, tid, _):
        stopped = []
        for key in (f"spam_{tid}", f"gcnc_{tid}", f"godspam_{tid}", f"picspam_{tid}"):
            if key in {l for l in self.reg._l.values()}:
                self.reg.stop_key(key)
                stopped.append(key.split("_")[0])
        # Also stop any /pwgo tasks
        user_key = f"pwgo:{self.cl.username}:{tid}"
        pw_stopped = await stop_pwgo(user_key)
        for gc in self.eng.get_gcs(self.cl.username):
            self.reg.stop_key(f"pwgo:{gc['id']}")
        if pw_stopped:
            stopped.append("pwgo")
        if stopped:
            await self.reply(tid, f"🛑 Stopped: {', '.join(stopped)}")
        else:
            await self.reply(tid, "ℹ️  No active tasks in this GC.")

    async def _startgcnc(self, tid, args):
        gcs = self.eng.get_gcs(self.cl.username)
        if not gcs:
            await self.reply(tid, "❌ No GCs found. Run /scangcs first."); return
        names = args if args else None
        self.reg.stop_key("gcnc")
        for gc in gcs:
            t = asyncio.create_task(
                worker_gcnc(self.eng, self.cl, gc["id"], gc.get("name", str(gc["id"])), names))
            self.reg.add(t, "gcnc")
        await self.reply(tid, f"🏷️  GCNC ACTIVE → {len(gcs)} GCs\n   Stop with: /stopgcnc")

    async def _stopgcnc(self, tid, _):
        self.reg.stop_key("gcnc")
        for k in list({l for l in self.reg._l.values() if l.startswith("gcnc_")}):
            self.reg.stop_key(k)
        await self.reply(tid, "🛑 GCNC stopped on all GCs.")

    async def _startspam(self, tid, args):
        gcs = self.eng.get_gcs(self.cl.username)
        if not gcs:
            await self.reply(tid, "❌ No GCs found. Run /scangcs first."); return
        self.reg.stop_key("spam")
        custom = " ".join(args) if args else None
        for gc in gcs:
            t = asyncio.create_task(
                worker_spam(self.eng, self.cl, [gc], custom, self.sq))
            self.reg.add(t, "spam")
        await self.reply(tid, f"🔥 UNLIMITED SPAM → {len(gcs)} GCs")

    async def _gspam(self, tid, args):
        """
        /gspam [speed] [text]
        Global smartspam: auto-detect active GC + loop ALL known GCs.
        If command came from inside a GC, that GC is included automatically.
        Speed: slow | medium | fast | unlimited  (default: fast)
        """
        gcs = self.eng.get_gcs(self.cl.username)

        # Auto-include the current thread if it's a known GC
        current_gc = self._agc() or {"id": tid, "name": "current GC"}
        if current_gc and not any(g["id"] == current_gc["id"] for g in gcs):
            gcs = [current_gc] + gcs

        if not gcs:
            await self.reply(tid, "❌ No GCs found. Run /scangcs first."); return

        speed  = "fast"
        custom = None
        if args:
            if args[0].lower() in SPEED_MODES:
                speed = args[0].lower()
                custom = " ".join(args[1:]) if len(args) > 1 else None
            else:
                custom = " ".join(args)

        burst = self.eng.cfg.get("smartspam_burst_count", 2)
        label = "gspam"
        self.reg.stop_key(label)
        t = asyncio.create_task(
            worker_smartspam(self.eng, gcs, speed=speed,
                             custom=custom, burst_count=burst))
        i = self.reg.add(t, label)
        dmin, dmax = SPEED_MODES[speed]
        delay_str = f"{dmin}-{dmax}s" if dmax > 0.05 else "UNLIMITED"
        await self.reply(tid,
            f"🌍 GSPAM | {len(gcs)} GCs | speed={speed} ({delay_str}) | id: {i}\n"
            f"Stop with /gstop or /stopmulti {i}")

    async def _gstop(self, tid, _):
        """Stop all gspam tasks."""
        self.reg.stop_key("gspam")
        self.reg.stop_key("spam")
        self.reg.stop_key("smartspam:all")
        await self.reply(tid, "🛑 GSPAM stopped.")

    async def _stopspam(self, tid, _):
        self.reg.stop_key("spam")
        await self.reply(tid, "🛑 Spam stopped on all GCs.")

    async def _stopgodspam(self, tid, args):
        if args:
            target = args[0].lower()
            gcs    = self.eng.get_gcs(self.cl.username) or []
            gc_id  = args[0]
            for g in gcs:
                if str(g["id"]).lower() == target or target in g.get("name","").lower():
                    gc_id = g["id"]
                    break
            self.reg.stop_key(f"godspam_{gc_id}")
            await self.reply(tid, f"🛑 GODSPAM stopped → {args[0]}")
        else:
            keys = list({l for l in self.reg._l.values() if l.startswith("godspam_")})
            for k in keys:
                self.reg.stop_key(k)
            await self.reply(tid, f"🛑 GODSPAM stopped on all GCs ({len(keys)} loops)")

    async def _startpicspam(self, tid, _):
        gcs = self.eng.get_gcs(self.cl.username)
        if not gcs:
            await self.reply(tid, "❌ No GCs found. Run /scangcs first."); return
        self.reg.stop_key("picspam")
        for gc in gcs:
            t = asyncio.create_task(worker_pic(self.eng, self.cl, [gc]))
            self.reg.add(t, "picspam")
        await self.reply(tid, f"🔥 PIC-SPAM → {len(gcs)} GCs")

    async def _stoppicspam(self, tid, _):
        self.reg.stop_key("picspam")
        await self.reply(tid, "🛑 Pic-spam stopped.")

    async def _voice(self, tid, args):
        if not args:
            await self.reply(tid, "Usage: /animevoice [voice] <text>\nVoices: " + " ".join(VOICE_MAP)); return
        if args[0].lower() in VOICE_MAP:
            vk, text = args[0].lower(), " ".join(args[1:])
        else:
            vk, text = "default", " ".join(args)
        if not text: await self.reply(tid, "❌ No text."); return
        await self.reply(tid, f"🎤 Generating [{vk}]…")
        p = await asyncio.get_running_loop().run_in_executor(_POOL, lambda: _gen_voice(text, vk))
        if not p:
            await self.reply(tid, "❌ Voice failed. pip install edge-tts"); return
        gc = self._agc()
        try:
            await self.cl.send_photo(gc["id"] if gc else tid, p)
            await self.reply(tid, "✅ Voice note sent.")
        except Exception as e:
            await self.reply(tid, f"⚠️ Send failed: {e}")
        finally:
            try: p.unlink()
            except Exception: pass

    async def _search(self, tid, args):
        if not args: await self.reply(tid, "Usage: /search <username>"); return
        res = await self.cl.search(args[0])
        if res:
            lines = [f"✅ {len(res)} result(s):"]
            for u in res[:5]:
                lines.append(f"  @{u.get('username','?')} – {u.get('full_name','?')}")
            await self.reply(tid, "\n".join(lines))
        else:
            await self.reply(tid, "❌ No results.")

    async def _setdelay(self, tid, args):
        if not args: await self.reply(tid, "Usage: /setdelay <sec>"); return
        try:
            v = max(0.0, float(args[0]))
            self.eng.cfg["spam_delay_min"] = v * 0.5
            self.eng.cfg["spam_delay_max"] = v
            save_cfg(self.eng.cfg)
            await self.reply(tid, f"✅ Spam delay range = {v*0.5:.2f}–{v:.2f}s")
        except ValueError: await self.reply(tid, "❌ Bad number.")

    async def _setncdelay(self, tid, args):
        if not args: await self.reply(tid, "Usage: /setncdelay <sec>"); return
        try:
            v = max(0.5, float(args[0]))
            self.eng.cfg["nc_delay"] = v
            save_cfg(self.eng.cfg)
            await self.reply(tid, f"✅ NC delay = {v}s")
        except ValueError: await self.reply(tid, "❌ Bad number.")

# ─────────────────────────────────────────────────────────────────────────────
# LISTENER
# ─────────────────────────────────────────────────────────────────────────────
async def listener(eng: Engine, cl: IGClient, reg: TaskReg, sq: SendQueue, regs: dict):
    handler   = CmdHandler(eng, cl, reg, regs, sq)
    poll      = eng.cfg.get("cmd_poll_interval", 1.0)
    in_groups = eng.cfg.get("listen_in_groups", True)
    inbox_limit = eng.cfg.get("inbox_limit", 100)
    seen: set = set()
    pk_to_user: Dict[str, str] = {}

    def _owner() -> str:
        return eng.cfg.get("owner_username", "").lower()

    log.info(f"👂 @{cl.username} listening | owner=@{_owner() or '<anyone>'} | poll={poll}s")

    _consecutive_empty = 0
    _inbox_backoff     = poll
    _inbox_confirmed   = False

    while True:
        try:
            threads = await cl.get_inbox(inbox_limit)

            if threads:
                _consecutive_empty = 0
                _inbox_backoff     = poll
                if not _inbox_confirmed:
                    _inbox_confirmed = True
                    log.info(f"✅ @{cl.username}: inbox active — {len(threads)} thread(s)")
            else:
                _consecutive_empty += 1
                if _consecutive_empty >= 5:
                    _inbox_backoff = min(60.0, poll * (1.5 ** (_consecutive_empty - 4)))

            for thread in threads:
                users    = thread.get("users", [])
                is_group = thread.get("is_group") or len(users) > 1
                tid      = str(thread.get("thread_id", ""))
                items    = thread.get("items", [])
                if not tid:
                    continue

                # Track GC activity
                if is_group:
                    gc_obj = {"id": tid, "name": thread.get("thread_title", tid)}
                    eng.update_last_active_gc(cl.username, gc_obj)

                for u in users:
                    pk  = str(u.get("pk", ""))
                    unm = u.get("username", "").lower()
                    if pk and unm:
                        pk_to_user[pk] = unm

                owner  = _owner()
                private_mode = eng.cfg.get("private_mode", True)

                usernames = {u.get("username", "").lower() for u in users}

                # In private_mode: only accept commands from owner in DM
                # But spam commands in group are OK from authorized users
                if private_mode and not is_group and owner and owner not in usernames:
                    continue

                if is_group and not in_groups:
                    continue

                for item in reversed(items):
                    mid  = str(item.get("item_id", ""))
                    text = (item.get("text") or "").strip()
                    if not mid or mid in seen:
                        continue
                    seen.add(mid)
                    if not text.startswith("/"):
                        continue

                    sender_id = str(item.get("user_id", ""))
                    sender_nm = (
                        pk_to_user.get(sender_id)
                        or next(
                            (u.get("username", "").lower()
                             for u in users if str(u.get("pk", "")) == sender_id),
                            ""
                        )
                    )

                    # Ultra security: only owner/allowed can send commands
                    # In private_mode from DM: strictly owner only
                    if private_mode and not is_group:
                        if owner and sender_nm != owner:
                            log.debug(f"⚠ unauthorized DM ({sender_nm})")
                            continue

                    src = "GC" if is_group else "DM"
                    log.info(f"📩 [{src}] @{sender_nm} → @{cl.username}: {text}")
                    asyncio.create_task(handler.run(tid, text, sender=sender_nm))

            if len(seen) > 10000:
                seen = set(list(seen)[-4000:])
            if len(pk_to_user) > 5000:
                pk_to_user.clear()

        except asyncio.CancelledError:
            raise
        except LoginRequired:
            log.warning(f"⚠️  @{cl.username} session expired — refreshing…")
            eng.inc("reconnects")
            try:
                loop = asyncio.get_running_loop()
                refreshed = await loop.run_in_executor(_POOL, cl._try_refresh_session)
                if refreshed:
                    await cl._ensure_aio(force_rebuild=True)
                    log.info(f"♻️  @{cl.username} session refreshed OK")
                else:
                    log.warning(f"⚠️  @{cl.username} session refresh failed — waiting {eng.cfg.get('reconnect_delay', 30)}s")
                    await asyncio.sleep(eng.cfg.get("reconnect_delay", 30))
            except Exception as e:
                log.debug(f"Session refresh @{cl.username}: {e}")
        except Exception as e:
            err_str = str(e).lower()
            if any(k in err_str for k in ("login_required", "loginrequired", "challenge_required")):
                log.warning(f"⚠️  @{cl.username} auth error — refreshing…")
                eng.inc("reconnects")
                try:
                    loop = asyncio.get_running_loop()
                    refreshed = await loop.run_in_executor(_POOL, cl._try_refresh_session)
                    if refreshed:
                        await cl._ensure_aio(force_rebuild=True)
                        log.info(f"♻️  @{cl.username} session refreshed OK")
                    else:
                        await asyncio.sleep(eng.cfg.get("reconnect_delay", 30))
                except Exception as inner_e:
                    log.debug(f"Session refresh @{cl.username}: {inner_e}")
            else:
                log.debug(f"Listener @{cl.username}: {e}")
                METRICS.errors_total += 1
                eng.inc("errors")

        await asyncio.sleep(_inbox_backoff)

# ─────────────────────────────────────────────────────────────────────────────
# HEARTBEAT
# ─────────────────────────────────────────────────────────────────────────────
def heartbeat(eng: Engine, regs: dict):
    iv = eng.cfg.get("heartbeat_interval", 30)
    while eng.running:
        time.sleep(iv)
        try:
            ops  = sum(r.count() for r in regs.values())
            m    = METRICS.snapshot()
            acct = len(eng._clients)
            errs = METRICS.errors_total
            mps  = m["msgs_per_sec"]
            print(
                f"\r♻️  ALIVE | {uptime()} | accts={acct} | ops={ops} | "
                f"{mps}/s | errs={errs} | proxies={len(eng.proxy_rotator)}",
                flush=True,
            )
        except Exception as e:
            log.debug(f"heartbeat error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PER-ACCOUNT ASYNC RUNNER
# ─────────────────────────────────────────────────────────────────────────────
async def run_account(eng: Engine, acct: dict, reg: TaskReg, regs: dict):
    username     = acct["username"]
    password     = acct.get("password", "")
    session_file = acct.get("session_file", f"{username}_session.json")
    sessionid    = acct.get("sessionid", "")
    rd           = eng.cfg.get("reconnect_delay", 30)
    is_session_login = bool(sessionid)

    cl = IGClient(username, password, eng.cfg, session_file=session_file, eng=eng)

    try:
        loop = asyncio.get_running_loop()
        if is_session_login:
            logged_in = await loop.run_in_executor(
                _POOL, lambda: cl.login_sessionid(sessionid))
        else:
            logged_in = await loop.run_in_executor(_POOL, cl.login)
    except asyncio.CancelledError:
        return
    except Exception as e:
        log.error(f"❌ Login ERROR @{username}: {_clean_exc(e)}")
        return

    if not logged_in:
        log.error(f"❌ Login failed @{username} — bot continues without this account.")
        return

    eng.inc("logins")
    eng.register_client(cl)

    gcs = eng.get_gcs(username)
    log.info(f"✅ @{username} live | {len(gcs)} GCs loaded | "
             f"proxies={len(eng.proxy_rotator)}")

    sq = SendQueue(cl, eng, workers=eng.cfg.get("send_concurrency", 64))
    await sq.start()

    while eng.running:
        try:
            await listener(eng, cl, reg, sq, regs)
        except asyncio.CancelledError:
            break
        except Exception as e:
            log.error(f"❌ Listener crash @{username}: {_clean_exc(e)}")

        if not eng.running:
            break

        log.warning(f"⚠️  @{username} listener exited – reconnecting in {rd}s…")
        eng.inc("reconnects")
        await asyncio.sleep(rd)

        if not is_session_login and not cl._logged_in:
            try:
                loop = asyncio.get_running_loop()
                relogged = await loop.run_in_executor(_POOL, cl.login)
                if not relogged:
                    log.error(f"❌ Re-login failed @{username} — stopping.")
                    break
            except asyncio.CancelledError:
                break
            except Exception as e:
                log.error(f"❌ Re-login error @{username}: {_clean_exc(e)}")
                break

    await sq.stop()
    await cl.close()
    eng.unregister_client(cl)


def thread_account(eng: Engine, acct: dict, reg: TaskReg, regs: dict = None):
    if regs is None:
        regs = {}
    if HAS_UVLOOP:
        loop = uvloop.new_event_loop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_account(eng, acct, reg, regs))
    except Exception as e:
        log.error(f"❌ Thread @{acct['username']}: {_clean_exc(e)}")
    finally:
        loop.close()

# ─────────────────────────────────────────────────────────────────────────────
# FASTAPI GATEWAY (optional --api mode)
# ─────────────────────────────────────────────────────────────────────────────
def _start_api_gateway(eng: Engine, port: int = 8080):
    if not HAS_FASTAPI:
        log.error("❌ FastAPI not installed. pip install fastapi uvicorn")
        return

    app = FastAPI(title="NIGGA SYSTEM API Gateway v7.0")

    class SendRequest(BaseModel):
        thread_id: str
        text: str
        username: Optional[str] = None

    class SendResponse(BaseModel):
        success: bool
        account: str
        message: str

    @app.get("/health")
    async def health():
        return {"status": "ok", "accounts": len(eng._clients), "uptime": uptime()}

    @app.get("/stats")
    async def stats():
        m = METRICS.snapshot()
        return {"stats": dict(eng.stats), "metrics": m, "accounts": eng.list_usernames()}

    @app.post("/send", response_model=SendResponse)
    async def send_message(req: SendRequest):
        if req.username:
            cl = eng.get_client(req.username)
        else:
            cl = eng.next_client()
        if not cl:
            raise HTTPException(status_code=503, detail="No active accounts")
        ok = await cl.send(req.thread_id, req.text)
        return SendResponse(
            success=ok,
            account=cl.username,
            message="Sent" if ok else "Failed",
        )

    @app.get("/accounts")
    async def accounts():
        return {"accounts": eng.list_usernames(), "count": len(eng._clients)}

    @app.get("/proxy-stats")
    async def proxy_stats():
        return eng.proxy_rotator.get_stats()

    def _run():
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")

    t = threading.Thread(target=_run, name="api-gateway", daemon=True)
    t.start()
    log.info(f"🚀 FastAPI gateway started on :{port}")

# ─────────────────────────────────────────────────────────────────────────────
# LIVE STATS PRINTER — background coroutine, prints every 2 sec
# ─────────────────────────────────────────────────────────────────────────────
async def stats_printer(eng: Engine):
    while eng.running:
        try:
            snap = TASK_STATS.snapshot()
            mps  = METRICS.msgs_per_sec()
            ops  = sum(r.count() for r in eng._account_regs.values()) if hasattr(eng, "_account_regs") else 0
            print(
                f"\r[STATS] Sent: {snap['sent']} | Failed: {snap['failed']} "
                f"| Msgs/s: {mps} | Active tasks: {ops} "
                f"| Accounts: {len(eng._clients)}",
                end="", flush=True,
            )
        except Exception:
            pass
        await asyncio.sleep(2)

# ─────────────────────────────────────────────────────────────────────────────
# TELEGRAM MENU TEXT
# ─────────────────────────────────────────────────────────────────────────────
TG_MENU_TEXT = """
╔═══════════════════════════════════════╗
║     NIGGA SYSTEM v9.0 🔥              ║
║     Telegram + IG Dual Control        ║
╠═══════════════════════════════════════╣
║  🎛️  UI PANEL                         ║
║  /panel  ← full button control panel  ║
╠═══════════════════════════════════════╣
║  🔐 ACCOUNTS                          ║
║  /login <user> <pass>                 ║
║  /loginsession <user> <sessionid>     ║
║  /pwlogin <user> <sessionid>          ║
║  /logout <user>  /accounts            ║
╠═══════════════════════════════════════╣
║  🚀 SPAM                              ║
║  /gspam [speed] [text] ← ALL GCs     ║
║  /gstop                ← stop gspam   ║
║  /smartspam <tgt> <speed> [text]      ║
║  /pwspam <tgt> <speed> [text]         ║
║  /spam [text]   /godspam [text]       ║
║  /picspam                             ║
║  /startspam [text]  /stopspam         ║
╠═══════════════════════════════════════╣
║  🛑 CONTROL                           ║
║  /stop     ← stop all tasks           ║
║  /stopmulti <id|all>                  ║
║  /listmulti                           ║
╠═══════════════════════════════════════╣
║  🏷️  NAME CHANGE                      ║
║  /gcnc [name]  /startnc  /stopnc      ║
║  /startgcnc [name]  /stopgcnc         ║
╠═══════════════════════════════════════╣
║  📊 GC MANAGEMENT                     ║
║  /scangcs  /listgcs                   ║
║  /addgc <id> [name]                   ║
║  /switchgc <id|name>                  ║
║  /gcaddbots  /gcadd <user1,user2>     ║
║  /raid <gc_name> [users]              ║
╠═══════════════════════════════════════╣
║  📈 STATS & SETTINGS                  ║
║  /stats  /owner  /proxystats          ║
║  /setdelay <sec>  /setncdelay <sec>   ║
║  /search <username>                   ║
╠═══════════════════════════════════════╣
║  🔑 ACCESS CONTROL                    ║
║  /allow @user  /remove @user          ║
║  /allowed                             ║
╚═══════════════════════════════════════╝

⚡ speed: slow | medium | fast | unlimited
🎯 targets: all | @group | id1,id2,...
💡 Commands work inside IG GC — no GC arg needed
"""

# ─────────────────────────────────────────────────────────────────────────────
# TELEGRAM CMD ADAPTER — wraps CmdHandler, overrides reply() to Telegram chat
# ─────────────────────────────────────────────────────────────────────────────
class TelegramCmdAdapter(CmdHandler):
    """
    Inherits all CmdHandler command logic.
    reply() sends to Telegram instead of IG thread.
    """
    def __init__(self, eng: Engine, cl: "IGClient", reg: TaskReg,
                 regs: dict, sq: Optional[SendQueue],
                 tg_reply_fn):
        super().__init__(eng, cl, reg, regs, sq)
        self._tg_reply_fn = tg_reply_fn

    async def reply(self, tid: str, text: str):
        try:
            await self._tg_reply_fn(text)
        except Exception as e:
            log.debug(f"TG reply error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# PER-USER TELEGRAM TASK STORE
# ─────────────────────────────────────────────────────────────────────────────
class TgTaskStore:
    def __init__(self):
        self._lock  = threading.Lock()
        self._tasks: Dict[int, Dict[str, asyncio.Task]] = {}

    def add(self, user_id: int, task_id: str, task: asyncio.Task):
        with self._lock:
            self._tasks.setdefault(user_id, {})[task_id] = task

    def stop_all(self, user_id: int) -> int:
        with self._lock:
            tasks = self._tasks.pop(user_id, {})
        count = 0
        for t in tasks.values():
            if not t.done():
                t.cancel()
                count += 1
        return count

    def stop_one(self, user_id: int, task_id: str) -> bool:
        with self._lock:
            tasks = self._tasks.get(user_id, {})
            t = tasks.pop(task_id, None)
        if t and not t.done():
            t.cancel()
            return True
        return False

    def list_tasks(self, user_id: int) -> List[str]:
        with self._lock:
            return list(self._tasks.get(user_id, {}).keys())

    def cleanup_done(self, user_id: int):
        with self._lock:
            tasks = self._tasks.get(user_id, {})
            dead  = [k for k, t in tasks.items() if t.done()]
            for k in dead:
                tasks.pop(k, None)

TG_TASKS = TgTaskStore()

# ─────────────────────────────────────────────────────────────────────────────
# TELEGRAM PANEL — per-user state + keyboard builders
# ─────────────────────────────────────────────────────────────────────────────

# {user_id: {"gc_id": str|None, "gc_name": str, "mode": str,
#            "speed": str, "text": str|None, "awaiting": str|None}}
_PANEL_STATE: Dict[int, Dict] = {}

def _panel_default_state() -> dict:
    return {
        "gc_id":    None,
        "gc_name":  "All GCs",
        "mode":     "spam",
        "speed":    "fast",
        "text":     None,
        "awaiting": None,
        # ── Sasuke Spam sub-panel state ──────────────────────
        "ss_gc_url":  None,   # selected GC URL for sasukespam
        "ss_gc_name": None,   # display name of selected GC
        "ss_target":  None,   # target/opponent name
        "ss_text":    None,   # custom spam text (None = use _OBLIVION_MESSAGES)
        "ss_engines": 4,      # engine count
    }

def _panel_state(user_id: int) -> dict:
    if user_id not in _PANEL_STATE:
        _PANEL_STATE[user_id] = _panel_default_state()
    return _PANEL_STATE[user_id]

# Mode labels & icons
_MODE_LABELS = {
    "spam":  "💬 Spam",
    "god":   "⚡ GodSpam",
    "nc":    "🏷️ NC",
    "pw":    "🎭 PW",
    "pic":   "🖼️ PicSpam",
}
_SPEED_LABELS = {
    "slow":      "🐢 Slow",
    "medium":    "🐇 Medium",
    "fast":      "🚀 Fast",
    "unlimited": "∞ Unlimited",
}

def _build_main_panel(st: dict) -> "InlineKeyboardMarkup":
    gc_name = st["gc_name"] or "No GC"
    mode    = _MODE_LABELS.get(st["mode"], st["mode"])
    speed   = _SPEED_LABELS.get(st["speed"], st["speed"])
    txt     = f'"{st["text"][:20]}…"' if st.get("text") and len(st["text"]) > 20 else (f'"{st["text"]}"' if st.get("text") else "random")
    sess    = _user_session(0)   # placeholder; real session loaded per user
    rows = [
        [InlineKeyboardButton(f"📂 GC: {gc_name}", callback_data="p_gclist:0")],
        [InlineKeyboardButton(f"🔧 Mode: {mode}", callback_data="p_settings"),
         InlineKeyboardButton(f"⚡ Speed: {speed}", callback_data="p_settings")],
        [InlineKeyboardButton(f"📝 Text: {txt}", callback_data="p_settext")],
        # Quick action buttons
        [InlineKeyboardButton("⚡ Ultra Spam", callback_data="p_ultra"),
         InlineKeyboardButton("🔥 NC",         callback_data="p_quicknc"),
         InlineKeyboardButton("💀 Stop All",   callback_data="p_stop")],
        [InlineKeyboardButton("▶️ START", callback_data="p_start"),
         InlineKeyboardButton("⏹ STOP ALL", callback_data="p_stop")],
        [InlineKeyboardButton("📊 Stats",      callback_data="p_stats"),
         InlineKeyboardButton("⚙️ Ultra Cfg",  callback_data="p_ultracfg"),
         InlineKeyboardButton("🔄 Refresh",    callback_data="p_main")],
    ]
    return InlineKeyboardMarkup(rows)


def _build_main_panel_for(st: dict, user_id: int) -> "InlineKeyboardMarkup":
    """Build main panel with per-user session data."""
    gc_name = st["gc_name"] or "No GC"
    mode    = _MODE_LABELS.get(st["mode"], st["mode"])
    speed   = _SPEED_LABELS.get(st["speed"], st["speed"])
    txt     = f'"{st["text"][:20]}…"' if st.get("text") and len(st["text"]) > 20 else (f'"{st["text"]}"' if st.get("text") else "random")
    sess    = _user_session(user_id)
    tabs    = sess.get("tabs", 4)
    burst   = sess.get("burst", 3)
    rows = [
        [InlineKeyboardButton(f"📂 GC: {gc_name}", callback_data="p_gclist:0")],
        [InlineKeyboardButton(f"🔧 Mode: {mode}", callback_data="p_settings"),
         InlineKeyboardButton(f"⚡ Speed: {speed}", callback_data="p_settings")],
        [InlineKeyboardButton(f"📝 Text: {txt}", callback_data="p_settext")],
        # Quick ultra buttons
        [InlineKeyboardButton("⚡ Ultra Spam", callback_data="p_ultra"),
         InlineKeyboardButton("🔥 Quick NC",   callback_data="p_quicknc"),
         InlineKeyboardButton("💀 Stop All",   callback_data="p_stop")],
        # Sasuke Spam entry point
        [InlineKeyboardButton("🔱 Sasuke Spam", callback_data="p_sasuke")],
        [InlineKeyboardButton("▶️ START",     callback_data="p_start"),
         InlineKeyboardButton("⏹ STOP",       callback_data="p_stop")],
        [InlineKeyboardButton(f"🗂 Tabs:{tabs}  Burst:{burst}", callback_data="p_ultracfg")],
        [InlineKeyboardButton("📊 Live Stats", callback_data="p_stats"),
         InlineKeyboardButton("🔄 Refresh",    callback_data="p_main")],
    ]
    return InlineKeyboardMarkup(rows)

def _build_gc_list_keyboard(gcs: list, page: int = 0) -> "InlineKeyboardMarkup":
    per_page = 8
    start = page * per_page
    chunk = gcs[start:start + per_page]
    rows  = []
    for gc in chunk:
        name = (gc.get("name") or gc["id"])[:28]
        rows.append([InlineKeyboardButton(
            f"📌 {name}", callback_data=f"p_gc:{gc['id']}")])
    # Navigation
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀ Prev", callback_data=f"p_gclist:{page-1}"))
    if start + per_page < len(gcs):
        nav.append(InlineKeyboardButton("Next ▶", callback_data=f"p_gclist:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([
        InlineKeyboardButton("🌍 ALL GCs", callback_data="p_gc:ALL"),
        InlineKeyboardButton("◀ Back",    callback_data="p_main"),
    ])
    return InlineKeyboardMarkup(rows)


# ── Sasuke Spam GC picker (uses p_sasuke_gc: prefix) ─────────────────────────
def _build_sasuke_gc_list(gcs: list, page: int = 0) -> "InlineKeyboardMarkup":
    """GC selector keyboard for Sasuke Spam panel (separate from main GC picker)."""
    per_page = 8
    start    = page * per_page
    chunk    = gcs[start:start + per_page]
    rows: List = []
    for gc in chunk:
        name = (gc.get("name") or gc["id"])[:28]
        rows.append([InlineKeyboardButton(
            f"📌 {name}", callback_data=f"p_sasuke_gc:{gc['id']}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀ Prev", callback_data=f"p_sasuke_gclist:{page-1}"))
    if start + per_page < len(gcs):
        nav.append(InlineKeyboardButton("Next ▶", callback_data=f"p_sasuke_gclist:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("◀ Back", callback_data="p_sasuke")])
    return InlineKeyboardMarkup(rows)


def _build_sasuke_panel(st: dict) -> "InlineKeyboardMarkup":
    """
    Sasuke Spam control sub-panel.
    Shows current config and input buttons for GC, target, text, engines.
    Rows:
      [📂 Select GC]
      [🎯 Target: <name>]  [📝 Text: <preview>]
      [🏎️ Engines: N]  [-]  [+]
      [▶️ START]  [⏹ STOP]
      [◀ Back to Panel]
    """
    gc_disp  = (st.get("ss_gc_name") or "⚠️ Not selected")[:24]
    tgt_disp = (st.get("ss_target") or "⚠️ Not set")[:20]
    txt_raw  = st.get("ss_text")
    txt_disp = f'"{txt_raw[:18]}…"' if txt_raw and len(txt_raw) > 18 else (f'"{txt_raw}"' if txt_raw else "auto (160-gap)")
    engines  = st.get("ss_engines", 4)
    rows = [
        [InlineKeyboardButton(f"📂 GC: {gc_disp}", callback_data="p_sasuke_gclist:0")],
        [InlineKeyboardButton(f"🎯 Target: {tgt_disp}", callback_data="p_sasuke_target"),
         InlineKeyboardButton(f"📝 Text: {txt_disp}", callback_data="p_sasuke_text")],
        [InlineKeyboardButton("➖", callback_data="p_sasuke_eng_dec"),
         InlineKeyboardButton(f"🏎️ Engines: {engines}", callback_data="p_noop"),
         InlineKeyboardButton("➕", callback_data="p_sasuke_eng_inc")],
        [InlineKeyboardButton("▶️ START", callback_data="p_sasuke_start"),
         InlineKeyboardButton("⏹ STOP",  callback_data="p_sasuke_stop")],
        [InlineKeyboardButton("◀ Back to Panel", callback_data="p_main")],
    ]
    return InlineKeyboardMarkup(rows)


def _build_settings_keyboard(st: dict) -> "InlineKeyboardMarkup":
    def _m(k): return f"✅ {_MODE_LABELS[k]}" if st["mode"] == k else _MODE_LABELS[k]
    def _s(k): return f"✅ {_SPEED_LABELS[k]}" if st["speed"] == k else _SPEED_LABELS[k]
    rows = [
        [InlineKeyboardButton("── MODE ──", callback_data="p_noop")],
        [InlineKeyboardButton(_m("spam"), callback_data="p_mode:spam"),
         InlineKeyboardButton(_m("god"),  callback_data="p_mode:god")],
        [InlineKeyboardButton(_m("nc"),   callback_data="p_mode:nc"),
         InlineKeyboardButton(_m("pw"),   callback_data="p_mode:pw")],
        [InlineKeyboardButton(_m("pic"),  callback_data="p_mode:pic")],
        [InlineKeyboardButton("── SPEED ──", callback_data="p_noop")],
        [InlineKeyboardButton(_s("slow"),      callback_data="p_speed:slow"),
         InlineKeyboardButton(_s("medium"),    callback_data="p_speed:medium")],
        [InlineKeyboardButton(_s("fast"),      callback_data="p_speed:fast"),
         InlineKeyboardButton(_s("unlimited"), callback_data="p_speed:unlimited")],
        [InlineKeyboardButton("📝 Set Custom Text", callback_data="p_settext")],
        [InlineKeyboardButton("◀ Back to Panel",    callback_data="p_main")],
    ]
    return InlineKeyboardMarkup(rows)


def _build_ultra_cfg_keyboard(user_id: int) -> "InlineKeyboardMarkup":
    """Ultra Engine config panel — tabs per GC, burst size."""
    sess  = _user_session(user_id)
    tabs  = sess.get("tabs", 4)
    burst = sess.get("burst", 3)

    def _t(n): return f"✅ {n}" if tabs == n else str(n)
    def _b(n): return f"✅ {n}" if burst == n else str(n)

    rows = [
        [InlineKeyboardButton("── TABS PER GC ──", callback_data="p_noop")],
        [InlineKeyboardButton(_t(1), callback_data="p_tabs:1"),
         InlineKeyboardButton(_t(2), callback_data="p_tabs:2"),
         InlineKeyboardButton(_t(3), callback_data="p_tabs:3"),
         InlineKeyboardButton(_t(4), callback_data="p_tabs:4"),
         InlineKeyboardButton(_t(5), callback_data="p_tabs:5")],
        [InlineKeyboardButton("── BURST SIZE ──", callback_data="p_noop")],
        [InlineKeyboardButton(_b(1), callback_data="p_burst:1"),
         InlineKeyboardButton(_b(2), callback_data="p_burst:2"),
         InlineKeyboardButton(_b(3), callback_data="p_burst:3"),
         InlineKeyboardButton(_b(5), callback_data="p_burst:5"),
         InlineKeyboardButton(_b(8), callback_data="p_burst:8")],
        [InlineKeyboardButton("── ENGINE COUNT ──", callback_data="p_noop")],
        [InlineKeyboardButton("1 eng", callback_data="p_engines:1"),
         InlineKeyboardButton("2 eng", callback_data="p_engines:2"),
         InlineKeyboardButton("4 eng", callback_data="p_engines:4"),
         InlineKeyboardButton("6 eng", callback_data="p_engines:6"),
         InlineKeyboardButton("8 eng", callback_data="p_engines:8")],
        [InlineKeyboardButton("◀ Back to Panel", callback_data="p_main")],
    ]
    return InlineKeyboardMarkup(rows)


def _build_account_selector(eng: "Engine") -> "InlineKeyboardMarkup":
    """Account selector — shows all active accounts."""
    clients = ACCOUNT_MANAGER.list_active()
    rows    = [[InlineKeyboardButton("── SELECT ACCOUNT ──", callback_data="p_noop")]]
    for cl in clients[:10]:
        rows.append([InlineKeyboardButton(
            f"👤 @{cl.username}", callback_data=f"p_acct:{cl.username}")])
    rows.append([InlineKeyboardButton("🌍 All Accounts", callback_data="p_acct:ALL")])
    rows.append([InlineKeyboardButton("◀ Back",          callback_data="p_main")])
    return InlineKeyboardMarkup(rows)

# ─────────────────────────────────────────────────────────────────────────────
# TELEGRAM CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────
class TelegramController:
    """
    Full Telegram bot controller using python-telegram-bot v21+.
    Runs in a dedicated asyncio event loop on a background thread.
    All IG commands are routed through TelegramCmdAdapter → CmdHandler logic.
    """

    def __init__(self, token: str, eng: Engine, regs: dict):
        self.token   = token
        self.eng     = eng
        self.regs    = regs
        self._app:   Optional[Application] = None
        self._loop:  Optional[asyncio.AbstractEventLoop] = None
        self._reg    = TaskReg()

    # ── auth check ────────────────────────────────────────────────────────────
    def _check_auth(self, update: Update) -> Tuple[bool, str]:
        user     = update.effective_user
        username = (user.username or "").lower() if user else ""
        uid      = user.id if user else 0
        cfg      = self.eng.cfg

        # Numeric owner ID check (most reliable — set via OWNER_TELEGRAM_ID)
        owner_id = int(cfg.get("owner_telegram_id", 0) or 0)
        if owner_id and uid == owner_id:
            return True, username

        owner    = _normalize_username(cfg.get("owner_username", ""))
        allowed  = [_normalize_username(u) for u in cfg.get("allowed_users", [])]
        authorized = (
            (owner and username == owner) or
            username in allowed or
            (owner == "" and allowed == [] and owner_id == 0)
        )
        return authorized, username

    async def _require_auth(self, update: Update) -> bool:
        ok, uname = self._check_auth(update)
        if not ok:
            log.debug(f"⚠ TG unauthorized: @{uname}")
        return ok

    # ── get primary IGClient ──────────────────────────────────────────────────
    def _primary_cl(self) -> Optional["IGClient"]:
        return self.eng.next_client()

    # ── build adapter (creates a TelegramCmdAdapter for one command) ──────────
    def _make_adapter(self, update: Update) -> Optional[TelegramCmdAdapter]:
        cl = self._primary_cl()
        if not cl:
            return None
        chat_id = str(update.effective_chat.id)

        async def tg_reply(text: str):
            try:
                max_len = 4096
                for i in range(0, len(text), max_len):
                    await update.effective_chat.send_message(
                        text[i:i+max_len],
                        parse_mode=None,
                    )
            except Exception as e:
                log.debug(f"TG send error: {e}")

        # Use the primary account's TaskReg
        reg = self.regs.get(cl.username, self._reg)
        return TelegramCmdAdapter(
            eng=self.eng, cl=cl, reg=reg,
            regs=self.regs, sq=None,
            tg_reply_fn=tg_reply,
        )

    # ── route command through unified adapter ─────────────────────────────────
    async def _route(self, update: Update, text: str):
        if not await self._require_auth(update):
            return
        adapter = self._make_adapter(update)
        if not adapter:
            await update.effective_chat.send_message("❌ No IG accounts active. Use /login first.")
            return
        _, sender = self._check_auth(update)
        chat_id = str(update.effective_chat.id)
        await adapter.run(chat_id, text, sender=sender)

    # ── /start ─────────────────────────────────────────────────────────────────
    async def cmd_start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update):
            return
        await update.effective_chat.send_message(TG_MENU_TEXT)

    # ── /help ──────────────────────────────────────────────────────────────────
    async def cmd_help(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update):
            return
        await update.effective_chat.send_message(HELP_MSG)

    # ── /login ─────────────────────────────────────────────────────────────────
    async def cmd_login(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/login " + " ".join(ctx.args or []))

    # ── /loginsession ──────────────────────────────────────────────────────────
    async def cmd_loginsession(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/loginsession " + " ".join(ctx.args or []))

    # ── /logout ────────────────────────────────────────────────────────────────
    async def cmd_logout(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/logout " + " ".join(ctx.args or []))

    # ── /accounts ─────────────────────────────────────────────────────────────
    async def cmd_accounts(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/accounts")

    # ── /pwlogin ──────────────────────────────────────────────────────────────
    async def cmd_pwlogin(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """
        /pwlogin <username> <sessionid>
        Injects sessionid into a Playwright browser context silently (headless).
        Stores session for reuse by /pwspam.
        """
        if not await self._require_auth(update):
            return
        args = ctx.args or []
        if len(args) < 2:
            await update.effective_chat.send_message(
                "Usage: /pwlogin <username> <sessionid>"); return
        username, sessionid = args[0], args[1]
        await update.effective_chat.send_message(
            f"🎭 Creating Playwright session for @{username}… (headless, no browser)")

        if not HAS_PLAYWRIGHT:
            await update.effective_chat.send_message(
                "❌ Playwright not installed.\npip install playwright && playwright install chromium"); return

        if not _PW_ENGINE._ready:
            await update.effective_chat.send_message("⚙️ Starting Playwright browser…")
            await _PW_ENGINE.start()

        try:
            ctx_obj = await _PW_ENGINE._get_or_create_context(username, sessionid)
            if ctx_obj:
                await update.effective_chat.send_message(
                    f"✅ @{username} Playwright context ready.\n"
                    f"Session injected silently — no browser window opened.\n"
                    f"Now use /pwspam to send messages via this session.")
                log.info(f"✅ PW context created for @{username} via Telegram")
            else:
                await update.effective_chat.send_message(f"❌ Failed to create Playwright context for @{username}")
        except Exception as e:
            await update.effective_chat.send_message(f"❌ pwlogin error: {e}")

    # ── /pwspam ───────────────────────────────────────────────────────────────
    async def cmd_pwspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/pwspam " + " ".join(ctx.args or []))

    # ── /sasnc ────────────────────────────────────────────────────────────────
    async def cmd_sasnc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Ultra-fast stylish GC name changer. /sasnc <text>"""
        await self._route(update, "/sasnc " + " ".join(ctx.args or []))

    async def cmd_stopsasnc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/stopsasnc")

    # ── /loginuser ────────────────────────────────────────────────────────────
    async def cmd_loginuser(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/loginuser " + " ".join(ctx.args or []))

    # ── /creategc ─────────────────────────────────────────────────────────────
    async def cmd_creategc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/creategc " + " ".join(ctx.args or []))

    # ── /addbot ───────────────────────────────────────────────────────────────
    async def cmd_addbot(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/addbot " + " ".join(ctx.args or []))

    # ── /promotebots ──────────────────────────────────────────────────────────
    async def cmd_promotebots(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/promotebots " + " ".join(ctx.args or []))

    # ── /pwgo ─────────────────────────────────────────────────────────────────
    async def cmd_pwgo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """
        /pwgo [engines] [text]
        Ultra-fast Playwright multi-engine spam. No rate limit errors.
        engines = 1-8 parallel browser instances (default 4).
        text    = custom spam message (optional).
        Stop with /stopgo.
        """
        await self._route(update, "/pwgo " + " ".join(ctx.args or []))

    # ── /stopgo ───────────────────────────────────────────────────────────────
    async def cmd_stopgo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Stop all /pwgo engines."""
        await self._route(update, "/stopgo")

    # ── /smartspam ────────────────────────────────────────────────────────────
    async def cmd_smartspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/smartspam " + " ".join(ctx.args or []))

    # ── /spam ─────────────────────────────────────────────────────────────────
    async def cmd_spam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """
        /spam <gc_id_or_target> [text]
        """
        if not await self._require_auth(update):
            return
        args = ctx.args or []
        if not args:
            await update.effective_chat.send_message(
                "Usage: /spam <gc_id> [text]\n"
                "Or first use /smartspam all medium [text] to spam all GCs"); return
        await self._route(update, "/spam " + " ".join(args))

    # ── /godspam ──────────────────────────────────────────────────────────────
    async def cmd_godspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/godspam " + " ".join(ctx.args or []))

    # ── /picspam ──────────────────────────────────────────────────────────────
    async def cmd_picspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/picspam")

    # ── /startspam / stopspam ─────────────────────────────────────────────────
    async def cmd_startspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/startspam " + " ".join(ctx.args or []))

    async def cmd_stopspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/stopspam")

    # ── /gspam / gstop ───────────────────────────────────────────────────────
    async def cmd_gspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/gspam " + " ".join(ctx.args or []))

    async def cmd_gstop(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/gstop")

    # ── /panel — inline button control panel ─────────────────────────────────
    async def cmd_panel(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update):
            return
        user_id = update.effective_user.id
        st  = _panel_state(user_id)
        # Pre-load GC list if empty
        cl  = self._primary_cl()
        if cl:
            gcs = self.eng.get_gcs(cl.username)
            if gcs and st["gc_id"] is None:
                st["gc_id"]   = gcs[0]["id"]
                st["gc_name"] = gcs[0].get("name", gcs[0]["id"])
        sess = _user_session(user_id)
        kb  = _build_main_panel_for(st, user_id)
        txt = (
            "🎛️ *ULTRA CONTROL PANEL*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"📂 GC     : {st['gc_name']}\n"
            f"🔧 Mode   : {_MODE_LABELS.get(st['mode'], st['mode'])}\n"
            f"⚡ Speed  : {_SPEED_LABELS.get(st['speed'], st['speed'])}\n"
            f"📝 Text   : {st['text'] or 'random'}\n"
            f"🗂 Tabs   : {sess.get('tabs', 4)} per GC\n"
            f"💥 Burst  : {sess.get('burst', 3)} msgs/tab\n"
            f"🏎️ Engines: {sess.get('engines', 4)}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Ultra Spam · 🔥 Quick NC · 💀 Stop All"
        )
        await update.effective_chat.send_message(txt, reply_markup=kb, parse_mode="Markdown")

    # ── panel callback handler ─────────────────────────────────────────────────
    async def panel_callback(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        if not query:
            return
        await query.answer()

        ok, uname = self._check_auth(update)
        if not ok:
            await query.answer("❌ Unauthorized", show_alert=True)
            return

        user_id = update.effective_user.id
        st  = _panel_state(user_id)
        data = query.data or ""

        async def _edit(text: str, kb):
            try:
                await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
            except Exception:
                pass

        def _panel_text():
            return (
                "🎛️ *CONTROL PANEL*\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"📂 GC   : {st['gc_name']}\n"
                f"🔧 Mode : {_MODE_LABELS.get(st['mode'], st['mode'])}\n"
                f"⚡ Speed: {_SPEED_LABELS.get(st['speed'], st['speed'])}\n"
                f"📝 Text : {st['text'] or 'random'}"
            )

        if data == "p_noop":
            return

        elif data == "p_main":
            await _edit(_panel_text(), _build_main_panel_for(st, user_id))

        elif data.startswith("p_gclist:"):
            page = int(data.split(":")[1])
            cl   = self._primary_cl()
            gcs  = self.eng.get_gcs(cl.username) if cl else []
            if not gcs:
                await query.answer("❌ No GCs. Run /scangcs first.", show_alert=True)
                return
            await _edit(
                f"📂 *Select Group Chat*\n({len(gcs)} GCs found)",
                _build_gc_list_keyboard(gcs, page)
            )

        elif data.startswith("p_gc:"):
            gc_id = data[5:]
            if gc_id == "ALL":
                st["gc_id"]   = None
                st["gc_name"] = "All GCs"
            else:
                cl  = self._primary_cl()
                gcs = self.eng.get_gcs(cl.username) if cl else []
                gc  = next((g for g in gcs if g["id"] == gc_id), None)
                st["gc_id"]   = gc_id
                st["gc_name"] = gc.get("name", gc_id[:16]) if gc else gc_id[:16]
            await _edit(_panel_text(), _build_main_panel(st))

        elif data == "p_settings":
            await _edit(
                "⚙️ *Settings*\nChoose mode and speed:",
                _build_settings_keyboard(st)
            )

        elif data.startswith("p_mode:"):
            st["mode"] = data[7:]
            await _edit(
                "⚙️ *Settings*\nChoose mode and speed:",
                _build_settings_keyboard(st)
            )

        elif data.startswith("p_speed:"):
            st["speed"] = data[8:]
            await _edit(
                "⚙️ *Settings*\nChoose mode and speed:",
                _build_settings_keyboard(st)
            )

        elif data == "p_settext":
            st["awaiting"] = "text"
            await query.edit_message_text(
                "📝 *Send your spam text now.*\n"
                "_(or send `/cancel` to keep random text)_",
                parse_mode="Markdown"
            )

        elif data == "p_start":
            cl = self._primary_cl()
            if not cl:
                await query.answer("❌ No IG accounts active", show_alert=True)
                return

            gc_id   = st.get("gc_id")
            gc_name = st.get("gc_name", "All GCs")
            mode    = st.get("mode", "spam")
            speed   = st.get("speed", "fast")
            custom  = st.get("text")
            reg     = self.regs.get(cl.username, self._reg)
            gcs     = self.eng.get_gcs(cl.username)

            if gc_id and gc_id != "ALL":
                # Single selected GC
                gc_obj = next((g for g in gcs if g["id"] == gc_id), {"id": gc_id, "name": gc_name})
                target_gcs = [gc_obj]
            else:
                target_gcs = gcs

            if not target_gcs:
                await query.answer("❌ No GCs found. Run /scangcs first.", show_alert=True)
                return

            burst = self.eng.cfg.get("smartspam_burst_count", 2)
            label = f"panel_{user_id}"
            reg.stop_key(label)

            if mode == "spam":
                t = asyncio.create_task(
                    worker_smartspam(self.eng, target_gcs, speed=speed, custom=custom, burst_count=burst))
            elif mode == "god":
                gc_o = target_gcs[0]
                t = asyncio.create_task(
                    worker_godspam(self.eng, cl, gc_o["id"], gc_o.get("name","GC"), custom))
            elif mode == "nc":
                t = asyncio.create_task(worker_nc(self.eng, cl, [custom] if custom else None))
            elif mode == "pw":
                t = asyncio.create_task(
                    worker_pwspam(self.eng, target_gcs, speed=speed, custom=custom))
            elif mode == "pic":
                t = asyncio.create_task(worker_pic(self.eng, cl, target_gcs))
            else:
                t = asyncio.create_task(
                    worker_smartspam(self.eng, target_gcs, speed=speed, custom=custom, burst_count=burst))

            task_id = reg.add(t, label)
            dmin, dmax = SPEED_MODES.get(speed, (0.5, 1.0))
            delay_str = "UNLIMITED" if dmax < 0.1 else f"{dmin}-{dmax}s"
            await query.edit_message_text(
                f"🚀 *STARTED*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📂 GC    : {gc_name}\n"
                f"🔧 Mode  : {_MODE_LABELS.get(mode, mode)}\n"
                f"⚡ Speed : {_SPEED_LABELS.get(speed, speed)} ({delay_str})\n"
                f"📝 Text  : {custom or 'random'}\n"
                f"🆔 ID    : {task_id}\n\n"
                f"Press Stop or /gstop to cancel.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⏹ STOP", callback_data="p_stop"),
                    InlineKeyboardButton("◀ Panel", callback_data="p_main"),
                ]])
            )

        elif data == "p_stop":
            cl   = self._primary_cl()
            cnt  = 0
            if cl:
                reg = self.regs.get(cl.username, self._reg)
                reg.stop_key(f"panel_{user_id}")
                reg.stop_key(f"quicknc_{user_id}")
                reg.stop_key("gspam")
                reg.stop_key("spam")
                cnt = TG_TASKS.stop_all(user_id)
            # Also stop any running ultra engine for this user
            user_key = f"ultra_{user_id}"
            await stop_pwgo(user_key)
            TASK_CTRL.stop_all()
            await query.edit_message_text(
                f"💀 *EVERYTHING STOPPED*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"TG tasks : {cnt} cancelled\n"
                f"IG loops : all cancelled\n"
                f"Ultra    : stopped\n"
                f"TASK_CTRL: all stopped",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀ Back to Panel", callback_data="p_main")
                ]])
            )

        elif data == "p_stats":
            ts   = TASK_STATS.snapshot()
            m    = METRICS.snapshot()
            cl   = self._primary_cl()
            acct = len(self.eng._clients)
            gcs  = self.eng.get_gcs(cl.username) if cl else []
            text = (
                f"📊 *Live Stats*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"⏱ Uptime   : {uptime()}\n"
                f"📡 Accounts : {acct}\n"
                f"📂 GCs      : {len(gcs)}\n"
                f"✅ Sent     : {ts['sent']}\n"
                f"❌ Failed   : {ts['failed']}\n"
                f"📈 Msgs/sec : {m['msgs_per_sec']}\n"
                f"📦 Queue    : {m['queue_size']}\n"
                f"🌐 Proxies  : {len(self.eng.proxy_rotator)}"
            )
            await _edit(text, InlineKeyboardMarkup([[
                InlineKeyboardButton("🔄 Refresh", callback_data="p_stats"),
                InlineKeyboardButton("◀ Panel",   callback_data="p_main"),
            ]]))

        # ── ⚡ Ultra Spam quick launch ─────────────────────────────────────────
        elif data == "p_ultra":
            cl      = self._primary_cl()
            if not cl:
                await query.answer("❌ No IG accounts active", show_alert=True)
                return
            sess    = _user_session(user_id)
            gcs     = self.eng.get_gcs(cl.username)
            custom  = st.get("text")
            gc_id   = st.get("gc_id")
            speed   = st.get("speed", "fast")
            tabs    = sess.get("tabs", 4)
            burst   = sess.get("burst", 3)
            engines = sess.get("engines", 4)

            if gc_id and gc_id != "ALL":
                gc_obj = next((g for g in gcs if g["id"] == gc_id), None)
                target_gcs = [gc_obj] if gc_obj else gcs
            else:
                target_gcs = gcs

            if not target_gcs:
                await query.answer("❌ No GCs. Run /scangcs first.", show_alert=True)
                return

            url_list = []
            for gc in target_gcs[:8]:
                gid = gc.get("id", "")
                url_list.append(f"https://www.instagram.com/direct/t/{gid}/")

            user_key = f"ultra_{user_id}"
            await stop_pwgo(user_key)

            pool   = self.eng.cfg.get("emoji_pool", ["⚡"])
            em     = random.choice(pool)
            text_v = custom or fmt(random.choice(SPAM_TEMPLATES),
                                   name=st.get("gc_name","GC"), emoji=em)

            task = asyncio.create_task(
                worker_pwgo(self.eng, url_list, text_v, user_key,
                            engine_count=engines, tabs_per_gc=tabs, burst=burst)
            )
            TG_TASKS.add(user_id, user_key, task)

            total_tabs = engines * tabs * len(url_list)
            await query.edit_message_text(
                f"⚡ *ULTRA SPAM LAUNCHED*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🏎️ Engines  : {engines}\n"
                f"🗂 Tabs/GC  : {tabs}\n"
                f"💥 Burst    : {burst} msgs/tab\n"
                f"🌐 GC URLs  : {len(url_list)}\n"
                f"📊 Total tab: {total_tabs}\n"
                f"⏱ Delay    : 0.01s (auto-adjust)\n"
                f"♻️ Accounts : {len(ACCOUNT_MANAGER.list_active())} round-robin\n\n"
                f"Stop with /stopgo or 💀 Stop All",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💀 STOP ALL", callback_data="p_stop"),
                     InlineKeyboardButton("◀ Panel",    callback_data="p_main")],
                ])
            )

        # ── 🔥 Quick NC ────────────────────────────────────────────────────────
        elif data == "p_quicknc":
            cl = self._primary_cl()
            if not cl:
                await query.answer("❌ No IG accounts active", show_alert=True)
                return
            custom = st.get("text")
            reg    = self.regs.get(cl.username, self._reg)
            reg.stop_key(f"quicknc_{user_id}")
            t = asyncio.create_task(
                worker_nc(self.eng, cl, [custom] if custom else None))
            reg.add(t, f"quicknc_{user_id}")
            await query.edit_message_text(
                f"🔥 *NAME CHANGE STARTED*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Account : @{cl.username}\n"
                f"Text    : {custom or 'random'}\n"
                f"Delay   : 0.01s\n\n"
                f"Stop with /stopnc or 💀 Stop All",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💀 STOP ALL", callback_data="p_stop"),
                     InlineKeyboardButton("◀ Panel",    callback_data="p_main")],
                ])
            )

        # ── ⚙️ Ultra Config ────────────────────────────────────────────────────
        elif data == "p_ultracfg":
            sess = _user_session(user_id)
            tabs  = sess.get("tabs", 4)
            burst = sess.get("burst", 3)
            engines = sess.get("engines", 4)
            await _edit(
                f"⚙️ *ULTRA ENGINE CONFIG*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Current: Engines={engines} | Tabs/GC={tabs} | Burst={burst}\n"
                f"Tabs/GC × Burst × Engines = msgs/cycle\n"
                f"→ {engines} × {tabs} × {burst} = {engines*tabs*burst} msgs/cycle",
                _build_ultra_cfg_keyboard(user_id)
            )

        elif data.startswith("p_tabs:"):
            sess = _user_session(user_id)
            sess["tabs"] = int(data.split(":")[1])
            await _edit(
                f"⚙️ *ULTRA ENGINE CONFIG* — Tabs/GC set to {sess['tabs']}",
                _build_ultra_cfg_keyboard(user_id)
            )

        elif data.startswith("p_burst:"):
            sess = _user_session(user_id)
            sess["burst"] = int(data.split(":")[1])
            await _edit(
                f"⚙️ *ULTRA ENGINE CONFIG* — Burst set to {sess['burst']}",
                _build_ultra_cfg_keyboard(user_id)
            )

        elif data.startswith("p_engines:"):
            sess = _user_session(user_id)
            sess["engines"] = int(data.split(":")[1])
            await _edit(
                f"⚙️ *ULTRA ENGINE CONFIG* — Engines set to {sess['engines']}",
                _build_ultra_cfg_keyboard(user_id)
            )

        # ── 🔱 Sasuke Spam sub-panel ───────────────────────────────────────────
        elif data == "p_sasuke":
            # Show Sasuke sub-panel with current config
            gc_name = st.get("ss_gc_name") or "⚠️ Not selected"
            target  = st.get("ss_target")  or "⚠️ Not set"
            txt_raw = st.get("ss_text")
            txt_d   = f'"{txt_raw[:30]}…"' if txt_raw and len(txt_raw) > 30 else (f'"{txt_raw}"' if txt_raw else "auto (Oblivion 160-gap)")
            engines = st.get("ss_engines", 4)
            await _edit(
                f"🔱 *SASUKE SPAM PANEL*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📂 GC      : {gc_name}\n"
                f"🎯 Target  : {target}\n"
                f"📝 Text    : {txt_d}\n"
                f"🏎️ Engines : {engines}\n"
                f"🧹 Purge   : every {OblivionSpamEngine.SOFT_PURGE_EVERY} msgs\n"
                f"🔒 Locker  : engine 1 locks GC name every {OblivionSpamEngine.LOCK_EVERY} msgs\n"
                f"⏱ Delay   : 0.01s (no rate-limit)\n\n"
                f"➡️ Select GC → set Target → tap START",
                _build_sasuke_panel(st)
            )

        elif data.startswith("p_sasuke_gclist:"):
            # Show GC picker for Sasuke
            page = int(data.split(":")[1])
            cl   = self._primary_cl()
            gcs  = self.eng.get_gcs(cl.username) if cl else []
            if not gcs:
                await query.answer(
                    "❌ No GCs found. Run /scangcs first.", show_alert=True)
                return
            await _edit(
                f"📂 *Select GC for Sasuke Spam*\n({len(gcs)} GCs found)",
                _build_sasuke_gc_list(gcs, page)
            )

        elif data.startswith("p_sasuke_gc:"):
            # Store selected GC in sasuke state
            gc_id = data[len("p_sasuke_gc:"):]
            cl    = self._primary_cl()
            gcs   = self.eng.get_gcs(cl.username) if cl else []
            gc    = next((g for g in gcs if g["id"] == gc_id), None)
            if gc:
                st["ss_gc_url"]  = f"https://www.instagram.com/direct/t/{gc_id}/"
                st["ss_gc_name"] = gc.get("name", gc_id[:20])
            else:
                st["ss_gc_url"]  = f"https://www.instagram.com/direct/t/{gc_id}/"
                st["ss_gc_name"] = gc_id[:20]
            await query.answer(f"✅ GC: {st['ss_gc_name']}", show_alert=False)
            engines = st.get("ss_engines", 4)
            await _edit(
                f"🔱 *SASUKE SPAM PANEL*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📂 GC      : {st['ss_gc_name']}\n"
                f"🎯 Target  : {st.get('ss_target') or '⚠️ Not set'}\n"
                f"📝 Text    : {('\"' + st['ss_text'][:20] + '\"') if st.get('ss_text') else 'auto (Oblivion 160-gap)'}\n"
                f"🏎️ Engines : {engines}\n\n"
                f"✅ GC selected! Now set your target name.",
                _build_sasuke_panel(st)
            )

        elif data == "p_sasuke_target":
            # Prompt user to type target name
            st["awaiting"] = "ss_target"
            await query.edit_message_text(
                "🎯 *SASUKE — Set Target Name*\n\n"
                "Type the opponent/target name:\n"
                "_(This name gets injected into every spam message)_\n\n"
                "Example: `ANSHU` or `HAMZA/ANSHU`\n\n"
                "Send /cancel to go back.",
                parse_mode="Markdown"
            )

        elif data == "p_sasuke_text":
            # Prompt user to type custom spam text
            st["awaiting"] = "ss_text"
            await query.edit_message_text(
                "📝 *SASUKE — Set Spam Text*\n\n"
                "Type your custom spam message:\n"
                "_(Leave blank / send /cancel to use the built-in Oblivion messages)_\n\n"
                "Tip: Type `/cancel` to revert to auto Oblivion messages.",
                parse_mode="Markdown"
            )

        elif data == "p_sasuke_eng_inc":
            st["ss_engines"] = min(8, st.get("ss_engines", 4) + 1)
            await _edit(
                f"🔱 *SASUKE SPAM PANEL*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📂 GC      : {st.get('ss_gc_name') or '⚠️ Not selected'}\n"
                f"🎯 Target  : {st.get('ss_target') or '⚠️ Not set'}\n"
                f"🏎️ Engines : {st['ss_engines']}",
                _build_sasuke_panel(st)
            )

        elif data == "p_sasuke_eng_dec":
            st["ss_engines"] = max(1, st.get("ss_engines", 4) - 1)
            await _edit(
                f"🔱 *SASUKE SPAM PANEL*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📂 GC      : {st.get('ss_gc_name') or '⚠️ Not selected'}\n"
                f"🎯 Target  : {st.get('ss_target') or '⚠️ Not set'}\n"
                f"🏎️ Engines : {st['ss_engines']}",
                _build_sasuke_panel(st)
            )

        elif data == "p_sasuke_start":
            # Validate & launch Sasuke Spam
            gc_url  = st.get("ss_gc_url")
            target  = st.get("ss_target")
            engines = st.get("ss_engines", 4)
            if not gc_url:
                await query.answer("❌ Select a GC first!", show_alert=True)
                return
            if not target:
                await query.answer("❌ Set a target name first!", show_alert=True)
                return
            clients = ACCOUNT_MANAGER.list_active()
            sids    = [cl._sessionid for cl in clients if cl._sessionid]
            if not sids:
                await query.answer(
                    "❌ No active IG sessions. Use /pwlogin first.", show_alert=True)
                return
            gc_name     = f"[{target}] की मां चुदके पागल"
            user_key    = f"sasuke_{user_id}"
            custom_text = st.get("ss_text") or None
            await stop_oblivion(user_key)
            task = asyncio.create_task(
                worker_oblivion(
                    eng=self.eng,
                    url=gc_url,
                    target=target,
                    gc_name=gc_name,
                    user_key=user_key,
                    engine_count=engines,
                    delay=0.01,
                    sids=sids,
                    custom_text=custom_text,
                )
            )
            TG_TASKS.add(user_id, user_key, task)
            await query.edit_message_text(
                f"🔱 *SASUKE SPAM LAUNCHED!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📂 GC      : {st.get('ss_gc_name')}\n"
                f"🎯 Target  : {target}\n"
                f"🏎️ Engines : {engines}\n"
                f"🔒 Locker  : Engine 1 (name reset every {OblivionSpamEngine.LOCK_EVERY} msgs)\n"
                f"🧹 Purge   : DOM reload every {OblivionSpamEngine.SOFT_PURGE_EVERY} msgs\n"
                f"⏱ Delay   : 0.01s\n"
                f"📱 Sessions: {len(sids)}\n"
                f"📨 Payload : 160-line gap messages\n\n"
                f"🛑 Tap STOP below or /stopsasuke",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏹ STOP SASUKE", callback_data="p_sasuke_stop"),
                     InlineKeyboardButton("◀ Panel",       callback_data="p_main")],
                ])
            )

        elif data == "p_sasuke_stop":
            user_key = f"sasuke_{user_id}"
            stopped  = await stop_oblivion(user_key)
            TG_TASKS.stop_all(user_id)
            await query.answer(
                "🛑 Sasuke Spam stopped." if stopped else "⚠️ Not running.",
                show_alert=True)
            await _edit(
                f"🔱 *SASUKE SPAM PANEL*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📂 GC      : {st.get('ss_gc_name') or '⚠️ Not selected'}\n"
                f"🎯 Target  : {st.get('ss_target') or '⚠️ Not set'}\n"
                f"🏎️ Engines : {st.get('ss_engines', 4)}\n\n"
                f"{'🛑 Stopped.' if stopped else '⚠️ Was not running.'}",
                _build_sasuke_panel(st)
            )

        # ── Account selector ───────────────────────────────────────────────────
        elif data == "p_accounts":
            await _edit(
                "👤 *SELECT ACCOUNT*\nChoose which account to use:",
                _build_account_selector(self.eng)
            )

        elif data.startswith("p_acct:"):
            acct_name = data[7:]
            sess = _user_session(user_id)
            if acct_name == "ALL":
                sess["account"] = None
                await query.answer("✅ Using all accounts (round-robin)", show_alert=False)
            else:
                sess["account"] = acct_name
                await query.answer(f"✅ Account set to @{acct_name}", show_alert=False)
            await _edit(
                f"🎛️ *CONTROL PANEL*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📂 GC   : {st['gc_name']}\n"
                f"🔧 Mode : {_MODE_LABELS.get(st['mode'], st['mode'])}\n"
                f"⚡ Speed: {_SPEED_LABELS.get(st['speed'], st['speed'])}\n"
                f"📝 Text : {st['text'] or 'random'}\n"
                f"👤 Acct : {sess['account'] or 'All (round-robin)'}",
                _build_main_panel_for(st, user_id)
            )

    # ── /gcnc ─────────────────────────────────────────────────────────────────
    async def cmd_gcnc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/gcnc " + " ".join(ctx.args or []))

    async def cmd_startnc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/startnc " + " ".join(ctx.args or []))

    async def cmd_stopnc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/stopnc")

    async def cmd_startgcnc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/startgcnc " + " ".join(ctx.args or []))

    async def cmd_stopgcnc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/stopgcnc")

    # ── /scangcs / listgcs / addgc / switchgc ────────────────────────────────
    async def cmd_scangcs(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/scangcs")

    async def cmd_listgcs(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/listgcs")

    async def cmd_addgc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/addgc " + " ".join(ctx.args or []))

    async def cmd_switchgc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/switchgc " + " ".join(ctx.args or []))

    # ── /gcaddbots / gcadd ────────────────────────────────────────────────────
    async def cmd_gcaddbots(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/gcaddbots")

    async def cmd_gcadd(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/gcadd " + " ".join(ctx.args or []))

    # ── /raid ─────────────────────────────────────────────────────────────────
    async def cmd_raid(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/raid " + " ".join(ctx.args or []))

    # ── /multinc ──────────────────────────────────────────────────────────────
    async def cmd_multinc(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/multinc " + " ".join(ctx.args or []))

    # ── /multispam / multipicspam ─────────────────────────────────────────────
    async def cmd_multispam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/multispam " + " ".join(ctx.args or []))

    async def cmd_multipicspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/multipicspam " + " ".join(ctx.args or []))

    # ── /stopmulti / listmulti ────────────────────────────────────────────────
    async def cmd_stopmulti(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/stopmulti " + " ".join(ctx.args or []))

    async def cmd_listmulti(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/listmulti")

    # ── /stop ─────────────────────────────────────────────────────────────────
    async def cmd_stop(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Cancel ALL tasks for this Telegram user."""
        if not await self._require_auth(update):
            return
        user_id = update.effective_user.id

        # Cancel per-user TG tasks
        tg_count = TG_TASKS.stop_all(user_id)

        # Cancel all tasks in the primary account's TaskReg
        cl = self._primary_cl()
        ig_count = 0
        if cl:
            reg = self.regs.get(cl.username)
            if reg:
                reg.stop_all()
                ig_count = reg.count()

        await update.effective_chat.send_message(
            f"🛑 Stopped {tg_count} TG tasks + all IG tasks.\n"
            f"All spam/nc/picspam loops cancelled.")

    # ── /stats ────────────────────────────────────────────────────────────────
    async def cmd_stats(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not await self._require_auth(update):
            return
        ts   = TASK_STATS.snapshot()
        m    = METRICS.snapshot()
        cl   = self._primary_cl()
        cpu  = f"CPU: {m['cpu_percent']}%" if m["cpu_percent"] is not None else ""
        mem  = f"MEM: {m['mem_percent']}%" if m["mem_percent"] is not None else ""

        running_tasks = [
            k for k, v in ts["tasks"].items() if v.get("running")
        ]
        task_lines = ""
        for tid in running_tasks[:5]:
            tv = ts["tasks"][tid]
            task_lines += f"\n  {tid}: sent={tv['sent']} fail={tv['failed']}"
        if len(running_tasks) > 5:
            task_lines += f"\n  …+{len(running_tasks)-5} more"

        text = (
            f"📊 NIGGA SYSTEM v8.0 STATS\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⏱ Uptime      : {uptime()}\n"
            f"📡 Accounts   : {len(self.eng._clients)}\n"
            f"🌐 Proxies    : {len(self.eng.proxy_rotator)}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✅ Total Sent  : {ts['sent']}\n"
            f"❌ Total Failed: {ts['failed']}\n"
            f"📈 Msgs/sec    : {m['msgs_per_sec']}\n"
            f"📦 Queue       : {m['queue_size']}\n"
            f"⚙️  Workers    : {m['workers_active']}/{m['workers_total']}\n"
            f"🎭 Playwright  : {m['playwright_sends']}\n"
            f"🔀 Proxy swaps : {m['proxy_switches']}\n"
            f"🔥 Active tasks: {len(running_tasks)}{task_lines}\n"
            f"🖥  {cpu} {mem}"
        )
        await update.effective_chat.send_message(text)

    # ── /owner ────────────────────────────────────────────────────────────────
    async def cmd_owner(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/owner")

    # ── /proxystats ───────────────────────────────────────────────────────────
    async def cmd_proxystats(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/proxystats")

    # ── /authenticate ─────────────────────────────────────────────────────────
    async def cmd_authenticate(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/authenticate " + " ".join(ctx.args or []))

    # ── /allow / remove / allowed ─────────────────────────────────────────────
    async def cmd_allow(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/allow " + " ".join(ctx.args or []))

    async def cmd_remove(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/remove " + " ".join(ctx.args or []))

    async def cmd_allowed(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/allowed")

    # ── /search ───────────────────────────────────────────────────────────────
    async def cmd_search(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/search " + " ".join(ctx.args or []))

    # ── /setdelay / setncdelay ────────────────────────────────────────────────
    async def cmd_setdelay(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/setdelay " + " ".join(ctx.args or []))

    async def cmd_setncdelay(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/setncdelay " + " ".join(ctx.args or []))

    # ── /animevoice ───────────────────────────────────────────────────────────
    async def cmd_animevoice(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/animevoice " + " ".join(ctx.args or []))

    # ── /addgroup / listgroups ────────────────────────────────────────────────
    async def cmd_addgroup(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/addgroup " + " ".join(ctx.args or []))

    async def cmd_listgroups(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/listgroups")

    # ── /startpicspam / stoppicspam ───────────────────────────────────────────
    async def cmd_startpicspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/startpicspam")

    async def cmd_stoppicspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/stoppicspam")

    async def cmd_stopgodspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await self._route(update, "/stopgodspam " + " ".join(ctx.args or []))

    # ── /sasukespam — 🔱 Sasuke Spam (Oblivion Titan V44 engine) ────────────
    async def cmd_sasukespam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """
        /sasukespam <target> <gc_url_or_id> [engines] [delay]
        Fast Playwright spam with target name injection, 160-line gap messages,
        DOM soft-purge every 30 msgs, name-locker on engine 1.
        target  : opponent name injected into every message
        gc_url  : Instagram direct GC URL or gc_id
        engines : parallel engine count (default 4)
        delay   : seconds between messages (default 0.01)
        Stop with /stopsasuke
        """
        if not await self._require_auth(update):
            return
        args = ctx.args or []
        if len(args) < 2:
            await update.effective_chat.send_message(
                "Usage: /sasukespam <target> <gc_url> [engines] [delay]\n"
                "Example: /sasukespam ANSHU https://www.instagram.com/direct/t/123456/ 4 0.01\n"
                "Or use /panel → 🔱 Sasuke Spam for interactive GC picker.")
            return

        target  = args[0]
        raw_url = args[1]
        engines = int(args[2]) if len(args) > 2 and args[2].isdigit() else 4
        delay   = float(args[3]) if len(args) > 3 else 0.01

        # Accept bare gc_id (digits) or full URL
        if raw_url.isdigit():
            gc_url = f"https://www.instagram.com/direct/t/{raw_url}/"
        elif raw_url.startswith("http"):
            gc_url = raw_url
        else:
            await update.effective_chat.send_message(
                "❌ Invalid URL. Use full URL or a numeric GC ID.")
            return

        user_id  = update.effective_user.id
        gc_name  = f"[{target}] की मां चुदके पागल"
        user_key = f"sasuke_{user_id}"

        clients = ACCOUNT_MANAGER.list_active()
        sids    = [cl._sessionid for cl in clients if cl._sessionid]
        if not sids:
            await update.effective_chat.send_message(
                "❌ No active IG sessions. Use /pwlogin <user> <sessionid> first.")
            return

        await stop_oblivion(user_key)

        task = asyncio.create_task(
            worker_oblivion(
                eng=self.eng,
                url=gc_url,
                target=target,
                gc_name=gc_name,
                user_key=user_key,
                engine_count=engines,
                delay=delay,
                sids=sids,
            )
        )
        TG_TASKS.add(user_id, user_key, task)

        await update.effective_chat.send_message(
            f"🔱 SASUKE SPAM LAUNCHED\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🎯 Target   : {target}\n"
            f"🌐 GC URL   : {gc_url[-40:]}\n"
            f"🏎️ Engines  : {engines}\n"
            f"🔒 Engine 1 : LOCKER (name reset every {OblivionSpamEngine.LOCK_EVERY} msgs)\n"
            f"🧹 Purge    : DOM reload every {OblivionSpamEngine.SOFT_PURGE_EVERY} msgs\n"
            f"⏱ Delay    : {delay}s\n"
            f"📱 Sessions : {len(sids)}\n"
            f"📨 Payload  : 160-line gap messages\n\n"
            f"Stop with /stopsasuke"
        )

    # ── /stopsasuke — stop Sasuke Spam engine ────────────────────────────────
    async def cmd_stopsasuke(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """Stop all /sasukespam engines for this user."""
        if not await self._require_auth(update):
            return
        user_id  = update.effective_user.id
        user_key = f"sasuke_{user_id}"
        stopped  = await stop_oblivion(user_key)
        TG_TASKS.stop_all(user_id)
        await update.effective_chat.send_message(
            "🛑 Sasuke Spam stopped." if stopped else
            "⚠️ No Sasuke Spam session running."
        )

    # ── /ultraspam — ⚡ one-shot ultra engine launch from command ──────────────
    async def cmd_ultraspam(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """
        /ultraspam [engines] [tabs] [burst] [text]
        Launches TRUE ULTRA ENGINE directly.
        engines=4 tabs=4 burst=3 by default (args optional).
        Reads GC list from panel state / eng GC store.
        Stop with /stopgo.
        """
        if not await self._require_auth(update):
            return
        args    = ctx.args or []
        user_id = update.effective_user.id
        sess    = _user_session(user_id)
        st      = _panel_state(user_id)

        engines = int(args[0]) if args and args[0].isdigit() else sess.get("engines", 4)
        tabs    = int(args[1]) if len(args) > 1 and args[1].isdigit() else sess.get("tabs", 4)
        burst   = int(args[2]) if len(args) > 2 and args[2].isdigit() else sess.get("burst", 3)
        custom  = " ".join(args[3:]) if len(args) > 3 else st.get("text")

        cl  = self._primary_cl()
        if not cl:
            await update.effective_chat.send_message("❌ No IG accounts active. Use /login first.")
            return

        gcs = self.eng.get_gcs(cl.username)
        if not gcs:
            await update.effective_chat.send_message(
                "❌ No GCs found. Run /scangcs first.")
            return

        url_list = [
            f"https://www.instagram.com/direct/t/{gc['id']}/"
            for gc in gcs[:8]
        ]

        pool   = self.eng.cfg.get("emoji_pool", ["⚡"])
        em     = random.choice(pool)
        text_v = custom or fmt(random.choice(SPAM_TEMPLATES),
                               name=st.get("gc_name", "GC"), emoji=em)

        user_key = f"ultra_{user_id}"
        await stop_pwgo(user_key)

        task = asyncio.create_task(
            worker_pwgo(self.eng, url_list, text_v, user_key,
                        engine_count=engines, tabs_per_gc=tabs, burst=burst)
        )
        TG_TASKS.add(user_id, user_key, task)

        total_tabs = engines * tabs * len(url_list)
        await update.effective_chat.send_message(
            f"⚡ ULTRA ENGINE STARTED\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Engines  : {engines}\n"
            f"Tabs/GC  : {tabs}\n"
            f"Burst    : {burst} msgs/tab/cycle\n"
            f"GC URLs  : {len(url_list)}\n"
            f"Total tab: {total_tabs}\n"
            f"Delay    : 0.01s zero-jitter (auto-adjusts)\n"
            f"Accounts : {len(ACCOUNT_MANAGER.list_active())} round-robin\n"
            f"Text     : {text_v[:50] if text_v else 'random'}\n\n"
            f"Stop with /stopgo"
        )

    # ── /stopall — 💀 kill everything instantly ───────────────────────────────
    async def cmd_stopall(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """
        /stopall
        Kills ALL tasks: TG tasks, IG loops, ultra engine, TASK_CTRL.
        """
        if not await self._require_auth(update):
            return
        user_id  = update.effective_user.id
        tg_count = TG_TASKS.stop_all(user_id)
        user_key = f"ultra_{user_id}"
        await stop_pwgo(user_key)
        cl = self._primary_cl()
        if cl:
            reg = self.regs.get(cl.username)
            if reg:
                reg.stop_all()
        TASK_CTRL.stop_all()
        await update.effective_chat.send_message(
            f"💀 ALL STOPPED\n"
            f"TG tasks: {tg_count} | IG loops: all | Ultra: stopped"
        )

    # ── /ultracfg — ⚙️ configure ultra engine settings ───────────────────────
    async def cmd_ultracfg(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        """
        /ultracfg [engines] [tabs] [burst]
        Set ultra engine parameters.
        """
        if not await self._require_auth(update):
            return
        args    = ctx.args or []
        user_id = update.effective_user.id
        sess    = _user_session(user_id)
        changed = []
        if len(args) >= 1 and args[0].isdigit():
            sess["engines"] = max(1, min(8, int(args[0])))
            changed.append(f"Engines={sess['engines']}")
        if len(args) >= 2 and args[1].isdigit():
            sess["tabs"] = max(1, min(5, int(args[1])))
            changed.append(f"Tabs/GC={sess['tabs']}")
        if len(args) >= 3 and args[2].isdigit():
            sess["burst"] = max(1, min(10, int(args[2])))
            changed.append(f"Burst={sess['burst']}")
        engines = sess.get("engines", 4)
        tabs    = sess.get("tabs", 4)
        burst   = sess.get("burst", 3)
        await update.effective_chat.send_message(
            f"⚙️ ULTRA CONFIG\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Engines : {engines}\n"
            f"Tabs/GC : {tabs}\n"
            f"Burst   : {burst}\n"
            f"→ {engines} × {tabs} × {burst} = {engines*tabs*burst} msgs/cycle\n"
            + (f"\nUpdated: {', '.join(changed)}" if changed else "\nNo changes (pass: engines tabs burst)")
        )

    # ── text message passthrough (non-command DM) ─────────────────────────────
    async def on_message(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        text    = update.message.text.strip()
        user_id = update.effective_user.id if update.effective_user else 0

        # ── Panel text-input state machine ──────────────────────────────────
        if user_id and user_id in _PANEL_STATE:
            st = _PANEL_STATE[user_id]
            awaiting = st.get("awaiting")

            if awaiting == "text":
                st["awaiting"] = None
                if text.lower() == "/cancel":
                    st["text"] = None
                    await update.message.reply_text("✅ Text cleared — will use random templates.")
                else:
                    st["text"] = text
                    await update.message.reply_text(
                        f"✅ Text saved: \"{text[:60]}{'…' if len(text)>60 else ''}\"\n"
                        f"Use /panel to open the control panel.",
                    )
                return  # Consumed

            elif awaiting == "ss_target":
                st["awaiting"] = None
                if text.lower() == "/cancel":
                    await update.message.reply_text(
                        "↩️ Cancelled. Open /panel → 🔱 Sasuke Spam to continue.")
                else:
                    st["ss_target"] = text.strip()
                    tgt = st["ss_target"]
                    await update.message.reply_text(
                        f"✅ Target set: *{tgt}*\n\n"
                        f"Every message will say: `[{tgt}] की मां ...`\n"
                        f"Open /panel → 🔱 Sasuke Spam to set text or hit START.",
                        parse_mode="Markdown"
                    )
                return  # Consumed

            elif awaiting == "ss_text":
                st["awaiting"] = None
                if text.lower() == "/cancel":
                    st["ss_text"] = None
                    await update.message.reply_text(
                        "✅ Custom text cleared — will use built-in Oblivion messages.\n"
                        "Open /panel → 🔱 Sasuke Spam.")
                else:
                    st["ss_text"] = text.strip()
                    await update.message.reply_text(
                        f"✅ Custom text set: \"{text[:60]}{'…' if len(text)>60 else ''}\"\n"
                        f"Open /panel → 🔱 Sasuke Spam to continue.",
                    )
                return  # Consumed

        if text.startswith("/"):
            await self._route(update, text)

    # ── build and run the bot ─────────────────────────────────────────────────
    def build_app(self) -> Application:
        app = ApplicationBuilder().token(self.token).build()

        handlers = [
            ("start",         self.cmd_start),
            ("help",          self.cmd_help),
            ("login",         self.cmd_login),
            ("loginsession",  self.cmd_loginsession),
            ("pwlogin",       self.cmd_pwlogin),
            ("logout",        self.cmd_logout),
            ("accounts",      self.cmd_accounts),
            ("pwspam",        self.cmd_pwspam),
            ("pwgo",          self.cmd_pwgo),
            ("sasnc",         self.cmd_sasnc),
            ("stopsasnc",     self.cmd_stopsasnc),
            ("loginuser",     self.cmd_loginuser),
            ("creategc",      self.cmd_creategc),
            ("addbot",        self.cmd_addbot),
            ("promotebots",   self.cmd_promotebots),
            ("stopgo",        self.cmd_stopgo),
            ("smartspam",     self.cmd_smartspam),
            ("spam",          self.cmd_spam),
            ("godspam",       self.cmd_godspam),
            ("picspam",       self.cmd_picspam),
            ("startspam",     self.cmd_startspam),
            ("stopspam",      self.cmd_stopspam),
            ("gcnc",          self.cmd_gcnc),
            ("startnc",       self.cmd_startnc),
            ("stopnc",        self.cmd_stopnc),
            ("startgcnc",     self.cmd_startgcnc),
            ("stopgcnc",      self.cmd_stopgcnc),
            ("scangcs",       self.cmd_scangcs),
            ("listgcs",       self.cmd_listgcs),
            ("addgc",         self.cmd_addgc),
            ("switchgc",      self.cmd_switchgc),
            ("gcaddbots",     self.cmd_gcaddbots),
            ("gcadd",         self.cmd_gcadd),
            ("raid",          self.cmd_raid),
            ("multinc",       self.cmd_multinc),
            ("multispam",     self.cmd_multispam),
            ("multipicspam",  self.cmd_multipicspam),
            ("stopmulti",     self.cmd_stopmulti),
            ("listmulti",     self.cmd_listmulti),
            ("stop",          self.cmd_stop),
            ("stats",         self.cmd_stats),
            ("owner",         self.cmd_owner),
            ("proxystats",    self.cmd_proxystats),
            ("authenticate",  self.cmd_authenticate),
            ("allow",         self.cmd_allow),
            ("remove",        self.cmd_remove),
            ("allowed",       self.cmd_allowed),
            ("search",        self.cmd_search),
            ("setdelay",      self.cmd_setdelay),
            ("setncdelay",    self.cmd_setncdelay),
            ("animevoice",    self.cmd_animevoice),
            ("addgroup",      self.cmd_addgroup),
            ("listgroups",    self.cmd_listgroups),
            ("startpicspam",  self.cmd_startpicspam),
            ("stoppicspam",   self.cmd_stoppicspam),
            ("stopgodspam",   self.cmd_stopgodspam),
            ("gspam",         self.cmd_gspam),
            ("gstop",         self.cmd_gstop),
            ("panel",         self.cmd_panel),
            # ── TRUE ULTRA ENGINE commands ────────────────────────────────────
            ("ultraspam",     self.cmd_ultraspam),
            ("stopall",       self.cmd_stopall),
            ("ultracfg",      self.cmd_ultracfg),
            # ── SASUKE SPAM ENGINE ───────────────────────────────────────────
            ("sasukespam",    self.cmd_sasukespam),
            ("stopsasuke",    self.cmd_stopsasuke),
        ]

        for cmd_name, handler_fn in handlers:
            app.add_handler(TGCommandHandler(cmd_name, handler_fn))

        # Inline button callback handler (panel)
        app.add_handler(CallbackQueryHandler(self.panel_callback))

        app.add_handler(
            TGMessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, self.on_message)
        )

        self._app = app
        return app

    async def run_async(self):
        app = self.build_app()
        log.info("🤖 Telegram bot starting…")
        await app.initialize()
        await app.start()
        await app.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        log.info(f"✅ Telegram bot live — send /start to your bot")

        # Keep running until eng stops
        while self.eng.running:
            await asyncio.sleep(1)

        await app.updater.stop()
        await app.stop()
        await app.shutdown()

    def start_in_thread(self):
        def _run():
            if HAS_UVLOOP:
                lp = uvloop.new_event_loop()
            else:
                lp = asyncio.new_event_loop()
            asyncio.set_event_loop(lp)
            try:
                lp.run_until_complete(self.run_async())
            except Exception as e:
                log.error(f"❌ Telegram bot crashed: {e}")
            finally:
                lp.close()

        t = threading.Thread(target=_run, name="telegram-bot", daemon=True)
        t.start()
        return t

# ─────────────────────────────────────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────────────────────────────────────
def banner(cfg: dict, proxy_rotator: ProxyRotator):
    log.info("═" * 72)
    log.info("  NIGGA SYSTEM v8.0 – TELEGRAM+IG DUAL CTRL · SMARTSPAM · STATS")
    log.info("═" * 72)
    owner   = cfg.get("owner_username", "<set via /authenticate>")
    allowed = cfg.get("allowed_users", [])
    tg_tok  = cfg.get("telegram_bot_token", "")
    log.info(f"  Owner         : @{owner}")
    log.info(f"  Allowed users : {len(allowed)} configured")
    log.info(f"  Private mode  : {cfg.get('private_mode', True)}")
    log.info(f"  Spam Tpl      : {len(SPAM_TEMPLATES)}")
    log.info(f"  Workers       : {cfg.get('send_concurrency', 64)} initial (auto-scales)")
    log.info(f"  Poll Interval : {cfg.get('cmd_poll_interval', 1.0)}s")
    log.info(f"  Burst Size    : {cfg.get('burst_size', 64)} msgs/cycle")
    log.info(f"  Session Ref   : every {cfg.get('session_refresh_interval', 300)}s")
    log.info(f"  Proxies       : {len(proxy_rotator)} loaded")
    log.info(f"  Telegram bot  : {'✅ token configured' if tg_tok else '⚠️  no token — set telegram_bot_token in config.json'}")
    log.info(f"  Playwright    : {'✅' if HAS_PLAYWRIGHT else '❌ pip install playwright'}")
    log.info(f"  python-telegram-bot: {'✅' if HAS_TELEGRAM else '❌ pip install python-telegram-bot'}")
    log.info(f"  uvloop        : {'✅' if HAS_UVLOOP   else '❌ pip install uvloop'}")
    log.info(f"  aiohttp       : {'✅' if HAS_AIOHTTP  else '❌ pip install aiohttp'}")
    log.info(f"  orjson        : {'✅' if HAS_ORJSON   else '❌ pip install orjson'}")
    log.info("═" * 72)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="NIGGA SYSTEM v8.0")
    parser.add_argument("--api", action="store_true", help="Enable FastAPI gateway mode")
    parser.add_argument("--api-port", type=int, default=8080, help="FastAPI port (default: 8080)")
    parser.add_argument("--no-playwright", action="store_true", help="Disable Playwright fallback")
    parser.add_argument("--telegram", action="store_true", help="Enable Telegram bot (requires telegram_bot_token in config.json)")
    parser.add_argument("--tg-token", default="", help="Telegram bot token (overrides config.json)")
    parser.add_argument("--no-stats-printer", action="store_true", help="Disable console stats printer")
    args = parser.parse_args()

    cfg  = load_cfg()

    if args.api:
        cfg["api_gateway_mode"] = True
        cfg["api_gateway_port"] = args.api_port
    if args.no_playwright:
        cfg["use_playwright_fallback"] = False

    # Top-of-file quick-config values take priority over config.json
    if TELEGRAM_BOT_TOKEN:
        cfg["telegram_bot_token"] = TELEGRAM_BOT_TOKEN
    if OWNER_TELEGRAM_ID:
        cfg["owner_telegram_id"] = OWNER_TELEGRAM_ID

    # CLI token overrides everything
    if args.tg_token:
        cfg["telegram_bot_token"] = args.tg_token

    # --telegram flag auto-enables if token is present
    tg_token = cfg.get("telegram_bot_token", "").strip()
    use_telegram = (args.telegram or bool(tg_token)) and bool(tg_token)

    proxy_rotator = ProxyRotator.from_file(cfg.get("proxy_file", "proxies.txt"))

    banner(cfg, proxy_rotator)

    eng  = Engine(cfg, proxy_rotator)
    eng.load_groups()
    eng.load_gcgroups()

    accounts = cfg.get("accounts", [])
    if not accounts:
        accounts = _console_login_menu(cfg)
        if accounts:
            cfg["accounts"] = accounts
            save_cfg(cfg)

    if not accounts:
        log.error("❌ No accounts configured.")
        sys.exit(1)

    regs: Dict[str, TaskReg] = {}

    # Initialize the global CommandExecutor singleton
    global _CMD_EXEC
    _CMD_EXEC = CommandExecutor(eng, regs)
    log.info("⚡ CommandExecutor (ULTRA ENGINE backend) initialized")

    threading.Thread(
        target=_status_writer, args=(eng, regs), name="status-writer", daemon=True
    ).start()

    threading.Thread(
        target=heartbeat, args=(eng, regs), name="heartbeat", daemon=True
    ).start()

    if cfg.get("api_gateway_mode"):
        _start_api_gateway(eng, cfg.get("api_gateway_port", 8080))

    def _shutdown(sig, frame):
        log.info("🛑 Shutting down…")
        eng.running = False

    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    for acct in accounts:
        if not acct.get("enabled", True):
            continue
        uname = acct["username"]
        reg   = TaskReg()
        regs[uname] = reg
        t = threading.Thread(
            target=thread_account,
            args=(eng, acct, reg, regs),
            name=f"acct-{uname}",
            daemon=True,
        )
        t.start()
        log.info(f"🚀 Started account thread: @{uname}")

    # Init Playwright in background (headless, async)
    if cfg.get("use_playwright_fallback", True) and HAS_PLAYWRIGHT:
        async def _init_pw():
            await _PW_ENGINE.start()
        def _pw_thread():
            lp = asyncio.new_event_loop()
            lp.run_until_complete(_init_pw())
        threading.Thread(target=_pw_thread, name="playwright-init", daemon=True).start()

    # Start Telegram bot in background thread
    if use_telegram:
        if not HAS_TELEGRAM:
            log.error("❌ python-telegram-bot not installed. pip install python-telegram-bot")
        else:
            tg_ctrl = TelegramController(tg_token, eng, regs)
            tg_ctrl.start_in_thread()
            log.info(f"🤖 Telegram bot started — send /start to your bot")
    else:
        if not tg_token:
            log.info("ℹ️  Telegram bot not started — set telegram_bot_token in config.json or use --tg-token")

    # Stats printer — runs in a background thread with its own event loop
    if not args.no_stats_printer:
        def _stats_thread():
            lp = asyncio.new_event_loop()
            asyncio.set_event_loop(lp)
            try:
                lp.run_until_complete(stats_printer(eng))
            finally:
                lp.close()
        threading.Thread(target=_stats_thread, name="stats-printer", daemon=True).start()

    active_count = len([a for a in accounts if a.get("enabled", True)])
    log.info(f"✅ {active_count} account(s) starting…")
    log.info("   • IG DM commands:  send /help to your bot account")
    if use_telegram:
        log.info("   • Telegram:        send /start to your Telegram bot")
    log.info("   • Console stats:   live Sent/Failed/Msgs-per-sec updates")

    try:
        while eng.running:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("🛑 KeyboardInterrupt — shutting down.")
        eng.running = False

    if _PW_ENGINE._ready:
        async def _stop_pw():
            await _PW_ENGINE.stop()
        asyncio.run(_stop_pw())

    log.info("👋 Bot stopped.")


if __name__ == "__main__":
    main()
