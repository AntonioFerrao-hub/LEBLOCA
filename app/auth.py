from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from . import db
from .models import User


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    name = (data.get("name") or "").strip()

    if not email or not password or not name:
        return jsonify({"message": "Nome, email e senha são obrigatórios."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Este e-mail já está cadastrado."}), 400

    user = User(email=email, name=name)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuário criado com sucesso."}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password or ""):
        return jsonify({"message": "Credenciais inválidas."}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()})
