import os
from dotenv import load_dotenv
from instagrapi import Client
from datetime import datetime

# Load environment variables
load_dotenv()

USERNAME = os.getenv("INSTA_USERNAME")
PASSWORD = os.getenv("INSTA_PASSWORD")

# 🔒 Fail-safe: ask user if not provided in .env
if not USERNAME:
    USERNAME = input("Enter your Instagram username: ").strip()

if not PASSWORD:
    PASSWORD = input("Enter your Instagram password: ").strip()

cl = Client()

try:
    cl.load_settings("session.json")
    cl.login(USERNAME, PASSWORD)
    print("✅ Logged in with saved session")
except Exception as e:
    print("⚠️ Saved session failed, logging in again...")
    cl.login(USERNAME, PASSWORD)
    cl.dump_settings("session.json")
    print("✅ Logged in successfully and session saved")
