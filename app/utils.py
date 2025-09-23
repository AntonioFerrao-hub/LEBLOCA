from __future__ import annotations

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from .models import User


def get_current_user() -> User | None:
    verify_jwt_in_request(optional=True)
    identity = get_jwt_identity()
    if identity is None:
        return None
    return User.query.get(int(identity))


def require_authentication():
    verify_jwt_in_request()
    identity = get_jwt_identity()
    user = User.query.get(int(identity)) if identity is not None else None
    if user is None:
        return jsonify({"message": "Usuário não encontrado."}), 401
    return user


__all__ = ["get_current_user", "require_authentication"]
