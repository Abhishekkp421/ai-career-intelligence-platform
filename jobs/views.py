from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import JobDescription
from .forms import JobDescriptionForm
from .services import (
    extract_text_from_pdf,
    analyze_job_description,
)


@login_required
def job_list(request):
    jobs = JobDescription.objects.filter(
        user=request.user
    )

    total_jobs = jobs.count()
    analyzed_jobs = jobs.filter(
        is_analyzed=True
    ).count()

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'total_jobs': total_jobs,
        'analyzed_jobs': analyzed_jobs,
    })


@login_required
def job_create(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST, request.FILES)

        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user

            try:
                uploaded_file = form.cleaned_data.get('uploaded_file')

                if uploaded_file:
                    description = extract_text_from_pdf(uploaded_file)
                    job.source_type = 'pdf'
                else:
                    description = form.cleaned_data.get(
                        'description_text', ''
                    ).strip()
                    job.source_type = 'text'

                job.description_text = description

                # Save first so the job is retained if Gemini fails.
                job.save()

                try:
                    analysis = analyze_job_description(description)

                    job.parsed_data = analysis

                    if not job.title.strip():
                        job.title = (
                            analysis.get('job_title') or 'Untitled Role'
                        )

                    if not job.company.strip():
                        job.company = analysis.get('company') or ''

                    job.is_analyzed = True
                    job.save()

                    messages.success(
                        request,
                        'Job description analyzed successfully!'
                    )

                except Exception as error:
                    messages.warning(
                        request,
                        f'Job saved, but AI analysis failed: {error}'
                    )

                return redirect('jobs:job_detail', pk=job.pk)

            except Exception as error:
                messages.error(request, str(error))

    else:
        form = JobDescriptionForm()

    return render(request, 'jobs/job_create.html', {
        'form': form
    })


@login_required
def job_detail(request, pk):
    job = get_object_or_404(
        JobDescription,
        pk=pk,
        user=request.user
    )

    return render(request, 'jobs/job_detail.html', {
        'job': job
    })


@login_required
def analyze_job(request, pk):
    if request.method != 'POST':
        return redirect('jobs:job_detail', pk=pk)

    job = get_object_or_404(
        JobDescription,
        pk=pk,
        user=request.user
    )

    try:
        analysis = analyze_job_description(job.description_text)

        job.parsed_data = analysis

        if not job.title.strip():
            job.title = analysis.get('job_title') or 'Untitled Role'

        if not job.company.strip():
            job.company = analysis.get('company') or ''

        job.is_analyzed = True
        job.save()

        messages.success(request, 'AI analysis completed successfully!')

    except Exception as error:
        messages.error(request, f'AI analysis failed: {error}')

    return redirect('jobs:job_detail', pk=job.pk)
