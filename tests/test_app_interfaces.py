import pytest

from app import create_app
from services.github_service import build_github_analysis
from services.career_match_service import get_job_matches, get_skill_dashboard
from services.career_coach_service import generate_coach_response


@pytest.fixture()
def client():
    app = create_app("testing")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_public_pages_render(client):
    assert client.get("/").status_code == 200
    assert client.get("/auth/register").status_code == 200
    assert client.get("/auth/login").status_code == 200


def test_user_registration_and_login_flow(client):
    register_response = client.post(
        "/auth/register",
        data={
            "username": "demo_user",
            "email": "demo@example.com",
            "full_name": "Demo User",
            "password": "pass123",
            "confirm_password": "pass123",
        },
        follow_redirects=False,
    )
    assert register_response.status_code == 302
    assert register_response.headers["Location"] == "/auth/login"

    login_response = client.post(
        "/auth/login",
        data={
            "email": "demo@example.com",
            "password": "pass123",
        },
        follow_redirects=False,
    )
    assert login_response.status_code == 302
    assert login_response.headers["Location"] == "/dashboard/"


def test_protected_pages_redirect_to_login(client):
    assert client.get("/dashboard/").status_code == 302
    assert client.get("/resume/").status_code == 302
    assert client.get("/resume/upload").status_code == 302
    assert client.get("/roadmap/").status_code == 302
    assert client.get("/jobs/").status_code == 302
    assert client.get("/skills/").status_code == 302
    assert client.get("/coach/").status_code == 302


def test_github_analysis_builds_role_specific_summary():
    profile = {
        "login": "alice",
        "public_repos": 8,
        "followers": 12,
        "public_gists": 3,
        "html_url": "https://github.com/alice",
    }
    repo_data = {
        "total_repos": 8,
        "language_distribution": {"Python": 5, "JavaScript": 2, "SQL": 1},
        "repos": [
            {"name": "ml-api", "stars": 20, "forks": 4, "language": "Python"},
            {"name": "dashboard", "stars": 12, "forks": 2, "language": "JavaScript"},
            {"name": "analytics", "stars": 8, "forks": 1, "language": "Python"},
        ],
    }

    result = build_github_analysis(profile, repo_data, "Data Scientist")

    assert result["github_score"] >= 0
    assert result["profile_summary"]
    assert any("Data Scientist" in item["task"] for item in result["milestones"])
    assert any("Python" in strength for strength in result["strengths"])
    assert result["metrics"]["total_repos"] == 8


def test_job_match_and_skill_dashboard_helpers():
    resume_skills = ["Python", "Flask", "SQL", "Git", "REST API", "Docker"]
    matches = get_job_matches(resume_skills)

    assert matches
    assert matches[0]["score"] >= 50
    assert matches[0]["role"]
    assert "suggested_next_step" in matches[0]

    skill_dashboard = get_skill_dashboard(resume_skills)
    assert skill_dashboard["total_skills"] == len(resume_skills)
    assert skill_dashboard["strongest_skills"]
    assert skill_dashboard["improvement_plan"]


def test_coach_response_builds_actionable_advice():
    result = generate_coach_response(
        "How should I improve my resume for a backend role?",
        ["Python", "Flask", "SQL", "Git", "REST API", "Docker"],
        "Backend Engineer",
    )

    assert result["answer"]
    assert "Backend Engineer" in result["answer"]
    assert result["steps"]
    assert result["focus_skills"]
    assert result["conversation_history"]


def test_profile_updates_github_and_uses_it_for_roadmap(client, monkeypatch):
    client.post(
        "/auth/register",
        data={
            "username": "roadmapuser",
            "email": "roadmap@example.com",
            "full_name": "Roadmap User",
            "password": "pass123",
            "confirm_password": "pass123",
        },
        follow_redirects=False,
    )
    client.post(
        "/auth/login",
        data={
            "email": "roadmap@example.com",
            "password": "pass123",
        },
        follow_redirects=False,
    )

    profile_response = client.post(
        "/auth/profile",
        data={
            "target_role": "Backend Engineer",
            "github_username": "octocat",
        },
        follow_redirects=False,
    )
    assert profile_response.status_code == 302

    monkeypatch.setattr(
        "routes.roadmap.get_github_user_data",
        lambda username: {"login": username, "followers": 8, "public_gists": 2, "html_url": f"https://github.com/{username}"},
    )
    monkeypatch.setattr(
        "routes.roadmap.get_user_repositories",
        lambda username: {
            "total_repos": 4,
            "total_stars": 15,
            "total_forks": 5,
            "language_distribution": {"Python": 3, "JavaScript": 1},
            "repos": [
                {"name": "proj1", "stars": 10, "forks": 2, "language": "Python"},
                {"name": "proj2", "stars": 5, "forks": 3, "language": "Python"},
            ],
        },
    )
    monkeypatch.setattr(
        "routes.roadmap.build_github_analysis",
        lambda profile, repo_data, target_role: {
            "github_score": 88,
            "milestones": [{"phase": "Profile snapshot", "task": "ok", "type": "summary"}],
        },
    )

    response = client.post(
        "/roadmap/analyze-github",
        data={
            "github_username": "",
            "target_role": "Backend Engineer",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/roadmap/" 


def test_coach_route_keeps_chat_history(client):
    client.post(
        "/auth/register",
        data={
            "username": "coachuser",
            "email": "coach@example.com",
            "full_name": "Coach User",
            "password": "pass123",
            "confirm_password": "pass123",
        },
        follow_redirects=False,
    )
    client.post(
        "/auth/login",
        data={
            "email": "coach@example.com",
            "password": "pass123",
        },
        follow_redirects=False,
    )

    first = client.post(
        "/coach/",
        data={
            "target_role": "Backend Engineer",
            "question": "How can I improve my resume?",
        },
        follow_redirects=True,
    )
    second = client.post(
        "/coach/",
        data={
            "target_role": "Backend Engineer",
            "question": "What should I study next?",
        },
        follow_redirects=True,
    )

    assert first.status_code == 200
    assert second.status_code == 200
