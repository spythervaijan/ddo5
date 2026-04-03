import os
import time
import re
import json
import asyncio
from playwright.async_api import async_playwright

# SPYTHER v1 Banner using cfonts (install: pip install python-cfonts)
try:
    from cfonts import render
except ImportError:
    print("Warning: python-cfonts not installed. Install with: pip install python-cfonts")
    render = None

MOBILE_UA = "Mozilla/5.0 (Linux; Android 13; vivo V60) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36"
MOBILE_VIEWPORT = {"width": 412, "height": 915}

LAUNCH_ARGS = [
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-sync",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--mute-audio",
]

# Accounts storage file
ACCOUNTS_FILE = "instagram_accounts.json"

def print_spyther_banner():
    """Print SPYTHER v1 banner using cfonts at the top"""
    if render:
        try:
            output = render('SPYTHER v1', font='block', colors=['cyan', 'yellow'], align='center')
            print(output)
            print("Instagram DM Auto Sender - Multi Account Interactive Mode")
            print("=" * 80)
        except Exception:
            pass
    else:
        # Fallback simple banner
        print("\n" + "=" * 80)
        print("                  SPYTHER v1 - Instagram DM Auto Sender")
        print("                  Multi Account | Interactive Mode")
        print("=" * 80 + "\n")

