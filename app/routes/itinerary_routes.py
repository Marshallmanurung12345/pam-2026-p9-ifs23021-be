from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.itinerary_service import create_itinerary, get_itineraries_by_user, get_itinerary_detail, delete_itinerary

itinerary_bp = Blueprint("itinerary", __name__, url_prefix="/itineraries")

@itinerary_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    theme = data.get("theme","").strip()
    duration_days = data.get("duration_days")
    budget = data.get("budget","medium").lower()
    group_type = data.get("group_type","solo").lower()
    if not theme: return jsonify({"error":"Tema wajib diisi"}), 400
    if not duration_days or not isinstance(duration_days,int): return jsonify({"error":"Durasi wajib diisi"}), 400
    if duration_days < 1 or duration_days > 7: return jsonify({"error":"Durasi 1-7 hari"}), 400
    if budget not in ["low","medium","high"]: return jsonify({"error":"Budget: low/medium/high"}), 400
    if group_type not in ["solo","couple","family","group"]: return jsonify({"error":"Group: solo/couple/family/group"}), 400
    try:
        return jsonify(create_itinerary(user_id,theme,duration_days,budget,group_type)), 201
    except Exception as e:
        return jsonify({"error":str(e)}), 500

@itinerary_bp.route("", methods=["GET"])
@jwt_required()
def list_itineraries():
    return jsonify(get_itineraries_by_user(int(get_jwt_identity()),
        page=request.args.get("page",1,type=int),per_page=request.args.get("per_page",10,type=int)))

@itinerary_bp.route("/<int:itinerary_id>", methods=["GET"])
@jwt_required()
def itinerary_detail(itinerary_id):
    result = get_itinerary_detail(itinerary_id, int(get_jwt_identity()))
    if not result: return jsonify({"error":"Tidak ditemukan"}), 404
    return jsonify(result)

@itinerary_bp.route("/<int:itinerary_id>", methods=["DELETE"])
@jwt_required()
def delete(itinerary_id):
    if not delete_itinerary(itinerary_id, int(get_jwt_identity())):
        return jsonify({"error":"Tidak ditemukan"}), 404
    return jsonify({"message":"Berhasil dihapus"})
