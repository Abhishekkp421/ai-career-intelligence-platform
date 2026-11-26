# AI Career Intelligence & Assessment Platform

An AI-powered career guidance and assessment platform designed to help candidates analyze their resumes, identify skill gaps, match job descriptions, practice interviews, and track career readiness.

## Key Features

- **AI Resume Intelligence:** Extracts resume content and generates AI-powered analysis.
- **Job Intelligence:** Analyzes job descriptions and identifies required skills.
- **Resume–Job Matching:** Calculates compatibility scores and highlights missing skills.
- **AI Mock Interviews:** Supports technical, HR, DSA, and situational interview practice.
- **AI Evaluation:** Provides feedback and performance insights.
- **Performance Analytics:** Tracks interview performance and progress.
- **Career Intelligence:** Generates personalized career recommendations and learning roadmaps.
- **AI Career Assistant:** Provides context-aware career guidance and interview preparation support.

## Technology Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Database:** MySQL
- **AI Integration:** Google Gemini API
- **NLP & Resume Processing:** PyMuPDF
- **Analytics:** Chart.js
- **Voice Features:** Browser Speech API

## Project Structure

```text
ai_interview_system/
├── accounts/
├── career/
├── config/
├── dashboard/
├── evaluation/
├── interviews/
├── jobs/
├── matching/
├── resumes/
├── templates/
├── static/
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Installation and Setup

1. Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ai_interview_system
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root using `.env.example` as