def load_accounts():
    """Load saved accounts from JSON file"""
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_accounts(accounts):
    """Save accounts to JSON file"""
    try:
        with open(ACCOUNTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save accounts: {e}")

def sanitize_input(raw):
    if isinstance(raw, list):
        raw = " ".join(raw)
    return raw

def parse_messages(names_arg):
    if isinstance(names_arg, list):
        names_arg = " ".join(names_arg)

    content = None  
    is_file = isinstance(names_arg, str) and names_arg.endswith('.txt') and os.path.exists(names_arg)  

    if is_file:  
        try:  
            msgs = []  
            with open(names_arg, 'r', encoding='utf-8') as f:  
                lines = [ln.rstrip('\n') for ln in f if ln.strip()]  
            for ln in lines:  
                m = json.loads(ln)  
                if isinstance(m, str):  
                    msgs.append(m)  
                else:  
                    raise ValueError("JSON line is not a string")  
            if msgs:  
                return msgs  
        except Exception:  
            pass  

        try:  
            with open(names_arg, 'r', encoding='utf-8') as f:  
                content = f.read()  
        except Exception as e:  
            raise ValueError(f"Failed to read file {names_arg}: {e}")  
    else:  
        content = str(names_arg)  

    if content is None:  
        raise ValueError("No valid content to parse")  

    content = (  
        content.replace('﹠', '&')  
        .replace('＆', '&')  
        .replace('⅋', '&')  
        .replace('ꓸ', '&')  
        .replace('︔', '&')  
    )  

    pattern = r'\s*(?:&|\band\b)\s*'  
    parts = [part.strip() for part in re.split(pattern, content, flags=re.IGNORECASE) if part.strip()]  
    return parts

async def login_account(username, password, storage_path, headless):
    """Login and save storage state for an account"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=headless,
                args=LAUNCH_ARGS
            )
            context = await browser.new_context(
                user_agent=MOBILE_UA,
                viewport=MOBILE_VIEWPORT,
                is_mobile=True,
                has_touch=True,
                device_scale_factor=2,
                color_scheme="dark"
            )
            page = await context.new_page()
            try:
                print(f"Logging in as {username}...")
                await page.goto("https://www.instagram.com/", timeout=60000)
                await page.wait_for_selector('input[name="username"]', timeout=30000)
                await page.fill('input[name="username"]', username)
                await page.fill('input[name="password"]', password)
                await page.click('button[type="submit"]')
                await page.wait_for_url("**/home**", timeout=60000)
                await context.storage_state(path=storage_path)
                print(f"Login successful for {username}. Session saved.")
                return True
            except Exception as e:
                print(f"Login error for {username}: {e}")
                return False
            finally:
                await browser.close()
    except Exception as e:
        print(f"Unexpected login error: {e}")
        return False

async def init_page(page, url, dm_selector):
    init_success = False
    for init_try in range(3):
        try:
            await page.goto("https://www.instagram.com/", timeout=60000)
            await page.goto(url, timeout=60000)
            await page.wait_for_selector(dm_selector, timeout=30000)
            init_success = True
            break
        except Exception as init_e:
            print(f"Tab for {url[:30]}... try {init_try+1}/3 failed: {init_e}")
            if init_try < 2:
                await asyncio.sleep(2)
    return init_success

async def sender(tab_id, messages, context, page):
    dm_selector = '[contenteditable="true"][role="textbox"]'
    print(f"Tab {tab_id} ready, starting infinite message loop.")
    current_page = page
    cycle_start = time.time()
    msg_index = 0
    while True:
        elapsed = time.time() - cycle_start
        if elapsed >= 60:
            try:
                print(f"Tab {tab_id} reloading thread after {elapsed:.1f}s")
                await current_page.reload(timeout=60000)
                await current_page.wait_for_selector(dm_selector, timeout=30000)
            except Exception as reload_e:
                print(f"Tab {tab_id} reload failed: {reload_e}")
                raise Exception(f"Tab {tab_id} reload failed: {reload_e}")
            cycle_start = time.time()
            continue

        msg = messages[msg_index]
        send_success = False
        max_retries = 2
        for retry in range(max_retries):
            try:
                if not await current_page.locator(dm_selector).is_visible():
                    try:
                        await current_page.press(dm_selector, 'Enter')
                        await asyncio.sleep(0.2)
                    except:
                        pass
                    await asyncio.sleep(0.5)
                    continue

                await current_page.click(dm_selector)
                await current_page.fill(dm_selector, msg)
                await current_page.press(dm_selector, 'Enter')
                print(f"Tab {tab_id} sent message {msg_index + 1}/{len(messages)}")
                send_success = True
                break
            except Exception as send_e:
                print(f"Tab {tab_id} send error on retry {retry+1}: {send_e}")
                if retry < max_retries - 1:
                    await asyncio.sleep(0.5)

        if not send_success:
            raise Exception(f"Tab {tab_id} failed to send after retries")

        await asyncio.sleep(0.24)
        msg_index = (msg_index + 1) % len(messages)

async def interactive_account_manager():
    """Interactive menu for managing multiple accounts"""
    accounts = load_accounts()
    print_spyther_banner()

    while True:
        print("\n=== SPYTHER v1 - Account Manager ===")
        print("1. Add new account")
        print("2. List saved accounts")
        print("3. Delete an account")
        print("4. Switch / Select account to use")
        print("5. Set auto-switch interval (minutes)")
        print("6. Start sending with current account")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            username = input("Enter Instagram username: ").strip()
            password = input("Enter Instagram password: ").strip()
            if username and password:
                acc_id = f"{username}_{int(time.time())}"
                storage_path = f"storage_{username}.json"
                accounts[acc_id] = {
                    "username": username,
                    "storage_path": storage_path,
                    "added_at": time.time()
                }
                success = await login_account(username, password, storage_path, headless=False)
                if success:
                    save_accounts(accounts)
                    print(f"Account {username} added and logged in successfully.")
                else:
                    print("Login failed. Account not saved.")
                    if acc_id in accounts:
                        del accounts[acc_id]
            else:
                print("Username and password required.")

        elif choice == "2":
            if not accounts:
                print("No accounts saved yet.")
            else:
                print("\nSaved Accounts:")
                for i, (aid, data) in enumerate(accounts.items(), 1):
                    print(f"{i}. {data['username']} (added: {time.ctime(data['added_at'])})")

        elif choice == "3":
            if not accounts:
                print("No accounts to delete.")
                continue
            for i, (aid, data) in enumerate(accounts.items(), 1):
                print(f"{i}. {data['username']}")
            try:
                idx = int(input("Enter number to delete: ")) - 1
                aid = list(accounts.keys())[idx]
                storage = accounts[aid]["storage_path"]
                if os.path.exists(storage):
                    os.remove(storage)
                del accounts[aid]
                save_accounts(accounts)
                print("Account deleted.")
            except Exception:
                print("Invalid selection.")

        elif choice == "4":
            if not accounts:
                print("No accounts saved. Add one first.")
                continue
            print("\nAvailable Accounts:")
            for i, (aid, data) in enumerate(accounts.items(), 1):
                print(f"{i}. {data['username']}")
            try:
                idx = int(input("Select account number: ")) - 1
                selected_aid = list(accounts.keys())[idx]
                selected_account = accounts[selected_aid]
                print(f"Switched to account: {selected_account['username']}")
                return selected_account  # Return selected for main sending
            except Exception:
                print("Invalid selection.")

        elif choice == "5":
            try:
                minutes = int(input("Enter auto-switch interval in minutes (0 = disabled): "))
                # For future use - currently just print (can be extended)
                print(f"Auto-switch interval set to {minutes} minutes.")
            except ValueError:
                print("Please enter a valid number.")

        elif choice == "6":
            if not accounts:
                print("No accounts saved. Add one first.")
                continue
            # Simple select for starting
            print("\nAvailable Accounts:")
            for i, (aid, data) in enumerate(accounts.items(), 1):
                print(f"{i}. {data['username']}")
            try:
                idx = int(input("Select account to start sending: ")) - 1
                selected_aid = list(accounts.keys())[idx]
                return accounts[selected_aid]
            except Exception:
                print("Invalid selection.")

        elif choice == "0":
            print("Exiting...")
            return None

        else:
            print("Invalid choice.")

async def main():
    print_spyther_banner()

    # Interactive account selection
    selected = await interactive_account_manager()
    if not selected:
        return

    storage_path = selected["storage_path"]
    username = selected["username"]

    if not os.path.exists(storage_path):
        print(f"Storage state not found for {username}. Please add/login the account again.")
        return

    print(f"\nUsing account: {username}")
    print(f"Session loaded from: {storage_path}")

    # Rest of the original logic (no argparse for interactive)
    thread_url_input = input("\nEnter thread URL(s) (comma-separated for multiple): ").strip()
    thread_urls = [u.strip() for u in thread_url_input.split(',') if u.strip()]
    if not thread_urls:
        print("No valid thread URLs provided.")
        return

    names_input = input("Enter messages (direct text, or path to .txt file): ").strip()
    if not names_input:
        print("No messages provided.")
        return

    try:
        messages = parse_messages(names_input)
    except ValueError as e:
        print(f"Error parsing messages: {e}")
        return

    if not messages:
        print("No valid messages parsed.")
        return

    print(f"Parsed {len(messages)} messages.")

    tabs_input = input("Number of parallel tabs per URL (1-5, default 1): ").strip()
    tabs = min(max(int(tabs_input) if tabs_input.isdigit() else 1, 1), 5)

    headless_input = input("Run in headless mode? (true/false, default true): ").strip().lower()
    headless = headless_input != 'false'

    total_tabs = len(thread_urls) * tabs
    print(f"Starting with {tabs} tabs per URL (total: {total_tabs} tabs). Ctrl+C to stop.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=LAUNCH_ARGS
        )
        context = await browser.new_context(
            storage_state=storage_path,
            user_agent=MOBILE_UA,
            viewport=MOBILE_VIEWPORT,
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2,
            color_scheme="dark"
        )
        dm_selector = '[contenteditable="true"][role="textbox"]'
        pages = []
        tasks = []
        try:
            while True:
                # Cleanup previous
                for page in pages:
                    try:
                        await page.close()
                    except:
                        pass
                pages = []
                for task in tasks:
                    try:
                        task.cancel()
                    except:
                        pass
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                tasks = []

                # Create pages
                page_urls = []
                for url in thread_urls:
                    for i in range(tabs):
                        page = await context.new_page()
                        page_urls.append((page, url))

                # Init pages
                init_tasks = [asyncio.create_task(init_page(page, url, dm_selector)) for page, url in page_urls]
                init_results = await asyncio.gather(*init_tasks, return_exceptions=True)

                for idx, result in enumerate(init_results):
                    page, url = page_urls[idx]
                    if isinstance(result, Exception) or not result:
                        print(f"Tab for {url} failed to initialize, skipping.")
                        try:
                            await page.close()
                        except:
                            pass
                    else:
                        pages.append(page)
                        print(f"Tab {len(pages)} ready for {url[:50]}...")

                if not pages:
                    print("No tabs initialized. Retrying in 10s...")
                    await asyncio.sleep(10)
                    continue

                actual_tabs = len(pages)
                tasks = [asyncio.create_task(sender(j + 1, messages, context, pages[j])) for j in range(actual_tabs)]
                print(f"Starting {actual_tabs} tab(s) in infinite loop.")

                pending = set(tasks)
                while pending:
                    done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                    for task in done:
                        if task.exception():
                            exc = task.exception()
                            print(f"Tab task exception: {exc}")
                            for t in list(pending):
                                t.cancel()
                            await asyncio.gather(*pending, return_exceptions=True)
                            pending.clear()
                            break
                    else:
                        continue
                    break
        except KeyboardInterrupt:
            print("\nStopping all tabs...")
        finally:
            for page in pages:
                try:
                    await page.close()
                except:
                    pass
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())