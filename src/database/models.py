import enum

from sqlalchemy.types import Integer, String, DateTime, Date
from sqlalchemy import Column, func, Enum, Boolean, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50), unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    reset_password_token = Column(String(255), nullable=True)
    roles = Column("role", Enum(Role), default=Role.user)
    confirmed = Column(Boolean, default=False)
    ban_status = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


photo_m2m_tag = Table(
    "photos_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Photo(Base):
    __tablename__ = "photos"
    id = Column(Integer, primary_key=True)
    photo = Column(String(255), nullable=False)
    qr_code = Column(String(255), nullable=True)
    description = Column(String(200), nullable=True)
    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", backref="users", innerjoin=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    tags = relationship("Tag", secondary=photo_m2m_tag, backref="notes")


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    tag_name = Column(String(255), nullable=False)


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    comment = Column(String(255), nullable=False)
    photo_id = Column("photo_id", ForeignKey("photos.id", ondelete="CASCADE"))
    user_id = Column("user_id", ForeignKey("users.id", ondelete="CASCADE"))
    photo = relationship("Photo", backref="photos", innerjoin=True)
    user = relationship("User", backref="user_comment", innerjoin=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
