import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import config
from database import db_manager
from gplinks_api import generate_gplink

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# Set higher logging level for httpx to avoid verbose output from http client
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message and tutorial, and adds the user to the database."""
    user_tg_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if db_manager.add_user(user_tg_id):
        logger.info(f"New user added: {username} (ID: {user_tg_id})")
    else:
        logger.info(f"User {username} (ID: {user_tg_id}) already exists.")

    welcome_message = (
        "👋 Welcome to Earn Bot! You can earn ₹1 per completed link. "
        "Complete 10 links = ₹10 payout via UPI."
    )
    tutorial_message = (
        "\n\n*Tutorial:*\n"
        "1️⃣ Use /getlink to receive your earning link.\n"
        "2️⃣ Open and complete the link (e.g., bypass ads, wait for timer).\n"
        "3️⃣ Check your /balance anytime.\n"
        "4️⃣ When your balance is ≥ ₹10, use `/withdraw <your_upi_id>` to request a payout."
    )
    await update.message.reply_markdown(welcome_message + tutorial_message)

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generates a unique GP Links shortlink and sends it to the user."""
    user_tg_id = update.effective_user.id
    user = db_manager.get_user(user_tg_id)

    if not user:
        await update.message.reply_text("Please /start the bot first!")
        return

    # In a real scenario, the 'original_url' would point to your content
    # or a unique page that tracks the user's completion.
    # For demonstration, we'll use a placeholder and simulate completion.
    base_target_url = "https://yourwebsite.com/earn_page" # Replace with your actual target URL
    # Appending user_tg_id and a unique identifier (like link count)
    # helps you track which user completed which link, if you had a tracking system.
    original_url = f"{base_target_url}?user={user_tg_id}&link_seq={user.get('completed_links', 0) + 1}"

    short_link = await generate_gplink(original_url)

    if short_link:
        db_manager.add_link(user_tg_id, short_link, status='pending')
        await update.message.reply_text(
            f"🔗 Here is your unique earning link:\n`{short_link}`\n\n"
            "Complete this link to earn ₹1!"
        )
        logger.info(f"User {user_tg_id} generated link: {short_link}")

        # --- SIMULATE LINK COMPLETION FOR DEMO PURPOSES ---
        # In a real system, you would have a webhook or a manual verification
        # process to confirm link completion and then call db_manager.update_user_balance.
        # For this demo, we'll auto-complete it after generation.
        if db_manager.update_user_balance(user_tg_id, amount=1.0):
            await update.message.reply_text("✅ Link completion simulated! ₹1 has been added to your balance.")
            logger.info(f"Simulated link completion for user {user_tg_id}. Balance updated.")
        else:
            await update.message.reply_text("❌ Failed to update your balance after link generation (simulation error).")
            logger.error(f"Failed to simulate balance update for user {user_tg_id}.")
        # --- END SIMULATION ---

    else:
        await update.message.reply_text(
            "😞 Sorry, I couldn't generate an earning link at the moment. Please try again later."
        )
        logger.error(f"Failed to generate GP Link for user {user_tg_id}.")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the user's current balance and completed links."""
    user_tg_id = update.effective_user.id
    user = db_manager.get_user(user_tg_id)

    if user:
        balance_amount = user.get("balance", 0.0)
        completed_links = user.get("completed_links", 0)
        await update.message.reply_text(
            f"💰 Your current balance: ₹{balance_amount:.2f}\n"
            f"🔗 Completed links: {completed_links}"
        )
        logger.info(f"User {user_tg_id} checked balance: ₹{balance_amount:.2f}, {completed_links} links.")
    else:
        await update.message.reply_text("You haven't started yet! Use /start to begin.")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles user withdrawal requests."""
    user_tg_id = update.effective_user.id
    user = db_manager.get_user(user_tg_id)

    if not user:
        await update.message.reply_text("Please /start the bot first!")
        return

    current_balance = user.get("balance", 0.0)
    args = context.args

    if current_balance < 10:
        await update.message.reply_text(
            f"You need at least ₹10 to withdraw. Your current balance is ₹{current_balance:.2f}."
        )
        return

    if not args:
        await update.message.reply_text(
            "Please provide your UPI ID after the command, e.g., `/withdraw your_upi_id@bank`"
        )
        return

    upi_id = " ".join(args).strip()
    if not upi_id:
        await update.message.reply_text("Invalid UPI ID provided.")
        return

    if db_manager.update_user_upi_id(user_tg_id, upi_id) and \
       db_manager.add_withdrawal_request(user_tg_id, current_balance, upi_id) and \
       db_manager.reset_user_balance_and_links(user_tg_id):
        
        await update.message.reply_text(
            f"✅ Withdrawal request for ₹{current_balance:.2f} to UPI ID `{upi_id}` has been submitted.\n"
            "It will be reviewed by an admin shortly. Your balance has been reset."
        )
        logger.info(f"Withdrawal request from user {user_tg_id} for ₹{current_balance:.2f} to {upi_id}.")

        # Notify admins
        for admin_id in config.ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=f"🚨 *New Withdrawal Request!* 🚨\n\n"
                         f"User ID: `{user_tg_id}` (`{update.effective_user.username}`)\n"
                         f"Amount: ₹{current_balance:.2f}\n"
                         f"UPI ID: `{upi_id}`\n"
                         f"Status: *Pending*\n\n"
                         f"Use `/admin` to see all requests. To approve/reject, you'll need the request's `_id` from the /admin list."
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
    else:
        await update.message.reply_text("❌ An error occurred while processing your withdrawal. Please try again.")
        logger.error(f"Failed to process withdrawal for user {user_tg_id}.")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin command to list and manage withdrawal requests."""
    user_tg_id = update.effective_user.id

    if user_tg_id not in config.ADMIN_IDS:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        logger.warning(f"Unauthorized admin access attempt by user {user_tg_id}.")
        return

    args = context.args
    if not args:
        requests = db_manager.get_pending_withdrawal_requests()
        if not requests:
            await update.message.reply_text("No pending withdrawal requests.")
            return

        message = "🗓️ *Pending Withdrawal Requests:*\n\n"
        for req in requests:
            message += (
                f"• *Request ID:* `{req['_id']}`\n"
                f"  *User TG ID:* `{req['user_tg_id']}`\n"
                f"  *Amount:* ₹{req['amount']:.2f}\n"
                f"  *UPI ID:* `{req['upi_id']}`\n"
                f"  *Requested On:* `{req['timestamp'].strftime('%Y-%m-%d %H:%M')}`\n\n"
            )
        message += "To approve/reject: `/admin approve <request_id>` or `/admin reject <request_id>`"
        await update.message.reply_markdown(message)
        logger.info(f"Admin {user_tg_id} viewed pending withdrawal requests.")
    else:
        action = args[0].lower()
        if action in ["approve", "reject"]:
            if len(args) < 2:
                await update.message.reply_text(f"Please provide a request ID: `/admin {action} <request_id>`")
                return
            
            request_id = args[1] # MongoDB _id is a string
            
            # Basic validation to check if it looks like an ObjectId
            from bson.objectid import ObjectId
            if not ObjectId.is_valid(request_id):
                await update.message.reply_text("Invalid request ID format. Please provide a valid MongoDB ObjectId.")
                return

            # Retrieve the request to ensure it's pending and to get user info
            req = db_manager.withdrawal_requests_collection.find_one({"_id": ObjectId(request_id), "status": "pending"})

            if not req:
                await update.message.reply_text(f"Request ID `{request_id}` not found or not pending.")
                return

            if db_manager.update_withdrawal_request_status(request_id, action):
                await update.message.reply_text(f"Withdrawal request `{request_id}` {action}d.")
                logger.info(f"Admin {user_tg_id} {action}d withdrawal request {request_id}.")

                # Notify the user about the status
                requested_tg_id = req['user_tg_id']
                amount = req['amount']
                try:
                    await context.bot.send_message(
                        chat_id=requested_tg_id,
                        text=f"📢 Your withdrawal request for ₹{amount:.2f} has been *{action}d* by an admin."
                    )
                except Exception as e:
                    logger.error(f"Failed to notify user {requested_tg_id} about withdrawal status: {e}")
            else:
                await update.message.reply_text(f"❌ Failed to {action} request `{request_id}`.")
                logger.error(f"Admin {user_tg_id} failed to {action} request {request_id}.")
        else:
            await update.message.reply_text("Unknown admin action. Use `/admin approve <request_id>` or `/admin reject <request_id>`.")


def main() -> None:
    """Starts the bot."""
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getlink", get_link))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("withdraw", withdraw))
    application.add_handler(CommandHandler("admin", admin))

    logger.info("Bot started polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")
    finally:
        db_manager.close() # Ensure MongoDB connection is closed on exit
