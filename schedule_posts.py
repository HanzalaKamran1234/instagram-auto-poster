# schedule_posts.py
import os
import time
import shutil
from datetime import datetime
from getpass import getpass
from instagrapi import Client
from dotenv import load_dotenv

# --- CONFIG ---
SESSION_FILE = "session.json"
LOG_FILE = os.path.join("logs", "schedule_log.txt")
os.makedirs("logs", exist_ok=True)

# --- Login / session handling (safe, won't change your working post_instagram.py) ---
load_dotenv()
USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")

if not USERNAME:
    USERNAME = input("Enter your Instagram username (or press Enter if you rely on saved session): ").strip() or None
if not PASSWORD and USERNAME:
    PASSWORD = getpass("Enter your Instagram password (hidden): ").strip() or None

cl = Client()

def save_log(line: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} - {line}\n")

# Try to load saved session first, then fall back to login with provided credentials
if os.path.exists(SESSION_FILE):
    try:
        cl.load_settings(SESSION_FILE)
        # If username/password available, attempt login (this refreshes session)
        if USERNAME and PASSWORD:
            cl.login(USERNAME, PASSWORD)
            cl.dump_settings(SESSION_FILE)
        print("✅ Loaded saved session.")
    except Exception as e:
        print("⚠️ Saved session failed to load:", e)
        # If we have credentials, try a fresh login
        if USERNAME and PASSWORD:
            try:
                cl = Client()
                cl.login(USERNAME, PASSWORD)
                cl.dump_settings(SESSION_FILE)
                print("✅ Login successful and session saved.")
            except Exception as ee:
                print("❌ Login failed:", ee)
                save_log(f"LOGIN FAILED: {ee}")
                raise SystemExit("Login failed. Fix credentials or session and rerun.")
        else:
            raise SystemExit("Saved session failed and no credentials provided. Add credentials to .env or run post_instagram.py once.")
else:
    # No saved session - must login with credentials (ask if missing)
    if not USERNAME:
        USERNAME = input("Enter your Instagram username: ").strip()
    if not PASSWORD:
        PASSWORD = getpass("Enter your Instagram password (hidden): ").strip()
    try:
        cl.login(USERNAME, PASSWORD)
        cl.dump_settings(SESSION_FILE)
        print("✅ Logged in and session saved.")
    except Exception as e:
        print("❌ Login failed:", e)
        save_log(f"LOGIN FAILED: {e}")
        raise SystemExit("Login failed. Fix credentials and rerun.")

# --- Collect scheduling jobs from user ---
def ask_for_datetime(prompt="Enter schedule datetime (YYYY-MM-DD HH:MM): "):
    while True:
        s = input(prompt).strip()
        try:
            dt = datetime.strptime(s, "%Y-%m-%d %H:%M")
            return dt
        except ValueError:
            print("Invalid format. Use: 2025-09-16 09:30")

def ask_for_image_path(i):
    while True:
        p = input(f"Enter path for image #{i} (full path, e.g. D:\\Python Folder\\insta-poster\\SocialAutoPoster\\posts\\post.jpg): ").strip()
        # Remove accidental quotes
        if p.startswith('"') and p.endswith('"'):
            p = p[1:-1]
        if p.startswith("'") and p.endswith("'"):
            p = p[1:-1]
        p = os.path.abspath(p)

        if os.path.isfile(p):
            return p
        elif os.path.isdir(p):
            print(f"❌ You entered a folder, not a file. Example: {os.path.join(p, 'post.jpg')}")
        else:
            print("❌ File not found. Try again.")


# Number of posts to schedule
while True:
    how_many = input("How many posts do you want to schedule in this run? (enter a number, e.g. 5): ").strip()
    try:
        total = int(how_many)
        if total <= 0:
            print("Enter a positive number.")
            continue
        break
    except ValueError:
        print("Please enter a valid integer.")

jobs = []
for i in range(1, total + 1):
    print(f"\n--- Job {i} of {total} ---")
    img_path = ask_for_image_path(i)
    caption = input("Enter caption (leave empty for no caption): ").strip()
    sched_dt = ask_for_datetime("Enter schedule date & time (YYYY-MM-DD HH:MM, local timezone): ")
    # If scheduled time in the past, give option to post immediately or re-enter
    if sched_dt <= datetime.now():
        ans = input("Scheduled time is in the past. Post immediately? (y/n) ").strip().lower()
        if ans == "y":
            sched_dt = datetime.now()
        else:
            print("Please re-enter a future datetime.")
            sched_dt = ask_for_datetime()
    jobs.append({"time": sched_dt, "path": img_path, "caption": caption})

# Sort jobs by scheduled datetime
jobs.sort(key=lambda x: x["time"])

print("\n✅ All jobs scheduled. The script will run and post at the requested times.")
print("Log file:", LOG_FILE)
print("To stop the scheduler, press Ctrl+C in this terminal.")

# --- Process scheduled jobs ---
for job in jobs:
    scheduled_time = job["time"]
    image_path = job["path"]
    caption = job["caption"]
    # wait until scheduled time
    while True:
        now = datetime.now()
        if now >= scheduled_time:
            break
        # print brief status every 30-60 seconds (to reassure progress)
        delta = (scheduled_time - now).total_seconds()
        if delta > 60:
            print(f"Waiting {int(delta//60)}m {int(delta%60)}s until {scheduled_time} to post '{os.path.basename(image_path)}' ...")
            time.sleep(30)
        else:
            # final countdown: sleep until time
            time.sleep(max(0.5, delta))

    print(f"\nPosting now: {image_path} (scheduled for {scheduled_time})")
    try:
        # Upload photo
        cl.photo_upload(image_path, caption)
        print("✅ Uploaded successfully.")
        save_log(f"SUCCESS: Uploaded {image_path} scheduled for {scheduled_time.isoformat()}")
        # Move posted image into a 'posted' folder alongside its folder
        src_dir = os.path.dirname(image_path)
        posted_dir = os.path.join(src_dir, "posted")
        os.makedirs(posted_dir, exist_ok=True)
        dst = os.path.join(posted_dir, os.path.basename(image_path))
        try:
            shutil.move(image_path, dst)
            print(f"Moved posted image to: {dst}")
        except Exception as e:
            print("Warning: could not move file:", e)
            save_log(f"WARN: move failed for {image_path}: {e}")
    except Exception as e:
        print("❌ Upload failed:", e)
        save_log(f"FAILED: {image_path} scheduled for {scheduled_time.isoformat()} - ERROR: {e}")
    # small pause to avoid posting too fast if multiple jobs share same minute
    time.sleep(5)

print("\nAll scheduled jobs processed. Exiting.")
