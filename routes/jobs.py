from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user

from models.resume import Resume
from services.career_match_service import get_job_matches

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs_bp.route("/", methods=["GET"])
@login_required
def index():
    latest_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
    skills = []

    if latest_resume:
        parsed = latest_resume.get_parsed_data() or {}
        skills = parsed.get("skills") or []

    if not skills:
        skills = ["Python", "SQL", "Git", "JavaScript", "Docker", "REST API"]

    matches = get_job_matches(skills)
    return render_template("jobs/index.html", matches=matches, user_skills=skills)
