import os
import re
import json
from PyPDF2 import PdfReader
import google.generativeai as genai


COMMON_SKILLS = [
    "Python", "JavaScript", "TypeScript", "HTML", "CSS", "React", "Vue", "Angular",
    "Flask", "Django", "Node.js", "Express", "SQL", "PostgreSQL", "SQLite", "MongoDB",
    "Docker", "Kubernetes", "AWS", "Git", "Linux", "REST API", "GraphQL", "Tailwind",
    "Machine Learning", "Data Analysis", "Power BI", "Tableau", "C++", "Java", "C#", "Go",
    "Azure", "GCP", "DevOps", "CI/CD", "Agile", "Product Management", "Figma"
]


def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file using PyPDF2."""
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        print(f"PDF Extraction Error: {e}")
    return text.strip()


def build_ats_analysis(raw_text, parsed_data):
    """Generate a practical ATS review with an overall score and improvement suggestions."""
    text = raw_text or ""
    lower_text = text.lower()
    contact = parsed_data.get("contact", {}) or {}
    skills = parsed_data.get("skills") or []
    experience = parsed_data.get("experience") or []
    education = parsed_data.get("education") or []

    score = 88
    strengths = []
    improvements = []

    if contact.get("email") and "not found" not in str(contact.get("email", "")).lower():
        strengths.append("Contact information is present and readable.")
    else:
        improvements.append("Add a professional email address and phone number near the top of the resume.")
        score -= 12

    if skills:
        strengths.append("Relevant technical keywords were detected and can help ATS match job descriptions.")
    else:
        improvements.append("Add role-specific keywords like Python, SQL, cloud tools, or frameworks aligned with your target role.")
        score -= 12

    if experience:
        strengths.append("Work experience appears to be described in a structured way.")
    else:
        improvements.append("Expand your experience section with measurable outcomes, project names, and impact metrics.")
        score -= 12

    if not re.search(r"\d+%|\d+\+|\b\d{2,4}\b", text):
        improvements.append("Include measurable results such as percentages, time saved, revenue impact, or team size.")
        score -= 10

    if not re.search(r"\b(summary|profile|overview)\b", lower_text):
        improvements.append("Add a short professional summary at the top that matches the target role.")
        score -= 8

    if not education:
        improvements.append("Include education or certifications if they support the role and are relevant to your target jobs.")
        score -= 5

    if not improvements:
        strengths.append("This resume is already well structured for ATS scanning and job matching.")

    ats_score = max(0, min(100, score))

    return {
        "ats_score": ats_score,
        "summary": "This resume is generally ATS-friendly but can be improved with better keyword coverage and measurable results.",
        "strengths": strengths,
        "improvements": improvements,
        "keywords": [str(skill) for skill in skills[:10]],
        "recommendations": improvements,
    }


def fallback_parse_text(text):
    """Basic Regex/Heuristic parser if AI service is not available."""
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    phones = re.findall(r'\+?\d[\d -]{8,}\d', text)

    extracted_skills = [skill for skill in COMMON_SKILLS if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE)]

    parsed_data = {
        "summary": "Parsed via Rule-Based Extractor.",
        "contact": {
            "email": emails[0] if emails else "Not found",
            "phone": phones[0] if phones else "Not found"
        },
        "skills": extracted_skills,
        "experience": ["Extracted text length: " + str(len(text)) + " characters."],
        "education": []
    }
    parsed_data["ats_analysis"] = build_ats_analysis(text, parsed_data)
    return parsed_data


def parse_resume_content(pdf_path, gemini_api_key=None):
    """Extracts text and structures resume content using Gemini or fallback parser."""
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text:
        return "", {"error": "Could not extract readable text from PDF.", "ats_analysis": {"ats_score": 0, "improvements": ["Upload a readable PDF with text content."]}}

    # Attempt AI Parsing if key is provided
    if gemini_api_key and len(gemini_api_key.strip()) > 0:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            Analyze the following resume text and extract the data strictly as JSON with key fields:
            "summary" (string), "contact" (object with email, phone), "skills" (array of strings),
            "experience" (array of strings), "education" (array of strings).

            Resume Text:
            {raw_text[:4000]}
            """
            response = model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                parsed_data = json.loads(json_match.group(0))
                if "ats_analysis" not in parsed_data:
                    parsed_data["ats_analysis"] = build_ats_analysis(raw_text, parsed_data)
                return raw_text, parsed_data
        except Exception as e:
            print(f"Gemini AI Parsing failed/fallback triggered: {e}")

    parsed_data = fallback_parse_text(raw_text)
    return raw_text, parsed_data