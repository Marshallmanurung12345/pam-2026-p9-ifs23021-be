from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app.extensions import Base, engine
from app.services.auth_service import seed_default_users
from app.services.tourist_spot_service import seed_tourist_spots

def create_app():
    app = Flask(__name__)
    CORS(
        app,
        resources={
            r"/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "expose_headers": ["Content-Type", "Authorization"],
            }
        },
    )
    app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
    JWTManager(app)

    from app.models import motivation, request_log, tourist_spot, user  # noqa
    Base.metadata.create_all(bind=engine)
    seed_default_users()
    seed_tourist_spots()

    from app.routes.motivation_routes import motivation_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.spot_routes import spots_bp
    app.register_blueprint(motivation_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(spots_bp)

    @app.route("/")
    def index():
        return jsonify({"message": "Delcom Motivation API", "status": "running"})

    return app
