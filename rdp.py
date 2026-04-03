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
    print("                       Pairs + Auto Switch + Session Only")
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
            print(f"[{account_name}] Tab {tab_id} send error: {e}")

        await asyncio.sleep(0.25)
        msg_index = (msg_index + 1) % len(messages)

async def run_with_account(storage_path, account_name, thread_urls, tabs_per_url, messages, headless):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless, args=LAUNCH_ARGS)
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
                    print(f"[{account_name}] Tab {len(pages)} ready")

            if not pages:
                print(f"[{account_name}] No tabs initialized!")
                return

            tasks = [asyncio.create_task(sender(i+1, messages, context, pages[i], account_name)) 
                    for i in range(len(pages))]

            await asyncio.gather(*tasks, return_exceptions=True)

        finally:
            for page in pages:
                await page.close()
            await context.close()
            await browser.close()

async def main():
    print_spyther_banner()
    
    accounts = load_accounts()
    pairs = load_pairs()
    switch_interval = 60   # default minutes

    while True:
        print("\n" + "═"*80)
        print("                    SPYTHER v1 - MAIN MENU")
        print("═"*80)
        print("1. Add New Account (Session Storage only)")
        print("2. List Saved Accounts")
        print("3. Create Account Pair / Sequence")
        print("4. List & Manage Pairs (unpair all)")
        print("5. Set Account Switch Interval")
        print("6. Start Auto Sender")
        print("0. Exit")
        print("═"*80)

        choice = input("\nChoose option: ").strip()

        if choice == "1":
            name = input("Enter account nickname (e.g. acc1): ").strip()
            path = input("Enter full path of storage_state JSON file: ").strip()
            if os.path.exists(path) and name:
                accounts[name] = {"storage_path": path, "added": str(datetime.now())}
                save_accounts(accounts)
                print(f"✅ Account '{name}' added successfully!")
            else:
                print("❌ Invalid path or name.")

        elif choice == "2":
            if not accounts:
                print("No accounts saved.")
            else:
                print("\nSaved Accounts:")
                for i, (name, data) in enumerate(accounts.items(), 1):
                    print(f"{i}. {name} → {data['storage_path']}")

        elif choice == "3":
            if len(accounts) < 1:
                print("Add at least one account first.")
                continue
            print("\nAvailable Accounts:")
            acc_list = list(accounts.keys())
            for i, name in enumerate(acc_list, 1):
                print(f"{i}. {name}")
            
            selected = input("\nEnter account numbers in order (space separated e.g. 1 3 2): ").strip()
            indices = [int(x)-1 for x in selected.split() if x.isdigit()]
            sequence = [acc_list[i] for i in indices if 0 <= i < len(acc_list)]
            
            if len(sequence) >= 1:
                pair_name = input("Enter pair name (e.g. main_cycle): ").strip()
                pairs[pair_name] = sequence
                save_pairs(pairs)
                print(f"✅ Pair '{pair_name}' created: {' → '.join(sequence)}")

        elif choice == "4":
            if not pairs:
                print("No pairs created yet.")
                continue
            print("\nExisting Pairs:")
            for name, seq in pairs.items():
                print(f"• {name}: {' → '.join(seq)}")
            action = input("\nDelete a pair? Enter pair name (or type 'unpair all'): ").strip()
            if action.lower() == "unpair all":
                pairs.clear()
                save_pairs(pairs)
                print("✅ All pairs deleted (unpaired).")
            elif action in pairs:
                del pairs[action]
                save_pairs(pairs)
                print(f"✅ Pair '{action}' deleted.")

        elif choice == "5":
            try:
                mins = int(input(f"Enter switch interval in minutes (current: {switch_interval}): "))
                if mins > 0:
                    switch_interval = mins
                    print(f"✅ Switch interval set to {switch_interval} minutes.")
            except:
                print("Invalid number.")

        elif choice == "6":
            if not pairs:
                print("Please create at least one account pair first.")
                continue

            print("\nAvailable Pairs:")
            for i, name in enumerate(pairs.keys(), 1):
                print(f"{i}. {name} → {' → '.join(pairs[name])}")
            
            try:
                idx = int(input("\nSelect pair number: ")) - 1
                pair_name = list(pairs.keys())[idx]
                current_pair = pairs[pair_name]
            except:
                print("Invalid selection.")
                continue

            urls_input = input("\nEnter Thread URL(s) (comma separated): ").strip()
            thread_urls = [u.strip() for u in urls_input.split(',') if u.strip()]

            tabs_input = input("Tabs per thread (1-5): ").strip()
            tabs_per_url = int(tabs_input) if tabs_input.isdigit() else 1
            tabs_per_url = max(1, min(5, tabs_per_url))

            msg_file = input("Enter messages .txt file path: ").strip()
            try:
                messages = parse_messages(msg_file)
                print(f"✅ Loaded {len(messages)} messages.")
            except Exception as e:
                print(f"Error: {e}")
                continue

            headless = input("Run in headless mode? (y/n): ").strip().lower() == 'y'

            print(f"\n🚀 Starting Auto Sender with Pair: {pair_name}")
            print(f"Switch every {switch_interval} minutes | Tabs per thread: {tabs_per_url}")

            account_index = 0
            try:
                while True:
                    current_account = current_pair[account_index]
                    storage_path = accounts[current_account]["storage_path"]
                    
                    print(f"\n{'═'*20} SWITCHED TO ACCOUNT: {current_account.upper()} {'═'*20}")
                    
                    try:
                        await asyncio.wait_for(
                            run_with_account(storage_path, current_account, thread_urls, 
                                           tabs_per_url, messages, headless),
                            timeout=switch_interval * 60
                        )
                    except asyncio.TimeoutError:
                        print(f"⏰ Time up! Switching account...")
                    except Exception as e:
                        print(f"Error with {current_account}: {e}")
                    
                    account_index = (account_index + 1) % len(current_pair)
                    
            except KeyboardInterrupt:
                print("\n🛑 Stopped by user.")
            except Exception as e:
                print(f"Critical error: {e}")

        elif choice == "0":
            print("Thank you for using SPYTHER v1!")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    asyncio.run(main())