from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.roadmap import CareerRoadmap
from services.github_service import get_github_user_data, get_user_repositories, build_github_analysis

roadmap_bp = Blueprint("roadmap", __name__, url_prefix="/roadmap")


@roadmap_bp.route("/", methods=["GET"])
@login_required
def index():
    user_roadmaps = CareerRoadmap.query.filter_by(user_id=current_user.id).order_by(CareerRoadmap.created_at.desc()).all()
    return render_template(
        "roadmap/index.html",
        roadmaps=user_roadmaps,
        default_github_username=current_user.github_username or "",
        default_target_role=current_user.target_role or "Software Engineer",
    )


@roadmap_bp.route("/analyze-github", methods=["POST"])
@login_required
def analyze_github():
    username = request.form.get("github_username", "").strip() or current_user.github_username or ""
    target_role = request.form.get("target_role", current_user.target_role or "Software Engineer").strip() or current_user.target_role or "Software Engineer"

    if not username:
        flash("Please provide a valid GitHub username.", "warning")
        return redirect(url_for("roadmap.index"))

    profile = get_github_user_data(username)
    if not profile:
        flash("Could not fetch GitHub profile. Please check the username.", "danger")
        return redirect(url_for("roadmap.index"))

    repo_data = get_user_repositories(username)
    analysis = build_github_analysis(profile, repo_data, target_role)

    if not analysis:
        flash("GitHub analysis could not be generated for this profile.", "danger")
        return redirect(url_for("roadmap.index"))

    current_user.github_username = username
    current_user.target_role = target_role
    db.session.add(current_user)

    roadmap = CareerRoadmap(
        user_id=current_user.id,
        target_role=target_role,
        github_score=analysis["github_score"],
    )
    roadmap.set_milestones(analysis["milestones"])

    db.session.add(roadmap)
    db.session.commit()

    flash(f"GitHub profile analyzed! Roadmap generated for {target_role} using {profile.get('login', username)}'s profile.", "success")
    return redirect(url_for("roadmap.index"))