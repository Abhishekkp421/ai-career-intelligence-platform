
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from resumes.models import Resume
from interviews.models import InterviewSession, InterviewAnswer


@login_required
def home(request):

    user = request.user

    # 1. Total resumes uploaded
    total_resumes = Resume.objects.filter(
        user=user
    ).count()

    # 2. Total interview sessions
    total_sessions = InterviewSession.objects.filter(
        user=user
    ).count()

    # 3. Completed interviews
    completed_sessions = InterviewSession.objects.filter(
        user=user,
        status='completed'
    )

    completed_count = completed_sessions.count()

    # 4. Average interview performance
    session_percentages = []

    for session in completed_sessions:

        answers = InterviewAnswer.objects.filter(
            interview_question__session=session,
            score__isnull=False
        )

        total_score = sum(
            answer.score or 0 for answer in answers
        )

        max_score = session.total_questions * 10

        if max_score > 0:
            percentage = (total_score / max_score) * 100
            session_percentages.append(percentage)

    average_score = (
        round(sum(session_percentages) / len(session_percentages), 2)
        if session_percentages else 0
    )

    context = {
        'total_resumes': total_resumes,
        'total_sessions': total_sessions,
        'completed_count': completed_count,
        'average_score': average_score,
    }

    return render(
        request,
        'dashboard/home.html',
        context
    )
