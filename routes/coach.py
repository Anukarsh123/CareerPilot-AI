from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user

from models.resume import Resume
from services.career_coach_service import generate_coach_response

coach_bp = Blueprint("coach", __name__, url_prefix="/coach")


@coach_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    skills = []
    latest_resume = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).first()
    if latest_resume:
        parsed = latest_resume.get_parsed_data() or {}
        skills = parsed.get("skills") or []

    if not skills:
        skills = ["Python", "SQL", "Git", "JavaScript", "Docker", "REST API"]

    history = []
    if "coach_history" in session:
        history = session["coach_history"]

    response = None
    default_target_role = current_user.target_role or "Software Engineer"
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        target_role = request.form.get("target_role", default_target_role).strip() or default_target_role

        if not question:
            flash("Please ask a career question before sending it.", "warning")
            return redirect(url_for("coach.index"))

        response = generate_coach_response(question, skills, target_role, history)
        history = response["conversation_history"]
        session["coach_history"] = history

    return render_template(
        "coach/index.html",
        response=response,
        skills=skills,
        history=history,
        default_target_role=default_target_role,
    )
