import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.interview import InterviewSession

interview_bp = Blueprint("interview", __name__, url_prefix="/interview")

ROLE_QUESTION_BANK = {
    "software engineer": [
        "Tell me about a complex project you built as a Software Engineer and the trade-offs you made.",
        "How do you handle technical disagreements within a team when priorities conflict?",
        "Describe a time you debugged a production issue and how you confirmed the root cause.",
        "What is your approach to designing APIs for scale, reliability, and maintainability?",
        "How do you decide when to refactor code versus build new functionality?",
        "Tell me about a time you improved performance or system reliability in production."
    ],
    "data scientist": [
        "Walk me through a data science project from problem definition to deployment.",
        "How do you validate whether a model is actually helping business outcomes?",
        "Describe a time you dealt with noisy or incomplete data.",
        "How do you explain a model’s predictions to non-technical stakeholders?",
        "What metrics do you use to evaluate different model choices?",
        "Describe a time you improved a data pipeline or analytical workflow."
    ],
    "frontend engineer": [
        "How do you optimize frontend performance for a slow application?",
        "Describe a time you improved accessibility or user experience across a product.",
        "How do you structure component architecture for maintainability in a growing app?",
        "What is your approach to working with design systems and shared UI patterns?",
        "How do you debug browser-specific UI issues across devices and browsers?",
        "Tell me about a project where you reduced friction in a user journey."
    ],
    "backend engineer": [
        "Design a scalable backend for a high-traffic product feature.",
        "How do you ensure reliability and observability in backend services?",
        "Describe a time you optimized a slow API or database query.",
        "How do you approach authentication, authorization, and security in production systems?",
        "Tell me about a service you designed to handle failure gracefully.",
        "How do you decide between sync and async processing in a backend system?"
    ],
    "product manager": [
        "How do you prioritize roadmap decisions when stakeholders disagree?",
        "Describe a time you launched a product feature with unclear success metrics.",
        "How do you evaluate whether a feature is worth building?",
        "Tell me about a strategy you used to gather customer insight and turn it into action.",
        "How do you balance speed with product quality?",
        "Describe a situation where you had to pivot direction based on feedback."
    ],
    "devops engineer": [
        "How do you design a CI/CD pipeline for a production system?",
        "Describe a time you reduced deployment risk or improved system reliability.",
        "How do you monitor incidents and prioritize recovery actions?",
        "What is your approach to infrastructure as code and environment consistency?",
        "Tell me about a deployment incident and what you learned from it.",
        "How do you balance automation with operational safety?"
    ],
    "qa engineer": [
        "How do you design a quality strategy for a complex product release?",
        "Describe how you prioritize automated tests for critical user flows.",
        "How do you handle regressions when a release is under pressure?",
        "Tell me about a time you caught a production bug before release.",
        "How do you balance test coverage, speed, and maintainability?",
        "Describe a situation where you improved a testing process for a team."
    ],
    "ux designer": [
        "How do you turn user research into a product design decision?",
        "Describe a time you improved a confusing user flow or interface.",
        "How do you validate design assumptions before a large implementation?",
        "What metrics do you use to evaluate product usability?",
        "How do you work with engineering teams during design handoff?",
        "Tell me about a project where you improved accessibility or inclusivity."
    ]
}


def get_role_questions(target_role):
    normalized = (target_role or "Software Engineer").strip().lower()
    for key, questions in ROLE_QUESTION_BANK.items():
        if key in normalized:
            return questions
    return ROLE_QUESTION_BANK["software engineer"]


@interview_bp.route("/", methods=["GET"])
@login_required
def index():
    sessions = InterviewSession.query.filter_by(user_id=current_user.id).order_by(InterviewSession.created_at.desc()).all()
    return render_template("interview/index.html", sessions=sessions)


@interview_bp.route("/start", methods=["POST"])
@login_required
def start():
    target_role = request.form.get("target_role", "Software Engineer").strip()
    difficulty = request.form.get("difficulty", "Medium")

    default_questions = get_role_questions(target_role)
    if difficulty.lower() == "hard":
        default_questions = default_questions[:6]
    elif difficulty.lower() == "easy":
        default_questions = default_questions[:4]

    session = InterviewSession(
        user_id=current_user.id,
        target_role=target_role,
        difficulty=difficulty,
        completed=False
    )
    session.set_questions(default_questions)

    db.session.add(session)
    db.session.commit()

    flash(f"Interview session started for {target_role}!", "success")
    return redirect(url_for("interview.room", session_id=session.id))


@interview_bp.route("/room/<int:session_id>", methods=["GET"])
@login_required
def room(session_id):
    session = InterviewSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash("Unauthorized access to interview session.", "danger")
        return redirect(url_for("interview.index"))

    return render_template("interview/session.html", session=session, questions=session.get_questions())


@interview_bp.route("/submit/<int:session_id>", methods=["POST"])
@login_required
def submit(session_id):
    session = InterviewSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash("Unauthorized access to interview session.", "danger")
        return redirect(url_for("interview.index"))

    questions = session.get_questions()
    responses = {}
    total_score = 0

    for idx, question in enumerate(questions):
        answer = request.form.get(f"question_{idx}", "").strip()
        if not answer:
            continue

        score = min(100, max(40, len(answer.split()) * 4))
        feedback = "Strong answer. You explained the situation clearly and showed good reasoning." if score >= 75 else "Good start. Add more specifics around impact, trade-offs, and measurable outcomes."
        responses[str(idx)] = {
            "question": question,
            "answer": answer,
            "score": score,
            "feedback": feedback,
        }
        total_score += score

    session.set_responses(responses)
    session.completed = True
    session.overall_score = round(total_score / len(responses), 2) if responses else 0
    db.session.commit()

    flash("Interview submitted successfully.", "success")
    return redirect(url_for("interview.results", session_id=session.id))


@interview_bp.route("/results/<int:session_id>", methods=["GET"])
@login_required
def results(session_id):
    session = InterviewSession.query.get_or_404(session_id)
    if session.user_id != current_user.id:
        flash("Unauthorized access to interview feedback.", "danger")
        return redirect(url_for("interview.index"))

    return render_template("interview/results.html", session=session, responses=session.get_responses())


@interview_bp.route("/submit-answer/<int:session_id>", methods=["POST"])
@login_required
def submit_answer(session_id):
    session = InterviewSession.query.get_or_404(session_id)
    data = request.get_json() or {}

    question_idx = data.get("question_index", 0)
    transcript = data.get("transcript", "").strip()

    responses = session.get_responses()
    responses[str(question_idx)] = {
        "transcript": transcript,
        "length_words": len(transcript.split()),
        "confidence_score": round(min(1.0, len(transcript.split()) / 40.0), 2)
    }
    session.set_responses(responses)
    db.session.commit()

    return jsonify({"status": "success", "recorded_words": len(transcript.split())})