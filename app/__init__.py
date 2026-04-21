from datetime import timedelta
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app.extensions import Base, engine

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
    CORS(app, resources={r"/*": {"origins": "*"}})
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"error": "Token tidak valid"}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"error": "Token kadaluarsa"}), 401

    from app.models import user, tourist_spot, itinerary, recommendation  # noqa
    Base.metadata.create_all(bind=engine)

    from app.services.auth_service import seed_default_users
    from app.services.tourist_spot_service import seed_tourist_spots
    seed_default_users()
    seed_tourist_spots()

    from app.routes.auth_routes import auth_bp
    from app.routes.spot_routes import spots_bp
    from app.routes.itinerary_routes import itinerary_bp
    from app.routes.recommendation_routes import recommendation_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(spots_bp)
    app.register_blueprint(itinerary_bp)
    app.register_blueprint(recommendation_bp)

    @app.route("/")
    def index():
        return jsonify({"message": "Smart Tourism Samosir API", "status": "running"})

    return app