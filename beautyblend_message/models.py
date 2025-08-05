from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# ----- USER TABLE -----
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    display_name = Column(String)
    avatar_url = Column(String)

    messages_sent = relationship("Message", back_populates="sender", foreign_keys="Message.sender_id")
    memberships = relationship("ChatRoomMembership", back_populates="user")


# ----- CHAT ROOM -----
class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    messages = relationship("Message", back_populates="chat_room")
    memberships = relationship("ChatRoomMembership", back_populates="chat_room")


# ----- CHAT ROOM MEMBERSHIP -----
class ChatRoomMembership(Base):
    __tablename__ = "chat_room_memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"))

    user = relationship("User", back_populates="memberships")
    chat_room = relationship("ChatRoom", back_populates="memberships")


# ----- MESSAGES -----
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_room_id = Column(Integer, ForeignKey("chat_rooms.id"))
    sender_id = Column(String, ForeignKey("users.id"))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)

    chat_room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="messages_sent")
