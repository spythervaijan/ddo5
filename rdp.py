import os
import time
import re
import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

try:
    from cfonts import render
except ImportError:
    print("pip install python-cfonts")
    render = None

MOBILE_UA = "Mozilla/5.0 (Linux; Android 13; vivo V60) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
MOBILE_VIEWPORT = {"width": 412, "height": 915}

LAUNCH_ARGS = [
    "--disable-dev-shm-usage", "--no-sandbox", "--disable-gpu",
    "--disable-extensions", "--disable-sync", "--mute-audio",
    "--disable-blink-features=AutomationControlled"
]

ACCOUNTS_FILE = "instagram_accounts.json"
PAIRS_FILE = "account_pairs.json"

def print_spyther_banner():
    if render:
        try:
            output = render('SPYTHER', font='block', colors=['cyan', 'yellow'], align='center')
            print(output)
        except:
            pass
    print("═" * 85)
    print("              SPYTHER v1 - Instagram Spam")
    print("                 Made with love")
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

# ==================== TERA STYLE SESSION TEST ====================
async def test_sessionid(sessionid: str):
    """Tere diye code jaisa - sessionid test + full storage_state"""
    print("🔄 Testing sessionid with Playwright (8-10 seconds wait)...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=LAUNCH_ARGS)
            context = await browser.new_context(
                user_agent=MOBILE_UA,
                viewport=MOBILE_VIEWPORT,
                is_mobile=True,
                has_touch=True,
                device_scale_factor=2,
                color_scheme="dark"
            )

            await context.add_cookies([{
                "name": "sessionid",
                "value": sessionid.strip(),
                "domain": ".instagram.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax"
            }])

            page = await context.new_page()
            await page.goto("https://www.instagram.com/", timeout=60000)
            await asyncio.sleep(8)  # Important wait

            # 👇 BAS YE ADD KIYA
            save_sel = 'div[role="button"]:has-text("Save info")'
            try:
                await page.locator(save_sel).click(timeout=5000)
                print("💾 Save info clicked")
            except:
                pass

            # Check login status
            login_count = await page.locator("text=Log in").count()
            success = login_count == 0

            # Save full storage state
            state = await context.storage_state()

            await browser.close()
            return success, state
    except Exception as e:
        print(f"Test error: {e}")
        return False, None

# ==================== SENDING with FULL STORAGE STATE ====================
async def run_with_account(state: dict, account_name: str, thread_urls: list, tabs_per_url: int, messages: list, headless: bool):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless, args=LAUNCH_ARGS)
        
        context = await browser.new_context(
            storage_state=state,   # ← Full state (sabse stable)
            user_agent=MOBILE_UA,
            viewport=MOBILE_VIEWPORT,
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2,
            color_scheme="dark"
        )

        print(f"[{account_name}] ✅ Full storage state loaded")

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
                    pages.append(page_list[i][0])
                    print(f"[{account_name}] Tab {len(pages)} ready")
                else:
                    print(f"[{account_name}] Tab {i+1} init failed")

            if not pages:
                print(f"[{account_name}] No tabs initialized.")
                return

            tasks = [asyncio.create_task(sender(i+1, messages, context, pages[i], account_name)) 
                     for i in range(len(pages))]
            await asyncio.gather(*tasks, return_exceptions=True)

        finally:
            for page in pages:
                try: await page.close()
                except: pass
            await context.close()
            await browser.close()

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
            print(f"[{account_name}] Tab {tab_id} sent {msg_index+1}")
        except Exception as e:
            print(f"[{account_name}] Tab {tab_id} error: {e}")
        await asyncio.sleep(0.25)
        msg_index = (msg_index + 1) % len(messages)

