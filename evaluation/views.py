import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from interviews.models import InterviewSession, InterviewAnswer


@login_required
def performance_analytics(request):

    # Only completed interviews of logged-in user
    sessions = InterviewSession.objects.filter(
        user=request.user,
        status='completed'
    ).select_related(
        'job_role'
    ).order_by('completed_at', 'created_at')

    interview_scores = []
    category_data = {}

    total_percentage = 0
    best_score = 0

    for session in sessions:

        answers = InterviewAnswer.objects.filter(
            interview_question__session=session,
            score__isnull=False
        )

        total_score = sum(
            answer.score or 0 for answer in answers
        )

        max_score = session.total_questions * 10

        if max_score == 0:
            continue

        percentage = round(
            (total_score / max_score) * 100, 2
        )

        total_percentage += percentage
        best_score = max(best_score, percentage)

        interview_scores.append({
            'label': session.completed_at.strftime('%d %b %Y')
            if session.completed_at else session.created_at.strftime('%d %b %Y'),
            'role': session.job_role.title,
            'score': percentage,
        })

        # Category-wise performance
        category = session.get_category_display()

        if category not in category_data:
            category_data[category] = {
                'total_score': 0,
                'total_questions': 0,
            }

        category_data[category]['total_score'] += total_score
        category_data[category]['total_questions'] += session.total_questions

    completed_count = len(interview_scores)

    average_score = (
        round(total_percentage / completed_count, 2)
        if completed_count else 0
    )

    category_labels = []
    category_scores = []

    for category, data in category_data.items():

        category_max = data['total_questions'] * 10

        category_percentage = (
            round((data['total_score'] / category_max) * 100, 2)
            if category_max else 0
        )

        category_labels.append(category)
        category_scores.append(category_percentage)

    weakest_category = (
        min(
            zip(category_labels, category_scores),
            key=lambda item: item[1]
        )[0]
        if category_labels else 'Not available'
    )

    context = {
        'completed_count': completed_count,
        'average_score': average_score,
        'best_score': best_score,
        'weakest_category': weakest_category,

        'trend_labels': json.dumps([
            item['label'] for item in interview_scores
        ]),

        'trend_scores': json.dumps([
            item['score'] for item in interview_scores
        ]),

        'category_labels': json.dumps(category_labels),
        'category_scores': json.dumps(category_scores),

        'recent_interviews': list(reversed(interview_scores[-5:])),
    }

    return render(
        request,
        'evaluation/analytics.html',
        context
    )
