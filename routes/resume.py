import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models.resume import Resume
from services.resume_parser import parse_resume_content

resume_bp = Blueprint("resume", __name__, url_prefix="/resume")

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@resume_bp.route("/", methods=["GET"])
@login_required
def index():
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.created_at.desc()).all()
    return render_template("resume/index.html", resumes=user_resumes)


@resume_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("resume/upload.html")

    if "file" not in request.files:
        flash("No file part selected.", "warning")
        return redirect(url_for("resume.index"))

    file = request.files["file"]
    title = request.form.get("title", "My Resume").strip()

    if file.filename == "":
        flash("No selected file.", "warning")
        return redirect(url_for("resume.index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{current_user.id}_{filename}")
        file.save(save_path)

        raw_text, parsed_data = parse_resume_content(save_path, current_app.config.get("GEMINI_API_KEY"))
        resume = Resume(
            user_id=current_user.id,
            title=title or "My Resume",
            file_path=save_path,
            raw_text=raw_text or "",
        )
        if isinstance(parsed_data, dict):
            resume.set_parsed_data(parsed_data)

        db.session.add(resume)
        db.session.commit()

        flash("Resume uploaded and analyzed successfully!", "success")
        return redirect(url_for("resume.index"))

    flash("Invalid file type. Only PDF, DOCX, and TXT are allowed.", "danger")
    return redirect(url_for("resume.index"))


@resume_bp.route("/<int:resume_id>", methods=["GET"])
@login_required
def view(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    parsed_data = resume.get_parsed_data() or {}
    return render_template("resume/view.html", resume=resume, parsed_data=parsed_data)


@resume_bp.route("/<int:resume_id>/delete", methods=["POST"])
@login_required
def delete(resume_id):
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()

    if resume.file_path and os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    db.session.delete(resume)
    db.session.commit()
    flash("Resume deleted successfully.", "success")
    return redirect(url_for("resume.index"))