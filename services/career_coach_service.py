def generate_coach_response(question, resume_skills=None, target_role=None, history=None):
    skills = resume_skills or []
    role = (target_role or "Software Engineer").strip() or "Software Engineer"
    previous_history = history or []

    normalized_skills = [str(skill).strip() for skill in skills if str(skill).strip()]
    role_library = {
        "backend engineer": ["Python", "SQL", "REST API", "Docker", "Flask", "PostgreSQL", "Redis", "System Design"],
        "data scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas", "Scikit-learn", "Experimentation", "Visualization"],
        "full stack engineer": ["JavaScript", "React", "Node.js", "SQL", "REST API", "Docker", "Git", "System Design"],
        "product manager": ["Roadmapping", "Stakeholder Communication", "SQL", "Analytics", "Prioritization", "Metrics", "Agile"],
        "software engineer": ["Python", "JavaScript", "Git", "SQL", "Docker", "System Design", "Testing", "REST API"],
        "frontend engineer": ["JavaScript", "HTML", "CSS", "React", "User Experience", "Testing", "Accessibility", "Performance"],
        "devops engineer": ["Docker", "AWS", "CI/CD", "Linux", "Kubernetes", "Terraform", "Monitoring", "Automation"],
    }

    role_key = role.lower()
    suggested_skills = []
    for key, options in role_library.items():
        if key in role_key:
            suggested_skills = options
            break
    if not suggested_skills:
        suggested_skills = [
            "Python", "SQL", "Git", "Project delivery", "Communication", "Problem solving"
        ]

    focus_skills = [skill for skill in suggested_skills if skill not in normalized_skills][:5]
    if not focus_skills:
        focus_skills = ["System design", "Portfolio proof", "Communication practice"]

    lower_question = (question or "").lower()
    recent_context = ""
    if previous_history:
        recent_context = f" You previously asked about {previous_history[-1].get('question', '').strip()[:50]} and the coach responded with actionable guidance."

    if "resume" in lower_question or "ats" in lower_question or "cv" in lower_question:
        keyword_text = ", ".join(normalized_skills[:5]) if normalized_skills else "your core job-relevant tools"
        answer = (
            f"For {role}, your resume should read like a results report, not a list of tools. "
            f"Lead with a strong summary, describe outcomes with numbers, and naturally include keywords like {keyword_text}. "
            f"Match your experience to the role description, highlight one or two high-impact projects, and keep the format ATS-friendly with clean section headings and a concise layout."
        )
        steps = [
            "Rewrite the summary to align directly with the target role and the job description.",
            "Put project results first: impact, scale, and measurable business outcomes.",
            "Add role-specific keywords in a natural way across summary, skills, and projects.",
            "Keep formatting simple and ATS-friendly with standard headings and no graphic-heavy layouts.",
        ]
    elif "interview" in lower_question or "prepare" in lower_question or "questions" in lower_question:
        answer = (
            f"For {role}, interview prep should combine technical depth and clear communication. "
            f"Practice explaining your project decisions, trade-offs, and impact in plain language. "
            f"Be ready for behavioral questions using STAR, and for technical questions around {', '.join(suggested_skills[:3])}. "
            f"A strong answer shows what you built, why you chose it, and what changed because of it."
        )
        steps = [
            "Prepare 3-5 project walkthroughs with structure, trade-offs, and outcomes.",
            "Practice system design and debugging questions for your role area.",
            "Use STAR for behavioral answers and keep examples role-relevant.",
            "Do a mock interview and record yourself to improve clarity and pace.",
        ]
    elif "study" in lower_question or "next" in lower_question or "learn" in lower_question or "skill" in lower_question:
        answer = (
            f"The best next move for {role} is to improve the highest-value gaps in your profile and ship one polished proof project. "
            f"Prioritize {', '.join(focus_skills[:3])} and then document your work publicly with a clean GitHub repo, a visible demo, and a short write-up of the problem and solution."
        )
        steps = [
            "Choose one project that maps directly to your target role and finish it end-to-end.",
            "Deepen the skill gaps that appear most often in job descriptions for this role.",
            "Share your work on GitHub and explain architecture decisions in a readable way.",
            "Revisit your resume after each project so your proof and profile stay aligned.",
        ]
    elif "github" in lower_question or "portfolio" in lower_question or "projects" in lower_question:
        answer = (
            f"For {role}, your GitHub and portfolio should prove execution, not just learning. "
            f"Keep your repositories organized, add a clear README, explain the business problem, show screenshots or a demo, and highlight the technologies used. "
            f"One strong project is more valuable than five unfinished ones."
        )
        steps = [
            "Refine your best repo with a clean README, architecture notes, and screenshots.",
            "Build a project that solves a real user problem or business workflow.",
            "Link your portfolio to your resume and highlight measurable outcomes.",
            "Review the repo as if a recruiter or hiring manager is opening it for the first time.",
        ]
    elif "career" in lower_question or "switch" in lower_question or "job" in lower_question or "hiring" in lower_question:
        answer = (
            f"To move toward {role}, build a clear transition plan: tighten your resume, improve the missing skills, and collect proof through projects and applied work. "
            f"Most candidates improve their chances by showing a focused story rather than trying to look broad everywhere at once."
        )
        steps = [
            "Define a clear narrative around your experience and why it fits this role.",
            "Close the most important skill gaps using projects and small practice sprints.",
            "Tailor your resume for each application instead of sending one generic version.",
            "Apply consistently while improving your portfolio and interview stories.",
        ]
    else:
        answer = (
            f"For {role}, the strongest approach is to keep building proof, show measurable impact, and connect your work to the job description. "
            f"Focus on the gaps that matter most for this role and improve them with one concrete project, one updated resume, and one interview-ready story.{recent_context}"
        )
        steps = [
            "Map your current strengths against the role requirements and identify 2-3 missing areas.",
            "Build or improve one project that demonstrates your strongest technical ability.",
            "Align your resume wording with the job description and quantify results.",
            "Practice concise explanations of your work so you can speak clearly in interviews.",
        ]

    conversation_history = []
    for item in previous_history[-5:]:
        conversation_history.append(item)
    conversation_history.append({
        "question": question,
        "answer": answer,
    })

    return {
        "question": question,
        "answer": answer,
        "summary": answer,
        "steps": steps,
        "focus_skills": focus_skills[:5],
        "role": role,
        "conversation_history": conversation_history,
    }
