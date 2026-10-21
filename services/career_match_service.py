JOB_ROLE_SKILLS = {
    "Software Engineer": [
        "Python", "JavaScript", "SQL", "Git", "REST API", "Docker", "AWS", "Algorithms"
    ],
    "Data Analyst": [
        "SQL", "Python", "Excel", "Data Analysis", "Power BI", "Statistics", "Tableau"
    ],
    "Data Scientist": [
        "Python", "Machine Learning", "SQL", "Statistics", "Data Analysis", "Model Evaluation"
    ],
    "Frontend Developer": [
        "JavaScript", "React", "HTML", "CSS", "TypeScript", "Tailwind", "UI/UX"
    ],
    "Backend Engineer": [
        "Python", "Flask", "SQL", "REST API", "Docker", "Git", "AWS", "Linux"
    ],
    "Product Manager": [
        "Product Management", "Agile", "SQL", "Analytics", "Roadmapping", "Stakeholder Communication"
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "Linux", "AWS", "CI/CD", "Git", "Cloud", "Monitoring"
    ],
}

ROLE_GUIDES = {
    "Software Engineer": "Focus on backend/frontend depth, system design, and clean project delivery.",
    "Data Analyst": "Improve SQL query depth, dashboard storytelling, and business metric analysis.",
    "Data Scientist": "Build model explainability, feature engineering, and end-to-end data projects.",
    "Frontend Developer": "Improve component architecture, accessibility, and polished UI/UX workflows.",
    "Backend Engineer": "Strengthen APIs, database design, deployment, and reliability patterns.",
    "Product Manager": "Practice roadmapping, prioritization, and stakeholder communication frameworks.",
    "DevOps Engineer": "Focus on CI/CD, infrastructure automation, observability, and deployment safety.",
}

SKILL_LEARNING_GUIDES = {
    "Python": {"suggestion": "Build 2 small Python APIs or automation scripts and add them to your GitHub.", "sources": ["Real Python", "Python official docs", "Project Euler"]},
    "SQL": {"suggestion": "Practice joins, subqueries, window functions, and real-world reporting tasks.", "sources": ["Mode SQL Tutorial", "LeetCode SQL", "SQLBolt"]},
    "REST API": {"suggestion": "Create a small CRUD API and document endpoints, auth, and error handling.", "sources": ["MDN HTTP", "FastAPI docs", "Postman learning center"]},
    "Docker": {"suggestion": "Containerize a project and practice multi-container setup with databases and apps.", "sources": ["Docker docs", "Docker labs", "Play with Docker"]},
    "Git": {"suggestion": "Practice branching, rebasing, and clean commit history.", "sources": ["Git docs", "Atlassian Git tutorial", "GitHub Skills"]},
    "JavaScript": {"suggestion": "Build a frontend project and focus on DOM, async flow, and clean state handling.", "sources": ["MDN JavaScript", "JavaScript.info", "freeCodeCamp"]},
    "AWS": {"suggestion": "Deploy a small app to the cloud and learn IAM, S3, EC2, and basic networking.", "sources": ["AWS Skill Builder", "Cloud Academy", "AWS documentation"]},
    "Flask": {"suggestion": "Build a full app with authentication, forms, and a database-backed workflow.", "sources": ["Flask docs", "Miguel Grinberg tutorials", "Full Stack Python"]},
    "Machine Learning": {"suggestion": "Work through a classification project and compare models with metrics and validation.", "sources": ["Scikit-learn docs", "Kaggle", "Coursera ML course"]},
    "Data Analysis": {"suggestion": "Turn raw data into a dashboard with insights, cleaning, and business storytelling.", "sources": ["Kaggle", "Coursera", "Google Data Analytics"]},
}


def normalize_skills(skills):
    if not skills:
        return []
    cleaned = []
    for skill in skills:
        value = str(skill).strip()
        if value:
            cleaned.append(value)
    return cleaned


