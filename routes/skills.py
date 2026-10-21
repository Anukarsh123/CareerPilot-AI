from flask import Blueprint, render_template
from flask_login import login_required, current_user

from models.resume import Resume
from services.career_match_service import get_skill_dashboard

skills_bp = Blueprint("skills", __name__, url_prefix="/skills")


@skills_bp.route("/", methods=["GET"])
@login_required
def index():
    latest_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
    skills = []

    if latest_resume:
        parsed = latest_resume.get_parsed_data() or {}
        skills = parsed.get("skills") or []

    if not skills:
        skills = ["Python", "SQL", "Git", "JavaScript", "Docker", "REST API"]

    dashboard = get_skill_dashboard(skills)
    return render_template("skills/index.html", dashboard=dashboard, skills=skills)
