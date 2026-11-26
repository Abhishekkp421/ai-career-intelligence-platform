from django.views.decorators.http import require_POST
from .services import save_career_recommendation
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg

from .models import CandidateProfile,CareerRecommendation
from .forms import CandidateProfileForm

from resumes.models import Resume
from matching.models import ResumeJobMatch
from interviews.models import InterviewSession, InterviewAnswer


@login_required
def profile(request):
    profile, created = CandidateProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        form = CandidateProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.user = request.user
            candidate.save()

            messages.success(
                request,
                'Your career profile has been saved successfully!'
            )

            return redirect('career:profile')

    else:
        form = CandidateProfileForm(instance=profile)

    return render(request, 'career/profile.html', {
        'form': form,
        'profile': profile,
    })


@login_required
def career_dashboard(request):

    user = request.user

    profile, created = CandidateProfile.objects.get_or_create(
        user=user
    )

    # Resume statistics
    resumes = Resume.objects.filter(user=user)

    total_resumes = resumes.count()
    latest_resume = resumes.order_by('-uploaded_at').first()

    # Job matching statistics
    matches = ResumeJobMatch.objects.filter(user=user)

    total_matches = matches.count()
    latest_match = matches.order_by('-updated_at').first()

    average_match = matches.aggregate(
        average=Avg('match_score')
    )['average'] or 0

    # Interview statistics
    sessions = InterviewSession.objects.filter(user=user)

    total_interviews = sessions.count()

    completed_interviews = sessions.filter(
        status='completed'
    ).count()

    interview_average = InterviewAnswer.objects.filter(
        interview_question__session__user=user
    ).aggregate(
        average=Avg('score')
    )['average'] or 0

    context = {
        'profile': profile,

        'total_resumes': total_resumes,
        'latest_resume': latest_resume,

        'total_matches': total_matches,
        'latest_match': latest_match,
        'average_match': round(average_match, 2),

        'total_interviews': total_interviews,
        'completed_interviews': completed_interviews,
        'interview_average': round(interview_average, 2),

        'technical_skills': profile.technical_skills,
        'soft_skills': profile.soft_skills,
    }

    return render(
        request,
        'career/dashboard.html',
        context
    )
@login_required
@require_POST
def generate_recommendations(request):
    try:
        recommendation, roadmap = save_career_recommendation(
            request.user
        )

        messages.success(
            request,
            'Your AI career recommendations are ready!'
        )

        return redirect(
            'career:recommendation_detail',
            pk=recommendation.pk
        )

    except Exception as error:
        messages.error(
            request,
            f'Could not generate recommendations: {error}'
        )

        return redirect('career:dashboard')


@login_required
def recommendation_detail(request, pk):
    recommendation = get_object_or_404(
        CareerRecommendation,
        pk=pk,
        user=request.user
    )

    roadmap = recommendation.roadmaps.order_by(
        '-created_at'
    ).first()

    return render(request, 'career/recommendation.html', {
        'recommendation': recommendation,
        'roadmap': roadmap,
    })