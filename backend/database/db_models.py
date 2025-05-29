import enum
import uuid

from sqlalchemy import TIMESTAMP, Column, Enum, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    google_sub = Column(String, unique=True, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class SenderEnum(enum.Enum):
    user = "user"
    bot = "bot"

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sender = Column(Enum(SenderEnum), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=text("now()"))

class UserMemory(Base):
    __tablename__ = "user_memory"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    memory = Column(Text, nullable=True)
    last_updated = Column(TIMESTAMP(timezone=True), server_default=text("now()"), onupdate=text("now()"), nullable=False)
