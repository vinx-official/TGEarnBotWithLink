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
{
  "tg_id": "123456789",
  "balance": 0,
  "completed_links": 0,
  "upi_id": ""
}
