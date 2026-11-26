import re
from collections import OrderedDict


# Common skill names and their variations
SKILL_ALIASES = {
    "python": ["python"],
    "django": ["django"],
    "flask": ["flask"],
    "java": ["java"],
    "c++": ["c++", "cpp"],
    "c": ["c programming", "c language"],
    "javascript": ["javascript", "js"],
    "html": ["html"],
    "css": ["css"],
    "react": ["react", "reactjs"],
    "node.js": ["node.js", "nodejs"],
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb"],
    "rest apis": ["rest api", "rest apis", "restful api", "restful apis"],
    "git": ["git", "github"],
    "docker": ["docker"],
    "aws": ["aws", "amazon web services"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning"],
    "data science": ["data science"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "data structures and algorithms": [
        "data structures and algorithms",
        "data structures",
        "algorithms",
        "dsa"
    ],
    "problem solving": ["problem solving"],
    "communication": ["communication", "communication skills"],
    "teamwork": ["teamwork", "team work"],
    "linux": ["linux"],
    "excel": ["excel", "ms excel"],
    "power bi": ["power bi"],
    "tableau": ["tableau"],
}


def normalize_text(text):
    """Convert text into a comparable lowercase format."""
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains_skill(text, aliases):
    """
    Check whether a skill or its alias exists in the resume.
    Uses word boundaries to avoid partial-word matches.
    """

    for alias in aliases:
        pattern = (
            r"(?<![a-z0-9+#.])"
            + re.escape(alias.lower())
            + r"(?![a-z0-9+#.])"
        )

        if re.search(pattern, text):
            return True

    return False


def extract_resume_skills(resume_text):
    """
    Extract known skills from resume text using a skill dictionary.
    """

    text = normalize_text(resume_text)
    extracted_skills = []

    for skill, aliases in SKILL_ALIASES.items():
        if contains_skill(text, aliases):
            extracted_skills.append(skill)

    return extracted_skills


def normalize_job_skills(skills):
    """
    Normalize job skills into canonical skill names.
    """

    normalized = OrderedDict()

    for skill in skills:
        if not isinstance(skill, str):
            continue

        skill = skill.strip()

        if not skill:
            continue

        for canonical_name, aliases in SKILL_ALIASES.items():
            if skill.lower() == canonical_name or skill.lower() in aliases:
                normalized[canonical_name] = canonical_name
                break
        else:
            normalized[skill.lower()] = skill

    return list(normalized.values())


def compare_skills(resume_skills, job_skills):
    """
    Compare resume skills against job requirements.
    """

    candidate_skills = set(resume_skills)

    matched = []
    missing = []

    for skill in job_skills:
        if skill in candidate_skills:
            matched.append(skill)
        else:
            missing.append(skill)

    return matched, missing


def calculate_match_score(
    required_skills,
    preferred_skills,
    matched_required,
    matched_preferred
):
    """
    Required skills carry 80% weight.
    Preferred skills carry 20% weight.

    If preferred skills are unavailable, required skills
    determine the complete score.
    """

    if not required_skills and not preferred_skills:
        return 0, {}

    if not required_skills:
        preferred_score = (
            len(matched_preferred) / len(preferred_skills)
        ) * 100

        return round(preferred_score, 2), {
            "required_score": None,
            "preferred_score": round(preferred_score, 2),
            "required_weight": 0,
            "preferred_weight": 100,
        }

    required_score = (
        len(matched_required) / len(required_skills)
    ) * 100

    if not preferred_skills:
        return round(required_score, 2), {
            "required_score": round(required_score, 2),
            "preferred_score": None,
            "required_weight": 100,
            "preferred_weight": 0,
        }

    preferred_score = (
        len(matched_preferred) / len(preferred_skills)
    ) * 100

    final_score = (
        required_score * 0.80
        + preferred_score * 0.20
    )

    return round(final_score, 2), {
        "required_score": round(required_score, 2),
        "preferred_score": round(preferred_score, 2),
        "required_weight": 80,
        "preferred_weight": 20,
    }


def generate_recommendations(missing_required, missing_preferred):
    """
    Generate practical recommendations based on missing skills.
    """

    recommendations = []

    for skill in missing_required:
        recommendations.append(
            f"Learn and practice {skill}, as it is a required job skill."
        )

    for skill in missing_preferred:
        recommendations.append(
            f"Consider learning {skill} to strengthen your profile."
        )

    if not recommendations:
        recommendations.append(
            "Your resume covers all identified job skills. "
            "Continue improving your projects and practical experience."
        )

    return recommendations


def match_resume_with_job(resume_text, job_data):
    """
    Main function: compare a resume against analyzed job requirements.
    """

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")

    if not isinstance(job_data, dict):
        raise ValueError("Invalid job analysis data.")

    required_skills = normalize_job_skills(
        job_data.get("required_skills", [])
    )

    preferred_skills = normalize_job_skills(
        job_data.get("preferred_skills", [])
    )

    # Fallback if the AI did not separate skill categories.
    if not required_skills and not preferred_skills:
        required_skills = normalize_job_skills(
            job_data.get("technical_skills", [])
        )

    if not required_skills and not preferred_skills:
        raise ValueError(
            "No job skills found. Analyze the job description first."
        )

    resume_skills = extract_resume_skills(resume_text)

    matched_required, missing_required = compare_skills(
        resume_skills,
        required_skills
    )

    matched_preferred, missing_preferred = compare_skills(
        resume_skills,
        preferred_skills
    )

    match_score, breakdown = calculate_match_score(
        required_skills,
        preferred_skills,
        matched_required,
        matched_preferred
    )

    recommendations = generate_recommendations(
        missing_required,
        missing_preferred
    )

    return {
        "match_score": match_score,
        "resume_skills": resume_skills,
        "matched_skills": matched_required,
        "missing_skills": missing_required,
        "preferred_matched_skills": matched_preferred,
        "missing_preferred_skills": missing_preferred,
        "score_breakdown": breakdown,
        "recommendations": recommendations,
    }