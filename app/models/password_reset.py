from datetime import datetime, timedelta
from beanie import Document, Indexed
from pydantic import Field
from pymongo import IndexModel, ASCENDING


class PasswordResetToken(Document):
    token: Indexed(str, unique=True)
    email: Indexed(str)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=15))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "password_reset_tokens"
        indexes = [
            IndexModel(
                [("expires_at", ASCENDING)],
                expireAfterSeconds=0 
            )
        ]
