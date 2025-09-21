# Telegram Earning Bot 💰

A Telegram bot that allows users to earn money by completing shortlink tasks.  
Users receive GP Links shortlinks, complete them, and earn ₹1 per link. After completing 10 links, they can withdraw ₹10 via UPI. The bot includes buttons for an interactive experience and an admin panel for managing withdrawals.

---

## Features

- **Interactive Buttons**
  - 🔗 Get Link
  - ✅ Mark Completed
  - 💰 Check Balance
  - 🏦 Withdraw Request
- **MongoDB Database** for storing user data and link completion status.
- **GP Links API Integration** for generating earning shortlinks.
- **Admin Panel**
  - Approve / Reject withdrawal requests.
- **Tutorial & Welcome Message** for first-time users.
- **Secure Token Handling** using environment variables.
- Modular, production-ready code with logging and error handling.

---

## Tech Stack

- **Language:** Python 3.10+
- **Telegram Library:** python-telegram-bot v20+
- **Database:** MongoDB
- **Shortlink API:** GP Links
- **Deployment:** Any server supporting Python (e.g., Railway, Render, VPS)

---

## Bot Commands & Buttons

### User Commands
- `/start` – Show welcome message & tutorial
- `/getlink` – Receive a new shortlink with interactive buttons
- `/balance` – Show current balance and completed links
- `/withdraw <upi_id>` – Request payout via UPI

### Admin Commands
- `/admin` – View pending withdrawals
- ✅ Approve / ❌ Reject buttons for withdrawal requests

---

## Database Schema

**Users Collection**
```json

Before Running:
Install Libraries:
code


Bash
"pip install python-telegram-bot~=20.0 pymongo python-dotenv aiohttp bso"

Set up .env file: Create a .env file in your project's root directory and fill in your API keys and admin IDs as shown in the config.py section.
MongoDB: Ensure your MongoDB instance is running and accessible (or use a MongoDB Atlas connection string). The MONGO_URI in your .env file should point to it. The database name used in the code is earning_bot.
GP Links API Key: Make sure your GPLINKS_API_KEY is correct. The gplinks_api.py assumes a specific API structure (https://gplinks.in/api?api=<KEY>&url=<URL>). Double-check the official GP Links API documentation to ensure this URL and response parsing are accurate.
Admin IDs: Replace the placeholder ADMIN_IDS in the .env file with your actual Telegram user ID(s) to access the /admin command.
How to Run:
code

Bash
"python main.py"
