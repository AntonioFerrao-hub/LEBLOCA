from __future__ import annotations

from datetime import datetime

from sqlalchemy.dialects.sqlite import JSON

from . import bcrypt, db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    google_accounts = db.relationship(
        "GoogleAccount",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
        }


class GoogleAccount(db.Model):
    __tablename__ = "google_accounts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    display_name = db.Column(db.String(150), nullable=False)
    account_id = db.Column(db.String(120), nullable=False)
    location_id = db.Column(db.String(120), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    settings = db.Column(JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship("User", back_populates="google_accounts")
    reviews = db.relationship(
        "ReviewSnapshot", cascade="all, delete-orphan", back_populates="google_account"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "account_id": self.account_id,
            "location_id": self.location_id,
            "refresh_token": self.refresh_token,
            "settings": self.settings or {},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ReviewSnapshot(db.Model):
    __tablename__ = "review_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    google_account_id = db.Column(db.Integer, db.ForeignKey("google_accounts.id"), nullable=False)
    review_id = db.Column(db.String(120), nullable=False)
    reviewer_name = db.Column(db.String(150))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    review_time = db.Column(db.DateTime)
    sync_time = db.Column(db.DateTime, default=datetime.utcnow)

    google_account = db.relationship("GoogleAccount", back_populates="reviews")

    __table_args__ = (db.UniqueConstraint("google_account_id", "review_id", name="uq_review"),)

    def to_dict(self) -> dict:
        return {
            "review_id": self.review_id,
            "reviewer_name": self.reviewer_name,
            "rating": self.rating,
            "comment": self.comment,
            "review_time": self.review_time.isoformat() if self.review_time else None,
            "sync_time": self.sync_time.isoformat() if self.sync_time else None,
        }


__all__ = ["User", "GoogleAccount", "ReviewSnapshot"]
