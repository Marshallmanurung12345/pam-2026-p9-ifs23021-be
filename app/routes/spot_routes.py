from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.tourist_spot_service import get_all_spots, get_spot_detail, get_categories

spots_bp = Blueprint("spots", __name__, url_prefix="/spots")

@spots_bp.route("", methods=["GET"])
@jwt_required()
def list_spots():
    return jsonify(get_all_spots(page=request.args.get("page",1,type=int),
        per_page=request.args.get("per_page",20,type=int),
        category=request.args.get("category"),search=request.args.get("search")))

@spots_bp.route("/categories", methods=["GET"])
@jwt_required()
def list_categories():
    return jsonify({"data":get_categories()})

@spots_bp.route("/<int:spot_id>", methods=["GET"])
@jwt_required()
def spot_detail(spot_id):
    spot = get_spot_detail(spot_id)
    if not spot:
        return jsonify({"error":"Tidak ditemukan"}), 404
    return jsonify(spot)
