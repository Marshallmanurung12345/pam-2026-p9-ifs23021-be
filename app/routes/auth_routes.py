from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.auth_service import verify_password, get_user_by_username, get_user_by_id

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username","").strip()
    password = data.get("password","").strip()
    if not username or not password:
        return jsonify({"error":"Username dan password wajib diisi"}), 400
    user = get_user_by_username(username)
    if not user or not verify_password(password, user.password):
        return jsonify({"error":"Username atau password salah"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"message":"Login berhasil","token":token,
                    "user":{"id":user.id,"name":user.name,"username":user.username,"is_admin":user.is_admin}})

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = get_user_by_id(int(get_jwt_identity()))
    if not user:
        return jsonify({"error":"User tidak ditemukan"}), 404
    return jsonify({"id":user.id,"name":user.name,"username":user.username,
                    "is_admin":user.is_admin,"created_at":user.created_at.isoformat()})
