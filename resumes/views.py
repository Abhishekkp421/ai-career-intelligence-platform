
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

import fitz

from .models import Resume
from .forms import ResumeUploadForm
from .services import analyze_resume


@login_required
def upload_resume(request):

    if request.method == 'POST':
        form = ResumeUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user

            # Step 1: Extract text from PDF
            try:
                pdf_document = fitz.open(
                    stream=resume.file.read(),
                    filetype="pdf"
                )

                extracted_text = ""

                for page in pdf_document:
                    extracted_text += page.get_text() + "\n"

                pdf_document.close()

                if not extracted_text.strip():
                    messages.error(
                        request,
                        'No readable text found in this PDF.'
                    )
                    return redirect('resumes:upload')

                # Step 2: Save uploaded resume
                resume.extracted_text = extracted_text
                resume.file.seek(0)
                resume.save()

            except Exception:
                messages.error(
                    request,
                    'Unable to read this PDF. Please upload a valid PDF.'
                )
                return redirect('resumes:upload')

            # Step 3: Gemini AI analysis
            try:
                analysis = analyze_resume(extracted_text)

                # Step 4: Save analysis in database
                resume.analysis_result = analysis
                resume.score = analysis.get('score')
                resume.analyzed_at = timezone.now()

                resume.save(
                    update_fields=[
                        'analysis_result',
                        'score',
                        'analyzed_at'
                    ]
                )

                messages.success(
                    request,
                    'Resume analysis completed successfully!'
                )

                # Step 5: Redirect to result page
                return redirect(
                    'resumes:result',
                    resume_id=resume.id
                )

            except Exception as e:
                print("Gemini Analysis Error:", str(e))

                messages.warning(
                    request,
                    'Resume uploaded successfully, but AI analysis failed. Please try again.'
                )

                return redirect('resumes:upload')

    else:
        form = ResumeUploadForm()

    return render(
        request,
        'resumes/upload.html',
        {'form': form}
    )


@login_required
def resume_result(request, resume_id):

    resume = get_object_or_404(
        Resume,
        id=resume_id,
        user=request.user
    )

    return render(
        request,
        'resumes/result.html',
        {'resume': resume}
    )
@login_required
def resume_history(request):

    resumes = Resume.objects.filter(
        user=request.user
    ).order_by('-uploaded_at')

    return render(
        request,
        'resumes/history.html',
        {'resumes': resumes}
    )