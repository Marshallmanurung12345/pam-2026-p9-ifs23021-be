from flask import Flask, jsonify
from flask_cors import CORS
from app.extensions import Base, engine

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    from app.models import motivation, request_log  # noqa
    Base.metadata.create_all(bind=engine)

    from app.routes.motivation_routes import motivation_bp
    app.register_blueprint(motivation_bp)

    @app.route("/")
    def index():
        return jsonify({"message": "Delcom Motivation API", "status": "running"})

    return app
