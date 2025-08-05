# ✅ Finalized crud.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, ChatRoom, Message, ChatRoomMembership
from datetime import datetime
from sqlalchemy import or_
import uuid

async def get_user_by_username(db: AsyncSession, username: str):
    res = await db.execute(select(User).where(User.username == username))
    return res.scalars().first()

async def create_user(db: AsyncSession, username: str, hashed_password: str):
    user = User(id=str(uuid.uuid4()), username=username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    return user

async def get_all_users(db: AsyncSession):
    res = await db.execute(select(User))
    return [{"username": u.username, "display_name": u.display_name, "avatar_url": u.avatar_url} for u in res.scalars()]

async def get_user_profile(db: AsyncSession, user_id: str):
    res = await db.execute(select(User).where(User.id == user_id))
    return res.scalars().first()

async def create_chatroom_if_not_exists(db: AsyncSession, user1: str, user2: str):
    users = sorted([user1, user2])
    name = f"{users[0]}-{users[1]}"
    res = await db.execute(select(ChatRoom).where(ChatRoom.name == name))
    room = res.scalars().first()
    if not room:
        room = ChatRoom(name=name)
        db.add(room)
        await db.flush()
        for username in users:
            u = await get_user_by_username(db, username)
            db.add(ChatRoomMembership(user_id=u.id, chat_room_id=room.id))
        await db.commit()
    return room

async def get_chatrooms_for_user(db: AsyncSession, user_id: str):
    q = await db.execute(
        select(ChatRoom).join(ChatRoomMembership).where(ChatRoomMembership.user_id == user_id)
    )
    return [{"id": r.id, "name": r.name} for r in q.scalars()]

async def get_messages_for_room(db: AsyncSession, room_id: int, user_id: str):
    q = await db.execute(
        select(Message).where(Message.chat_room_id == room_id).order_by(Message.timestamp)
    )
    result = []
    for msg in q.scalars():
        sender = await get_user_profile(db, msg.sender_id)
        result.append({
            "sender": sender.display_name or sender.username,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "avatar_url": sender.avatar_url,
            "is_read": True
        })
    return result

async def save_message(db: AsyncSession, chat_room_id: int, sender_id: str, content: str):
    msg = Message(chat_room_id=chat_room_id, sender_id=sender_id, content=content, timestamp=datetime.utcnow())
    db.add(msg)
    await db.commit()
