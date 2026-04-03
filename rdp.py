import os
import time
import re
import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

# ==================== SPYTHER v1 BANNER ====================
try:
    from cfonts import render
except ImportError:
    print("pip install python-cfonts")
    render = None

MOBILE_UA = "Mozilla/5.0 (Linux; Android 13; vivo V60) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
MOBILE_VIEWPORT = {"width": 412, "height": 915}

LAUNCH_ARGS = [
    "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu",
    "--disable-extensions", "--disable-sync", "--mute-audio"
]

ACCOUNTS_FILE = "instagram_accounts.json"
PAIRS_FILE = "account_pairs.json"

def print_spyther_banner():
    if render:
        try:
            output = render('SPYTHER v1', font='block', colors=['cyan', 'yellow'], align='center')
            print(output)
        except:
            pass
    print("═" * 85)
    print("              Instagram DM Auto Sender - Multi Account Switcher")
    print("                 Pairs + Single Mode + Session ID Only")
    print("═" * 85)

def load_accounts():
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(accounts, f, indent=2)

def load_pairs():
    if os.path.exists(PAIRS_FILE):
        try:
            with open(PAIRS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_pairs(pairs):
    with open(PAIRS_FILE, 'w', encoding='utf-8') as f:
        json.dump(pairs, f, indent=2)

async def validate_sessionid(sessionid: str):
    """Real validation using direct cookie injection"""
    print("Validating sessionid on Instagram...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=LAUNCH_ARGS)
            context = await browser.new_context(
                user_agent=MOBILE_UA,
                viewport=MOBILE_VIEWPORT,
                is_mobile=True,
                has_touch=True,
                device_scale_factor=2,
                color_scheme="dark"
            )
            cookies = [{
                "name": "sessionid",
                "value": sessionid.strip(),
                "domain": ".instagram.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax"
            }]
            await context.add_cookies(cookies)
            page = await context.new_page()
            await page.goto("https://www.instagram.com/", timeout=45000)
            await asyncio.sleep(4)

            current_url = page.url.lower()
            if "accounts/login" in current_url or "login" in current_url:
                await browser.close()
                return False, "Session ID invalid or expired (redirected to login page)."
            
            if "instagram.com" in current_url and not any(x in current_url for x in ["login", "accounts"]):
                await browser.close()
                return True, "Session ID is valid."
            
            await browser.close()
            return False, "Could not confirm session validity."
    except Exception as e:
        return False, f"Validation error: {e}"

def parse_messages(file_path):
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('﹠', '&').replace('＆', '&').replace('⅋', '&')
    pattern = r'\s*(?:&|\band\b)\s*'
    parts = [part.strip() for part in re.split(pattern, content, flags=re.IGNORECASE) if part.strip()]
    return parts

async def init_page(page, url, dm_selector):
    for _ in range(3):
        try:
            await page.goto(url, timeout=60000)
            await page.wait_for_selector(dm_selector, timeout=30000)
            return True
        except:
            await asyncio.sleep(3)
    return False

async def sender(tab_id, messages, context, page, account_name):
    dm_selector = '[contenteditable="true"][role="textbox"]'
    print(f"[{account_name}] Tab {tab_id} started.")
    current_page = page
    cycle_start = time.time()
    msg_index = 0
    while True:
        if time.time() - cycle_start >= 60:
            try:
                await current_page.reload(timeout=60000)
                await current_page.wait_for_selector(dm_selector, timeout=30000)
            except:
                pass
            cycle_start = time.time()
        msg = messages[msg_index]
        try:
            await current_page.click(dm_selector)
            await current_page.fill(dm_selector, msg)
            await current_page.press(dm_selector, 'Enter')
            print(f"[{account_name}] Tab {tab_id} sent message {msg_index+1}")
        except Exception as e:
            print(f"[{account_name}] Tab {tab_id} error: {e}")
        await asyncio.sleep(0.25)
        msg_index = (msg_index + 1) % len(messages)

# ==================== FIXED run_with_account (Direct Cookie Injection) ====================
async def run_with_account(sessionid: str, account_name: str, thread_urls: list, tabs_per_url: int, messages: list, headless: bool):
    """Fixed: Uses ONLY direct cookie injection. No storage_state anywhere."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless, args=LAUNCH_ARGS)
        
        context = await browser.new_context(
            user_agent=MOBILE_UA,
            viewport=MOBILE_VIEWPORT,
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2,
            color_scheme="dark"
        )

        # === DIRECT COOKIE INJECTION BEFORE ANY PAGE OPENS ===
        cookies = [
            {
                "name": "sessionid",
                "value": sessionid.strip(),
                "domain": ".instagram.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax"
            },
            {
                "name": "ds_user_id",
                "value": sessionid.split("%3A")[0] if "%3A" in sessionid else "0",
                "domain": ".instagram.com",
                "path": "/",
                "secure": True,
                "sameSite": "Lax"
            },
            {
                "name": "csrftoken",
                "value": "missing",
                "domain": ".instagram.com",
                "path": "/",
                "secure": True
            },
            {
                "name": "mid",
                "value": "Y" + "".join(str(i) for i in range(15)),
                "domain": ".instagram.com",
                "path": "/",
                "secure": True
            },
            {
                "name": "ig_did",
                "value": "D" + "".join(str(i) for i in range(20)),
                "domain": ".instagram.com",
                "path": "/",
                "secure": True
            }
        ]

        await context.add_cookies(cookies)
        print(f"[{account_name}] ✅ Cookies injected (sessionid + helpers)")

        dm_selector = '[contenteditable="true"][role="textbox"]'
        pages = []

        try:
            page_list = []
            for url in thread_urls:
                for _ in range(tabs_per_url):
                    page = await context.new_page()
                    page_list.append((page, url))

            init_tasks = [asyncio.create_task(init_page(page, url, dm_selector)) for page, url in page_list]
            results = await asyncio.gather(*init_tasks, return_exceptions=True)

            for i, success in enumerate(results):
                if not isinstance(success, Exception) and success:
                    page, url = page_list[i]
                    pages.append(page)
                    print(f"[{account_name}] Tab {len(pages)} ready for DM")

            if not pages:
                print(f"[{account_name}] No tabs could be initialized.")
                return

            tasks = [asyncio.create_task(sender(i+1, messages, context, pages[i], account_name)) 
                     for i in range(len(pages))]
            await asyncio.gather(*tasks, return_exceptions=True)

        finally:
            for page in pages:
                try:
                    await page.close()
                except:
                    pass
            await context.close()
            await browser.close()

async def main():
    print_spyther_banner()
    accounts = load_accounts()
    pairs = load_pairs()
    switch_interval = 60

    while True:
        print("\n" + "═"*80)
        print("                    SPYTHER v1 - MAIN MENU")
        print("═"*80)
        print("1. Add New Account (Session ID only)")
        print("2. List Saved Accounts")
        print("3. Create Account Pair / Sequence")
        print("4. List & Manage Pairs (unpair all)")
        print("5. Set Account Switch Interval")
        print("6. Start Auto Sender (With Pair OR Single Account)")
        print("0. Exit")
        print("═"*80)

        choice = input("\nChoose option: ").strip()

        if choice == "1":
            name = input("Enter account nickname (e.g. acc1): ").strip()
            if not name:
                continue
            sessionid = input("Paste Instagram sessionid cookie: ").strip()
            if sessionid:
                valid, msg = await validate_sessionid(sessionid)
                print(msg)
                if valid:
                    accounts[name] = {
                        "sessionid": sessionid,
                        "type": "sessionid",
                        "added": str(datetime.now())
                    }
                    save_accounts(accounts)
                    print(f"✅ Account '{name}' added successfully!")
                else:
                    print("❌ Session ID rejected. Please use a fresh valid sessionid.")
            else:
                print("Sessionid cannot be empty.")

        elif choice == "2":
            if not accounts:
                print("No accounts saved.")
            else:
                print("\nSaved Accounts:")
                for i, (n, d) in enumerate(accounts.items(), 1):
                    print(f"{i}. {n} → sessionid saved ({d.get('type','sessionid')})")

        elif choice == "3":
            if not accounts:
                print("Add accounts first.")
                continue
            acc_list = list(accounts.keys())
            for i, n in enumerate(acc_list, 1):
                print(f"{i}. {n}")
            sel = input("\nAccount numbers in order (space separated): ").strip()
            indices = [int(x)-1 for x in sel.split() if x.isdigit()]
            seq = [acc_list[i] for i in indices if 0 <= i < len(acc_list)]
            if seq:
                pname = input("Pair name: ").strip()
                pairs[pname] = seq
                save_pairs(pairs)
                print(f"✅ Pair '{pname}' created: {' → '.join(seq)}")

        elif choice == "4":
            if not pairs:
                print("No pairs.")
                continue
            for pname, seq in pairs.items():
                print(f"• {pname}: {' → '.join(seq)}")
            act = input("\nDelete pair name or 'unpair all': ").strip()
            if act.lower() == "unpair all":
                pairs.clear()
                save_pairs(pairs)
                print("All pairs deleted.")
            elif act in pairs:
                del pairs[act]
                save_pairs(pairs)
                print(f"Pair '{act}' deleted.")

        elif choice == "5":
            try:
                m = int(input(f"Switch interval in minutes (current {switch_interval}): "))
                if m > 0:
                    switch_interval = m
                    print(f"Interval set to {switch_interval} minutes.")
            except:
                print("Invalid.")

        elif choice == "6":
            print("\n1. Use Pair (Auto Switch)")
            print("2. Single Account (No Switching)")
            mode = input("Choose 1 or 2: ").strip()

            if mode == "1":
                if not pairs:
                    print("No pairs created.")
                    continue
                for i, pn in enumerate(pairs.keys(), 1):
                    print(f"{i}. {pn}")
                try:
                    idx = int(input("Select pair: ")) - 1
                    pair_name = list(pairs.keys())[idx]
                    current_accounts = pairs[pair_name]
                    use_pair = True
                except:
                    print("Invalid.")
                    continue
            else:
                if not accounts:
                    print("No accounts saved.")
                    continue
                for i, n in enumerate(accounts.keys(), 1):
                    print(f"{i}. {n}")
                try:
                    idx = int(input("Select account: ")) - 1
                    current_accounts = [list(accounts.keys())[idx]]
                    use_pair = False
                except:
                    print("Invalid.")
                    continue

            urls_input = input("\nThread URLs (comma separated): ").strip()
            thread_urls = [u.strip() for u in urls_input.split(',') if u.strip()]

            tabs_str = input("Tabs per thread (1-5): ").strip()
            tabs_per_url = max(1, min(5, int(tabs_str) if tabs_str.isdigit() else 1))

            msg_file = input("Messages .txt file full path: ").strip()
            try:
                messages = parse_messages(msg_file)
                print(f"✅ Loaded {len(messages)} messages.")
            except Exception as e:
                print(f"Error loading messages: {e}")
                continue

            headless = input("Headless mode? (y/n default y): ").strip().lower() != 'n'

            print(f"\n🚀 Starting Sender | Mode: {'Pair Switch' if use_pair else 'Single Account'}")

            account_index = 0
            try:
                while True:
                    curr_name = current_accounts[account_index]
                    session_id = accounts[curr_name]["sessionid"]
                    print(f"\n{'═'*20} ACCOUNT: {curr_name.upper()} {'═'*20}")

                    try:
                        timeout_sec = switch_interval * 60 if use_pair else None
                        if timeout_sec:
                            await asyncio.wait_for(
                                run_with_account(session_id, curr_name, thread_urls, tabs_per_url, messages, headless),
                                timeout=timeout_sec
                            )
                        else:
                            await run_with_account(session_id, curr_name, thread_urls, tabs_per_url, messages, headless)
                    except asyncio.TimeoutError:
                        print("⏰ Switch time reached → changing account")
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        print(f"Error with {curr_name}: {e}")

                    if not use_pair:
                        print("Single mode running continuously... (Ctrl+C to stop)")
                        await asyncio.sleep(3600)
                    else:
                        account_index = (account_index + 1) % len(current_accounts)
            except KeyboardInterrupt:
                print("\n🛑 Stopped.")

        elif choice == "0":
            print("Thank you for using SPYTHER v1!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    asyncio.run(main())