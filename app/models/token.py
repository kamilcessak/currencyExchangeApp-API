from datetime import datetime
from beanie import Document, Indexed
from pydantic import Field
from pymongo import IndexModel, ASCENDING

class TokenBlacklist(Document):
    token: Indexed(str, unique=True)
    timestamp: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "blacklisted_tokens"
        indexes = [
            IndexModel(
                [("timestamp", ASCENDING)],
                expireAfterSeconds=1800
            )
        ]
