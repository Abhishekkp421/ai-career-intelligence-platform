
import os
import json
from google import genai


def analyze_resume(extracted_text):
    """
    Analyze resume text using Gemini AI.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key not found.")

    if not extracted_text or not extracted_text.strip():
        raise ValueError("Resume text is empty.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert technical resume analyzer.

    Analyze the following resume and return the result
    in valid JSON format only.

    Evaluate these areas:
    1. Overall resume score (0 to 100)
    2. Technical skills
    3. Soft skills
    4. Strengths
    5. Weaknesses
    6. Missing skills
    7. Improvement suggestions
    8. Suitable job roles

    Use this exact JSON structure:

    {{
        "score": 0,
        "technical_skills": [],
        "soft_skills": [],
        "strengths": [],
        "weaknesses": [],
        "missing_skills": [],
        "suggestions": [],
        "job_roles": []
    }}

    Give realistic feedback based only on the resume.
    Do not invent qualifications or experience.

    Resume:
    {extracted_text[:15000]}
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )
    print("Gemini Raw Response:", repr(response.text))
    print("Gemini Candidates:", response.candidates)

    if not response.text or not response.text.strip():
        raise ValueError("Gemini returned an empty response.")
    # Remove Markdown code fences from Gemini response
    cleaned_response = response.text.strip()

    if cleaned_response.startswith("```json"):
        cleaned_response = cleaned_response[7:]

    elif cleaned_response.startswith("```"):
        cleaned_response = cleaned_response[3:]

    if cleaned_response.endswith("```"):
        cleaned_response = cleaned_response[:-3]

    # Convert JSON string into Python dictionary
    result = json.loads(cleaned_response.strip())

    return result
