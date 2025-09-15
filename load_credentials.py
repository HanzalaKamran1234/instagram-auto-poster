# load_credentials.py

from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Read credentials
instagram_username = os.getenv("INSTAGRAM_USERNAME")
instagram_password = os.getenv("INSTAGRAM_PASSWORD")
twitter_api_key = os.getenv("TWITTER_API_KEY")
twitter_api_secret = os.getenv("TWITTER_API_SECRET")

# Print to verify (just for testing, remove later!)
print("Instagram Username:", instagram_username)
print("Instagram Password:", instagram_password)
print("Twitter API Key:", twitter_api_key)
print("Twitter API Secret:", twitter_api_secret)