# ==================== MAIN MENU ====================
async def main():
    print_spyther_banner()
    accounts = load_accounts()
    pairs = load_pairs()
    switch_interval = 60

    while True:
        print("\n" + "═"*80)
        print("                    SPYTHER v1 - MAIN MENU")
        print("═"*80)
        print("1. Add New Account (Session ID)")
        print("2. List Saved Accounts")
        print("3. Create Account Pair")
        print("4. Manage Pairs")
        print("5. Set Switch Interval")
        print("6. Start Spam")
        print("0. Exit")
        print("═"*80)

        choice = input("\nChoose: ").strip()

        if choice == "1":
            name = input("Account nickname: ").strip()
            if not name: continue
            sessionid = input("Paste sessionid: ").strip()
            if not sessionid:
                print("Sessionid empty.")
                continue

            success, state = await test_sessionid(sessionid)
            if not success or not state:
                print("❌ Test FAILED - Redirected to login.")
                continue

            accounts[name] = {
                "storage_state": state,
                "sessionid": sessionid,
                "type": "full_state",
                "added": str(datetime.now())
            }
            save_accounts(accounts)
            print(f"✅ '{name}' saved with full storage state!")

        elif choice == "2":
            if not accounts:
                print("No accounts.")
            else:
                for i, (n, d) in enumerate(accounts.items(), 1):
                    print(f"{i}. {n} (Full State)")

        elif choice == "3":
            if not accounts:
                print("FIRST ADD ACCOUNT.")
                continue
            acc_list = list(accounts.keys())
            for i, n in enumerate(acc_list, 1):
                print(f"{i}. {n}")
            sel = input("Numbers space separated: ").strip()
            indices = [int(x)-1 for x in sel.split() if x.isdigit()]
            seq = [acc_list[i] for i in indices if 0 <= i < len(acc_list)]
            if seq:
                pname = input("Pair name: ").strip()
                pairs[pname] = seq
                save_pairs(pairs)
                print(f"Pair '{pname}' created.")

        elif choice == "4":
            if not pairs:
                print("No pairs.")
                continue
            for p, s in pairs.items():
                print(f"• {p}: {' → '.join(s)}")
            act = input("Delete pair or 'unpair all': ").strip()
            if act.lower() == "unpair all":
                pairs.clear()
                save_pairs(pairs)
                print("All unpaired.")
            elif act in pairs:
                del pairs[act]
                save_pairs(pairs)
                print(f"Deleted {act}")

        elif choice == "5":
            try:
                m = int(input(f"Minutes (current {switch_interval}): "))
                if m > 0:
                    switch_interval = m
                    print(f"Interval {switch_interval} min set.")
            except:
                print("Invalid.")

        elif choice == "6":
            # Pair ya Single select (same as before)
            print("\n1. Pair mode\n2. Single account")
            mode = input("Choose: ").strip()
            if mode == "1":
                if not pairs: 
                    print("No pairs.")
                    continue
                for i, pn in enumerate(pairs, 1):
                    print(f"{i}. {pn}")
                idx = int(input("Select: ")) - 1
                current_accounts = pairs[list(pairs.keys())[idx]]
                use_pair = True
            else:
                if not accounts:
                    print("No accounts.")
                    continue
                for i, n in enumerate(accounts, 1):
                    print(f"{i}. {n}")
                idx = int(input("Select: ")) - 1
                current_accounts = [list(accounts.keys())[idx]]
                use_pair = False

            urls = [u.strip() for u in input("Thread URLs (comma): ").split(',') if u.strip()]
            tabs_per = max(1, min(5, int(input("Tabs per URL (1-5): ") or 1)))
            msg_file = input("Messages .txt path: ").strip()
            try:
                messages = parse_messages(msg_file)   # define parse_messages if missing
                print(f"{len(messages)} messages loaded.")
            except Exception as e:
                print(f"Messages error: {e}")
                continue

            headless = input("Headless? (y/n default y): ").strip().lower() != 'n'

            account_index = 0
            try:
                while True:
                    curr = current_accounts[account_index]
                    state = accounts[curr]["storage_state"]
                    print(f"\n{'═'*15} {curr.upper()} {'═'*15}")
                    try:
                        if use_pair:
                            await asyncio.wait_for(
                                run_with_account(state, curr, urls, tabs_per, messages, headless),
                                timeout=switch_interval * 60
                            )
                        else:
                            await run_with_account(state, curr, urls, tabs_per, messages, headless)
                    except asyncio.TimeoutError:
                        print("Switching account...")
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        print(f"Error: {e}")

                    if not use_pair:
                        await asyncio.sleep(3600)
                    else:
                        account_index = (account_index + 1) % len(current_accounts)
            except KeyboardInterrupt:
                print("\nStopped.")

        elif choice == "0":
            print("Bye!")
            break

        else:
            print("Invalid choice.")

# parse_messages function (missing tha)
def parse_messages(file_path):
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('﹠', '&').replace('＆', '&').replace('⅋', '&')
    pattern = r'\s*(?:&|\band\b)\s*'
    parts = [part.strip() for part in re.split(pattern, content, flags=re.IGNORECASE) if part.strip()]
    return parts

if __name__ == "__main__":
    asyncio.run(main())