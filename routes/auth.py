from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User
from models.resume import Resume
from models.interview import InterviewSession
from models.roadmap import CareerRoadmap
from utils.forms import LoginForm, RegisterForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()

    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        full_name = form.full_name.data.strip()
        password = form.password.data

        user = User(username=username, email=email, full_name=full_name or username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()

    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard.index"))

        flash("Invalid email or password.", "danger")

    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        target_role = request.form.get("target_role", "").strip()
        github_username = request.form.get("github_username", "").strip()
        bio = request.form.get("bio", "").strip()

        current_user.full_name = full_name or current_user.full_name or current_user.username
        current_user.target_role = target_role or current_user.target_role
        current_user.github_username = github_username or current_user.github_username
        current_user.bio = bio or current_user.bio
        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.profile"))

    resumes_count = Resume.query.filter_by(user_id=current_user.id).count()
    interviews_count = InterviewSession.query.filter_by(user_id=current_user.id).count()
    roadmaps_count = CareerRoadmap.query.filter_by(user_id=current_user.id).count()

    return render_template(
        "auth/profile.html",
        user=current_user,
        resumes_count=resumes_count,
        interviews_count=interviews_count,
        roadmaps_count=roadmaps_count,
    )