from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from resumes.models import Resume
from jobs.models import JobDescription
from .models import ResumeJobMatch
from .services import match_resume_with_job


@login_required
def matching_home(request):
    resumes = Resume.objects.filter(
        user=request.user
    ).order_by('-uploaded_at')

    jobs = JobDescription.objects.filter(
        user=request.user,
        is_analyzed=True
    ).order_by('-created_at')

    matches = ResumeJobMatch.objects.filter(
        user=request.user
    ).select_related('resume', 'job')[:10]

    if request.method == 'POST':
        resume_id = request.POST.get('resume_id')
        job_id = request.POST.get('job_id')

        if not resume_id or not job_id:
            messages.error(
                request,
                'Please select both a resume and a job.'
            )
            return redirect('matching:home')

        resume = get_object_or_404(
            Resume,
            pk=resume_id,
            user=request.user
        )

        job = get_object_or_404(
            JobDescription,
            pk=job_id,
            user=request.user,
            is_analyzed=True
        )

        if not resume.extracted_text:
            messages.error(
                request,
                'Selected resume has no extracted text. '
                'Please upload and analyze it again.'
            )
            return redirect('matching:home')

        try:
            result = match_resume_with_job(
                resume.extracted_text,
                job.parsed_data
            )

            match, created = ResumeJobMatch.objects.update_or_create(
                user=request.user,
                resume=resume,
                job=job,
                defaults={
                    'match_score': result['match_score'],
                    'matched_skills': result['matched_skills'],
                    'missing_skills': result['missing_skills'],
                    'preferred_matched_skills': result[
                        'preferred_matched_skills'
                    ],
                    'score_breakdown': result['score_breakdown'],
                    'recommendations': result['recommendations'],
                }
            )

            messages.success(
                request,
                'Resume and job matching completed successfully!'
            )

            return redirect(
                'matching:result',
                pk=match.pk
            )

        except Exception as error:
            messages.error(
                request,
                f'Matching failed: {error}'
            )
            return redirect('matching:home')

    return render(request, 'matching/home.html', {
        'resumes': resumes,
        'jobs': jobs,
        'matches': matches,
    })


@login_required
def matching_result(request, pk):
    match = get_object_or_404(
        ResumeJobMatch.objects.select_related('resume', 'job'),
        pk=pk,
        user=request.user
    )

    return render(request, 'matching/result.html', {
        'match': match
    })
