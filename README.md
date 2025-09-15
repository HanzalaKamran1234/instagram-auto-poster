# Instagram Auto Poster

 A Python automation tool to schedule and post images on Instagram using [instagrapi](https://github.com/adw0rd/instagrapi).

---

##  Features
- Login with saved session (no need to re-enter credentials every time).
- Upload single or multiple Instagram posts.
- Schedule posts at custom times.
- Keeps logs of scheduled jobs and posts.
- Secure handling of credentials (avoid committing personal info).

---

##  Project Structure
├── config/ # Store log files, whitelist/blacklist lists
├── posts/ # Place your images here (not committed to GitHub)
├── post_instagram.py # Script for direct posting
├── schedule_posts.py # Script for scheduling posts
├── load_credentials.py # Handles user login credentials ( keep local only!)
├── requirements.txt # Python dependencies
└── README.md # Project documentation
