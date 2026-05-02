from flask import Flask, jsonify
from dotenv import load_dotenv
from src.extensions import db
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET")
    app.config["MONITORING_API_KEY"] = os.getenv("MONITORING_API_KEY")

    db.init_app(app)

    from src.routes.auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    from src.routes.batch_routes import batch_bp
    app.register_blueprint(batch_bp)

    from src.routes.session_routes import session_bp
    app.register_blueprint(session_bp)

    from src.routes.attendance_routes import attendance_bp
    app.register_blueprint(attendance_bp)

    from src.routes.summary_routes import summary_bp
    app.register_blueprint(summary_bp)

    from src.routes.monitoring_routes import monitoring_bp
    app.register_blueprint(monitoring_bp)

    with app.app_context():
        db.create_all()

        try:
            from src.seed import seed_data
            seed_data()
        except Exception as e:
            print("Seed skipped:", e)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404


    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405


    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    @app.get("/")
    def home():
        return jsonify({"message": "SkillBridge API running"})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)