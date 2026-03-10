from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, func
from sqlalchemy.orm import relationship
from app.database import Base
from typing import List

follows = Table('follows', Base.metadata,
                Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
                Column('following_id', Integer, ForeignKey('users.id'), primary_key=True)
)

likes = Table('likes', Base.metadata,
                Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
                Column('tweet_id', Integer, ForeignKey('tweets.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String(36), unique=True, index=True)
    name = Column(String(100), nullable=True)

class Tweet(Base):
    __tablename__ = "tweets"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(280), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    author = relationship("User")

class Media(Base):
    __tablename__ = "medias"
    id = Column(Integer, primary_key=True)
    file_path = Column(String(500))
    tweet_id = Column(Integer, ForeignKey("tweets.id"))
