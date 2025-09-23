from __future__ import annotations

from flask import Blueprint, jsonify, request

from . import db
from .google_reviews import sync_reviews
from .models import GoogleAccount
from .utils import require_authentication


google_accounts_bp = Blueprint("google_accounts", __name__)


def serialize_account(account: GoogleAccount) -> dict:
    payload = account.to_dict()
    payload["reviews"] = [review.to_dict() for review in account.reviews]
    return payload


@google_accounts_bp.get("")
def list_accounts():
    user = require_authentication()
    if isinstance(user, tuple):
        return user

    accounts = [
        serialize_account(account)
        for account in user.google_accounts.order_by(GoogleAccount.created_at.desc())
    ]
    return jsonify(accounts)


@google_accounts_bp.post("")
def create_account():
    user = require_authentication()
    if isinstance(user, tuple):
        return user

    data = request.get_json() or {}

    required_fields = ["display_name", "account_id", "location_id", "refresh_token"]
    missing_fields = [field for field in required_fields if not (data.get(field) or "").strip()]
    if missing_fields:
        return (
            jsonify({"message": f"Os campos {', '.join(missing_fields)} são obrigatórios."}),
            400,
        )

    account = GoogleAccount(
        owner=user,
        display_name=data["display_name"].strip(),
        account_id=data["account_id"].strip(),
        location_id=data["location_id"].strip(),
        refresh_token=data["refresh_token"].strip(),
        settings=data.get("settings") or {},
    )
    db.session.add(account)
    db.session.commit()

    return jsonify(serialize_account(account)), 201


@google_accounts_bp.put("/<int:account_id>")
@google_accounts_bp.patch("/<int:account_id>")
def update_account(account_id: int):
    user = require_authentication()
    if isinstance(user, tuple):
        return user

    account = GoogleAccount.query.filter_by(id=account_id, user_id=user.id).first()
    if not account:
        return jsonify({"message": "Conta não encontrada."}), 404

    data = request.get_json() or {}

    for field in ["display_name", "account_id", "location_id", "refresh_token"]:
        if field in data and isinstance(data[field], str) and data[field].strip():
            setattr(account, field, data[field].strip())

    if "settings" in data and isinstance(data["settings"], dict):
        account.settings = data["settings"]

    db.session.commit()

    return jsonify(serialize_account(account))


@google_accounts_bp.delete("/<int:account_id>")
def delete_account(account_id: int):
    user = require_authentication()
    if isinstance(user, tuple):
        return user

    account = GoogleAccount.query.filter_by(id=account_id, user_id=user.id).first()
    if not account:
        return jsonify({"message": "Conta não encontrada."}), 404

    db.session.delete(account)
    db.session.commit()

    return jsonify({"message": "Conta removida."})


@google_accounts_bp.post("/<int:account_id>/sync")
def sync_account_reviews(account_id: int):
    user = require_authentication()
    if isinstance(user, tuple):
        return user

    account = GoogleAccount.query.filter_by(id=account_id, user_id=user.id).first()
    if not account:
        return jsonify({"message": "Conta não encontrada."}), 404

    synced_reviews = sync_reviews(account)
    return jsonify([review.to_dict() for review in synced_reviews])
