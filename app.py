import os
from flask import Flask, render_template
from config import config_by_name
from extensions import db, login_manager

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints & Load Models inside app context
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.resume import resume_bp
    from routes.interview import interview_bp
    from routes.roadmap import roadmap_bp
    from routes.jobs import jobs_bp
    from routes.skills import skills_bp
    from routes.coach import coach_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(coach_bp)

    # Core Routes
    @app.route("/")
    def index():
        return render_template("index.html")

    # Ensure Instance & Upload directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["REPORTS_FOLDER"], exist_ok=True)

    with app.app_context():
        from models.roadmap import CareerRoadmap
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)