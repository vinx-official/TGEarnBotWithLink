import logging
from pymongo import MongoClient, errors
from pymongo.results import InsertOneResult, UpdateResult

from config import MONGO_URI

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None
        self.links_collection = None
        self.withdrawal_requests_collection = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client.earning_bot # Database name
            self.users_collection = self.db.users
            self.links_collection = self.db.links
            self.withdrawal_requests_collection = self.db.withdrawal_requests
            # Create unique index for tg_id if it doesn't exist
            self.users_collection.create_index("tg_id", unique=True)
            logger.info("Successfully connected to MongoDB.")
        except errors.ConnectionFailure as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise

    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

    def add_user(self, tg_id: int) -> bool:
        """Adds a new user to the database if they don't exist."""
        try:
            result: InsertOneResult = self.users_collection.insert_one(
                {
                    "tg_id": tg_id,
                    "balance": 0.0,
                    "completed_links": 0,
                    "upi_id": None,
                }
            )
            return result.acknowledged
        except errors.DuplicateKeyError:
            logger.info(f"User with tg_id {tg_id} already exists.")
            return False
        except Exception as e:
            logger.error(f"Error adding user {tg_id}: {e}")
            return False

    def get_user(self, tg_id: int) -> dict | None:
        """Retrieves user data by Telegram ID."""
        try:
            return self.users_collection.find_one({"tg_id": tg_id})
        except Exception as e:
            logger.error(f"Error getting user {tg_id}: {e}")
            return None

    def update_user_balance(self, tg_id: int, amount: float = 1.0) -> bool:
        """Updates user's balance and increments completed links."""
        try:
            result: UpdateResult = self.users_collection.update_one(
                {"tg_id": tg_id},
                {"$inc": {"balance": amount, "completed_links": 1}}
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error updating balance for user {tg_id}: {e}")
            return False

    def add_link(self, user_id: int, url: str, status: str = 'pending') -> bool:
        """Adds a new shortlink entry."""
        try:
            result: InsertOneResult = self.links_collection.insert_one(
                {"user_id": user_id, "url": url, "status": status}
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error adding link for user {user_id}: {e}")
            return False

    def update_user_upi_id(self, tg_id: int, upi_id: str) -> bool:
        """Updates the user's UPI ID."""
        try:
            result: UpdateResult = self.users_collection.update_one(
                {"tg_id": tg_id},
                {"$set": {"upi_id": upi_id}}
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error updating UPI ID for user {tg_id}: {e}")
            return False

    def add_withdrawal_request(self, user_tg_id: int, amount: float, upi_id: str) -> bool:
        """Adds a new withdrawal request."""
        try:
            result: InsertOneResult = self.withdrawal_requests_collection.insert_one(
                {
                    "user_tg_id": user_tg_id,
                    "amount": amount,
                    "upi_id": upi_id,
                    "status": "pending", # pending, approved, rejected
                    "timestamp": datetime.now()
                }
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error adding withdrawal request for user {user_tg_id}: {e}")
            return False

    def get_pending_withdrawal_requests(self) -> list:
        """Retrieves all pending withdrawal requests."""
        try:
            return list(self.withdrawal_requests_collection.find({"status": "pending"}))
        except Exception as e:
            logger.error(f"Error getting pending withdrawal requests: {e}")
            return []

    def update_withdrawal_request_status(self, request_id: str, status: str) -> bool:
        """Updates the status of a withdrawal request."""
        try:
            from bson.objectid import ObjectId # Import here to avoid circular dependency if not needed elsewhere
            result: UpdateResult = self.withdrawal_requests_collection.update_one(
                {"_id": ObjectId(request_id)},
                {"$set": {"status": status, "processed_at": datetime.now()}}
            )
            return result.acknowledged
        except errors.InvalidId:
            logger.error(f"Invalid request_id format: {request_id}")
            return False
        except Exception as e:
            logger.error(f"Error updating withdrawal request {request_id} status to {status}: {e}")
            return False

    def reset_user_balance_and_links(self, tg_id: int) -> bool:
        """Resets a user's balance and completed links after a withdrawal."""
        try:
            result: UpdateResult = self.users_collection.update_one(
                {"tg_id": tg_id},
                {"$set": {"balance": 0.0, "completed_links": 0}}
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error resetting balance for user {tg_id}: {e}")
            return False

# Instantiate DB manager
db_manager = MongoDB()

from datetime import datetime # Import here to avoid circular import with db_manager instantiation