def get_job_matches(resume_skills):
    normalized = normalize_skills(resume_skills)
    lowercase_map = {skill.lower(): skill for skill in normalized}
    matches = []

    for role, required_skills in JOB_ROLE_SKILLS.items():
        matched = []
        for skill in required_skills:
            if skill.lower() in lowercase_map:
                matched.append(skill)

        overlap = len(matched)
        target = len(required_skills)
        score = int((overlap / target) * 100) if target else 0
        if overlap == 0:
            score = 35

        final_score = min(100, max(40, score + 10))
        if final_score < 55:
            continue

        matches.append({
            "role": role,
            "score": final_score,
            "matched_skills": matched,
            "missing_skills": [skill for skill in required_skills if skill.lower() not in lowercase_map][:4],
            "summary": f"You match {overlap} of {target} core skills for {role}.",
            "suggested_next_step": ROLE_GUIDES.get(role, "Keep building project proof and role-specific depth."),
            "best_fit": final_score >= 75,
        })

    ranked = sorted(matches, key=lambda item: item["score"], reverse=True)
    if not ranked:
        return [{
            "role": "Software Engineer",
            "score": 62,
            "matched_skills": [],
            "missing_skills": ["Python", "SQL", "Git", "REST API"],
            "summary": "No strong role match detected yet. Start with a common software engineering profile and build practical project proof.",
            "suggested_next_step": "Build a portfolio project and practice core technical skills before targeting a specialized role.",
            "best_fit": True,
        }]

    return ranked[:3]


def get_skill_dashboard(resume_skills):
    normalized = normalize_skills(resume_skills)
    if not normalized:
        return {
            "total_skills": 0,
            "average_score": 0,
            "strongest_skills": [],
            "growth_areas": ["Add resume keywords for your target role", "Build at least 2 portfolio projects"],
            "skill_groups": [],
            "improvement_plan": [{
                "skill": "Python",
                "suggestion": "Practice a small end-to-end project and publish the code publicly.",
                "sources": ["Real Python", "Python docs", "GitHub projects"],
            }],
        }

    skill_groups = {
        "Core Tech": ["Python", "JavaScript", "SQL", "Git", "Docker"],
        "Web": ["HTML", "CSS", "React", "Flask", "REST API"],
        "Data": ["Data Analysis", "Statistics", "Machine Learning", "Power BI", "Tableau"],
        "Cloud & Ops": ["AWS", "Linux", "CI/CD", "DevOps", "Kubernetes"],
    }

    normalized_map = {item.lower(): item for item in normalized}
    grouped = []
    for group_name, skills in skill_groups.items():
        matched = [skill for skill in skills if skill.lower() in normalized_map]
        score = int((len(matched) / max(len(skills), 1)) * 100)
        grouped.append({
            "group": group_name,
            "strength": score,
            "skills": matched,
            "missing": [skill for skill in skills if skill.lower() not in normalized_map],
        })

    strongest = sorted(
        [{"skill": skill, "level": 75 + min(25, normalized.count(skill) * 5)} for skill in set(normalized)],
        key=lambda item: item["level"],
        reverse=True,
    )[:5]

    growth_areas = []
    for group in grouped:
        if group["strength"] < 65:
            growth_areas.extend(group["missing"][:2])

    if not growth_areas:
        growth_areas = ["Keep deepening your strongest skills with advanced projects and portfolio proof"]

    improvement_plan = []
    seen = set()
    for skill in normalized:
        guide = SKILL_LEARNING_GUIDES.get(skill)
        if guide and skill not in seen:
            improvement_plan.append({
                "skill": skill,
                "suggestion": guide["suggestion"],
                "sources": guide["sources"],
            })
            seen.add(skill)

    if not improvement_plan:
        improvement_plan.append({
            "skill": "Python",
            "suggestion": "Start with one real project and document your work using GitHub, README, and a deployment demo.",
            "sources": ["Real Python", "GitHub Skills", "freeCodeCamp"],
        })

    return {
        "total_skills": len(normalized),
        "average_score": int(sum(item["strength"] for item in grouped) / max(len(grouped), 1)),
        "strongest_skills": strongest,
        "growth_areas": growth_areas[:5],
        "skill_groups": grouped,
        "improvement_plan": improvement_plan[:5],
    }
