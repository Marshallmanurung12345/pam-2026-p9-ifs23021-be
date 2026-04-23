from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.recommendation_service import create_recommendation, get_recommendations_by_user, get_recommendation_detail, delete_recommendation

recommendation_bp = Blueprint("recommendation", __name__, url_prefix="/recommendations")

@recommendation_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    interest = data.get("interest","").strip()
    if not interest: return jsonify({"error":"Minat wisata wajib diisi"}), 400
    try:
        return jsonify(create_recommendation(user_id,interest,
            budget=data.get("budget"),duration=data.get("duration"))), 201
    except Exception as e:
        return jsonify({"error":str(e)}), 500

@recommendation_bp.route("", methods=["GET"])
@jwt_required()
def list_recommendations():
    return jsonify(get_recommendations_by_user(int(get_jwt_identity()),
        page=request.args.get("page",1,type=int),per_page=request.args.get("per_page",10,type=int)))

@recommendation_bp.route("/<int:rec_id>", methods=["GET"])
@jwt_required()
def recommendation_detail(rec_id):
    result = get_recommendation_detail(rec_id, int(get_jwt_identity()))
    if not result: return jsonify({"error":"Tidak ditemukan"}), 404
    return jsonify(result)

@recommendation_bp.route("/<int:rec_id>", methods=["DELETE"])
@jwt_required()
def delete(rec_id):
    if not delete_recommendation(rec_id, int(get_jwt_identity())):
        return jsonify({"error":"Tidak ditemukan"}), 404
    return jsonify({"message":"Berhasil dihapus"})
