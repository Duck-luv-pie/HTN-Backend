from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# User table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    badge_code = Column(String, unique=True, nullable=False) #four word string
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scans = relationship("Scan", back_populates="user", cascade="all, delete")

# Scan (activity) table
class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    activity_name = Column(String, nullable=False)
    activity_category = Column(String, nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scans")
