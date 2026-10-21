from flask import Blueprint, render_template
from flask_login import login_required, current_user
from extensions import db
from models.resume import Resume
from models.interview import InterviewSession
from models.roadmap import CareerRoadmap

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
@login_required
def index():
    resumes_count = Resume.query.filter_by(user_id=current_user.id).count()
    interviews_count = InterviewSession.query.filter_by(user_id=current_user.id).count()
    roadmaps_count = CareerRoadmap.query.filter_by(user_id=current_user.id).count()

    recent_roadmaps_raw = CareerRoadmap.query.filter_by(user_id=current_user.id).order_by(CareerRoadmap.created_at.desc()).limit(3).all()

    # Prepare safe, presentation-friendly roadmap data for the template
    recent_roadmaps = []
    for r in recent_roadmaps_raw:
        recent_roadmaps.append({
            "id": r.id,
            "target_role": r.target_role or "(no role)",
            "created_at": r.created_at.strftime("%b %d, %Y") if getattr(r, "created_at", None) else "Unknown",
            "github_score": int(r.github_score or 0),
        })

    return render_template(
        "dashboard/index.html",
        user=current_user,
        resumes_count=resumes_count,
        interviews_count=interviews_count,
        roadmaps_count=roadmaps_count,
        recent_roadmaps=recent_roadmaps
    )