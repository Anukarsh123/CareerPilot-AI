import requests

GITHUB_API_URL = "https://api.github.com"


def get_github_user_data(username):
    """Fetch profile details for a given GitHub username."""
    response = requests.get(f"{GITHUB_API_URL}/users/{username}", timeout=10)
    if response.status_code == 200:
        return response.json()
    return None


def get_user_repositories(username):
    """Fetch public repositories and extract key metrics (stars, languages, forks)."""
    response = requests.get(f"{GITHUB_API_URL}/users/{username}/repos?per_page=100&sort=updated", timeout=10)
    if response.status_code != 200:
        return []

    repos = response.json()
    repo_summary = []
    languages = {}

    for repo in repos:
        if repo.get("fork"):
            continue  # Skip forked repositories for clean analysis

        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1

        repo_summary.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "language": lang,
            "url": repo.get("html_url")
        })

    return {
        "repos": repo_summary,
        "language_distribution": languages,
        "total_repos": len(repo_summary),
        "total_stars": sum(repo.get("stars", 0) for repo in repo_summary),
        "total_forks": sum(repo.get("forks", 0) for repo in repo_summary),
    }


def build_github_analysis(profile, repo_data, target_role):
    """Convert raw GitHub profile data into a role-aware roadmap summary."""
    if not profile:
        return None

    repo_list = repo_data.get("repos", []) if isinstance(repo_data, dict) else []
    language_distribution = repo_data.get("language_distribution", {}) if isinstance(repo_data, dict) else {}
    total_repos = repo_data.get("total_repos", len(repo_list)) if isinstance(repo_data, dict) else len(repo_list)
    total_stars = repo_data.get("total_stars", sum(repo.get("stars", 0) for repo in repo_list)) if isinstance(repo_data, dict) else sum(repo.get("stars", 0) for repo in repo_list)
    total_forks = repo_data.get("total_forks", sum(repo.get("forks", 0) for repo in repo_list)) if isinstance(repo_data, dict) else sum(repo.get("forks", 0) for repo in repo_list)

    top_languages = sorted(language_distribution.items(), key=lambda item: item[1], reverse=True)[:3]
    primary_language = top_languages[0][0] if top_languages else "the main stack"
    followers = profile.get("followers", 0)
    public_gists = profile.get("public_gists", 0)

    score = min(
        100,
        (total_repos * 6)
        + (followers * 4)
        + (public_gists * 2)
        + (total_stars // 3)
        + (total_forks // 2),
    )

    strengths = []
    if top_languages:
        strengths.append(f"Strongest language focus: {primary_language} ({top_languages[0][1]} repos)")
    if total_stars > 0:
        strengths.append(f"Portfolio visibility: {total_stars} total stars across public repos")
    if total_repos >= 3:
        strengths.append(f"Active project history: {total_repos} public repositories")
    if followers > 0:
        strengths.append(f"Community reach: {followers} followers and public engagement")
    if not strengths:
        strengths.append("Profile is still growing; there is room to build more public evidence for the target role.")

    gaps = []
    if total_repos < 3:
        gaps.append("Build at least 2-3 public projects that demonstrate real-world problem solving for the target role.")
    if not top_languages:
        gaps.append("Add more project-based work so the language stack is clearer to recruiters and hiring managers.")
    if total_stars < 10:
        gaps.append("Improve repository polish with better READMEs, architecture notes, and deployed demos.")
    if not followers and total_repos >= 1:
        gaps.append("Increase visibility by sharing work, contributing to open-source, and documenting technical decisions.")
    if not gaps:
        gaps.append(f"Keep improving {target_role} depth by building one advanced portfolio project and refining system design readiness.")

    profile_summary = (
        f"{profile.get('login', 'This GitHub profile')} has {total_repos} public repos, "
        f"{followers} followers, and a focus on {', '.join(lang for lang, _ in top_languages) if top_languages else 'emerging technologies'}. "
        f"This profile is a good base for a {target_role} roadmap and can become much stronger with targeted portfolio work."
    )

    milestones = [
        {
            "phase": "Profile snapshot",
            "task": f"{profile_summary}",
            "type": "summary",
        },
        {
            "phase": "Core skill build",
            "task": f"Deepen {primary_language} and {target_role}-specific fundamentals with 2 project-based learning sprints and repeatable documentation.",
            "type": "skill",
        },
        {
            "phase": "Portfolio upgrade",
            "task": "Refine public repositories with clean READMEs, architecture notes, screenshots, and deployed links so recruiters can evaluate work quickly.",
            "type": "portfolio",
        },
        {
            "phase": "Advanced proof",
            "task": f"Create one end-to-end {target_role} project that demonstrates real data flow, testing, deployment, and business impact.",
            "type": "project",
        },
        {
            "phase": "Career readiness",
            "task": "Prepare for interviews with system design, debugging, behavioral questions, and resume tailoring aligned to the target role.",
            "type": "career",
        },
    ]

    return {
        "github_username": profile.get("login"),
        "profile_url": profile.get("html_url"),
        "profile_summary": profile_summary,
        "strengths": strengths,
        "gaps": gaps,
        "milestones": milestones,
        "github_score": score,
        "metrics": {
            "total_repos": total_repos,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "followers": followers,
            "public_gists": public_gists,
            "top_languages": [lang for lang, _ in top_languages],
        },
    }
