from resumes.models import Resume
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from .models import (
    JobRole,
    InterviewSession,
    Question,
    InterviewQuestion,
    InterviewAnswer
)

from .services import (
    generate_interview_questions,
    evaluate_interview_answer,
    translate_interview_question,
    generate_adaptive_followup
)


# =====================================
# ADAPTIVE DIFFICULTY
# =====================================

def get_next_difficulty(current_difficulty, score):

    levels = ['easy', 'medium', 'hard']

    current_index = levels.index(current_difficulty)

    if score <= 3:
        next_index = max(0, current_index - 1)

    elif score >= 8:
        next_index = min(2, current_index + 1)

    else:
        next_index = current_index

    return levels[next_index]



def format_feedback(evaluation):
    dimensions = [
        ("Accuracy", evaluation.get("accuracy", 0)),
        ("Relevance", evaluation.get("relevance", 0)),
        ("Completeness", evaluation.get("completeness", 0)),
        ("Reasoning", evaluation.get("reasoning", 0)),
        ("Communication", evaluation.get("communication", 0)),
    ]

    dimension_text = "\n".join(
        f"{name}: {score}/10"
        for name, score in dimensions
    )

    strengths = "\n".join(
        f"- {item}"
        for item in evaluation.get("strengths", [])
    )

    missing = "\n".join(
        f"- {item}"
        for item in evaluation.get("missing_points", [])
    )

    return (
        f"Overall Score: {evaluation['score']}/10\n\n"
        f"Evaluation Breakdown:\n{dimension_text}\n\n"
        f"Feedback:\n{evaluation['feedback']}\n\n"
        f"Strengths:\n{strengths}\n\n"
        f"Missing Points:\n{missing}\n\n"
        f"Improvement:\n{evaluation['improvement']}\n\n"
        f"Ideal Answer:\n{evaluation['ideal_answer']}"
    )


# =====================================
# INTERVIEW SETUP
# =====================================


@login_required
def interview_setup(request):

    job_roles = JobRole.objects.filter(is_active=True)
    resumes = Resume.objects.filter(
        user=request.user
    ).order_by('-uploaded_at')

    if request.method == 'POST':

        role_id = request.POST.get('job_role')
        difficulty = request.POST.get('difficulty')
        category = request.POST.get('category')
        resume_id = request.POST.get('resume')

        role = JobRole.objects.filter(
            id=role_id,
            is_active=True
        ).first()

        valid_difficulties = [
            choice[0]
            for choice in Question.DIFFICULTY_CHOICES
        ]

        valid_categories = [
            choice[0]
            for choice in Question.CATEGORY_CHOICES
        ]

        selected_resume = None

        if resume_id:
            selected_resume = Resume.objects.filter(
                id=resume_id,
                user=request.user
            ).first()

            if not selected_resume:
                messages.error(
                    request,
                    'Invalid resume selection.'
                )

                return redirect('interviews:setup')

            if not selected_resume.extracted_text:
                messages.error(
                    request,
                    'Please analyze your selected resume first.'
                )

                return redirect('interviews:setup')

        if (
            not role
            or difficulty not in valid_difficulties
            or category not in valid_categories
        ):
            messages.error(
                request,
                'Please select valid interview options.'
            )

            return redirect('interviews:setup')

        try:
            generated_questions = generate_interview_questions(
                job_role=role.title,
                difficulty=difficulty,
                category=category,
                resume_text=(
                    selected_resume.extracted_text
                    if selected_resume else None
                )
            )

            with transaction.atomic():

                session = InterviewSession.objects.create(
                    user=request.user,
                    resume=selected_resume,
                    job_role=role,
                    difficulty=difficulty,
                    category=category,
                    status='in_progress',
                    total_questions=len(generated_questions)
                )

                for index, item in enumerate(
                    generated_questions,
                    start=1
                ):

                    question = Question.objects.create(
                        question_text=item['question_text'],
                        reference_answer=item['reference_answer'],
                        category=category,
                        difficulty=difficulty
                    )

                    InterviewQuestion.objects.create(
                        session=session,
                        question=question,
                        sequence=index
                    )

            messages.success(
                request,
                'Personalized interview generated successfully!'
            )

            return redirect(
                'interviews:room',
                session_id=session.id
            )

        except Exception as e:

            print("Interview Generation Error:", str(e))

            messages.error(
                request,
                'Unable to generate interview. Please try again.'
            )

            return redirect('interviews:setup')

    return render(
        request,
        'interviews/setup.html',
        {
            'job_roles': job_roles,
            'resumes': resumes
        }
    )

# =====================================
# INTERVIEW ROOM
# =====================================

@login_required
def interview_room(request, session_id):

    session = get_object_or_404(
        InterviewSession,
        id=session_id,
        user=request.user
    )

    questions = session.session_questions.select_related(
        'question'
    ).all()

    if request.method == 'POST':

        # =================================
        # TRANSLATE QUESTION
        # =================================

        if request.POST.get('action') == 'translate':

            if session.category not in ['hr', 'situational']:
                return JsonResponse({
                    'success': False,
                    'message': 'Translation is not available for this category.'
                }, status=400)

            question_id = request.POST.get('question_id')

            interview_question = get_object_or_404(
                InterviewQuestion,
                id=question_id,
                session=session
            )

            try:

                translated_question = translate_interview_question(
                    interview_question.question.question_text
                )

                return JsonResponse({
                    'success': True,
                    'translated_question': translated_question
                })

            except Exception as e:

                print("Translation Error:", str(e))

                return JsonResponse({
                    'success': False,
                    'message': 'Question translation failed.'
                }, status=500)


        # =================================
        # FINISH INTERVIEW
        # =================================

        if request.POST.get('action') == 'finish':

            answers = InterviewAnswer.objects.filter(
                interview_question__session=session
            ).select_related(
                'interview_question__question'
            )

            if answers.count() != questions.count():

                return JsonResponse({
                    'success': False,
                    'message': 'Please answer all questions before finishing.'
                }, status=400)

            try:

                # Evaluate only answers that have not
                # already been evaluated during saving.

                for answer in answers:

                    if answer.score is not None:
                        continue

                    question = answer.interview_question.question

                    evaluation = evaluate_interview_answer(
                        question.question_text,
                        question.reference_answer,
                        answer.answer_text
                    )

                    answer.score = evaluation['score']
                    answer.ai_feedback = format_feedback(evaluation)
                    answer.answered_at = timezone.now()

                    answer.save(update_fields=[
                        'score',
                        'ai_feedback',
                        'answered_at'
                    ])

                session.status = 'completed'
                session.completed_at = timezone.now()

                session.save(update_fields=[
                    'status',
                    'completed_at'
                ])

                return JsonResponse({
                    'success': True,
                    'message': 'Interview evaluated successfully!'
                })

            except Exception as e:

                print("Evaluation Error:", str(e))

                return JsonResponse({
                    'success': False,
                    'message': 'Evaluation failed. Please try again.'
                }, status=500)


        # =================================
        # SAVE ANSWER + ADAPTIVE QUESTION
        # =================================

        if session.status == 'completed':

            return JsonResponse({
                'success': False,
                'message': 'This interview is already completed.'
            }, status=400)

        question_id = request.POST.get('question_id')

        answer_text = request.POST.get(
            'answer_text',
            ''
        ).strip()

        interview_question = get_object_or_404(
            InterviewQuestion,
            id=question_id,
            session=session
        )

        try:

            answer, created = InterviewAnswer.objects.get_or_create(
                interview_question=interview_question
            )

            answer_changed = answer.answer_text != answer_text
            needs_evaluation = answer.score is None or answer_changed

            answer.answer_text = answer_text
            answer.save(update_fields=['answer_text'])

            response_data = {
                'success': True,
                'message': 'Answer saved successfully!',
                'adaptive_question': None
            }

            # Do not generate an adaptive question
            # for an empty answer.

            if not answer_text:
                return JsonResponse(response_data)

            # Avoid unnecessary Gemini requests if
            # the answer has not changed.

            if not needs_evaluation:
                return JsonResponse(response_data)

            question = interview_question.question

            # Evaluate the current answer immediately.

            evaluation = evaluate_interview_answer(
                question.question_text,
                question.reference_answer,
                answer_text
            )

            answer.score = evaluation['score']
            answer.ai_feedback = format_feedback(evaluation)
            answer.answered_at = timezone.now()

            answer.save(update_fields=[
                'score',
                'ai_feedback',
                'answered_at'
            ])

            # Find the next existing question slot.

            next_interview_question = session.session_questions.filter(
                sequence__gt=interview_question.sequence
            ).select_related(
                'question'
            ).order_by(
                'sequence'
            ).first()

            if not next_interview_question:
                return JsonResponse(response_data)

            # Do not replace a question that the candidate
            # has already answered.

            next_answer = InterviewAnswer.objects.filter(
                interview_question=next_interview_question
            ).first()

            if next_answer and next_answer.answer_text.strip():
                return JsonResponse(response_data)

            # Determine adaptive difficulty.

            next_difficulty = get_next_difficulty(
                question.difficulty,
                evaluation['score']
            )

            # Generate personalized follow-up.

            adaptive_data = generate_adaptive_followup(
                job_role=session.job_role.title,
                category=session.get_category_display(),
                previous_question=question.question_text,
                reference_answer=question.reference_answer,
                candidate_answer=answer_text,
                evaluation_score=evaluation['score'],
                next_difficulty=next_difficulty
            )

            # Replace the next question in the existing sequence.

            with transaction.atomic():

                new_question = Question.objects.create(
                    question_text=adaptive_data['question_text'],
                    reference_answer=adaptive_data['reference_answer'],
                    category=session.category,
                    difficulty=next_difficulty
                )

                next_interview_question.question = new_question

                next_interview_question.save(
                    update_fields=['question']
                )

            response_data['adaptive_question'] = {
                'question_id': next_interview_question.id,
                'question_text': new_question.question_text,
                'difficulty': new_question.difficulty,
                'sequence': next_interview_question.sequence
            }

            response_data['message'] = (
                'Answer evaluated. Your next personalized question is ready!'
            )

            return JsonResponse(response_data)

        except Exception as e:

            print("Adaptive Interview Error:", str(e))

            return JsonResponse({
                'success': False,
                'message': (
                    'Answer processing failed. Please try saving again.'
                )
            }, status=500)


    # =================================
    # RESTORE PREVIOUS ANSWERS
    # =================================

    for item in questions:

        item.saved_answer = (
            item.answer.answer_text
            if hasattr(item, 'answer')
            else ''
        )

    return render(request, 'interviews/room.html', {
        'session': session,
        'questions': questions
    })


# =====================================
# INTERVIEW RESULT
# =====================================

@login_required
def interview_result(request, session_id):

    session = get_object_or_404(
        InterviewSession,
        id=session_id,
        user=request.user,
        status='completed'
    )

    answers = InterviewAnswer.objects.filter(
        interview_question__session=session
    ).select_related(
        'interview_question__question'
    ).order_by(
        'interview_question__sequence'
    )

    total_questions = answers.count()

    total_score = sum(
        answer.score or 0 for answer in answers
    )

    max_score = total_questions * 10

    percentage = (
        round((total_score / max_score) * 100, 2)
        if max_score else 0
    )

    context = {
        'session': session,
        'answers': answers,
        'total_questions': total_questions,
        'total_score': total_score,
        'max_score': max_score,
        'percentage': percentage,
    }

    return render(
        request,
        'interviews/result.html',
        context
    )


# =====================================
# INTERVIEW HISTORY
# =====================================

@login_required
def interview_history(request):

    sessions = InterviewSession.objects.filter(
        user=request.user
    ).select_related(
        'job_role'
    ).order_by('-created_at')

    history = []

    for session in sessions:

        answers = InterviewAnswer.objects.filter(
            interview_question__session=session
        )

        answered_questions = answers.exclude(
            answer_text=''
        ).count()

        evaluated_answers = answers.filter(
            score__isnull=False
        )

        total_score = sum(
            answer.score or 0 for answer in evaluated_answers
        )

        total_questions = session.total_questions
        max_score = total_questions * 10

        percentage = (
            round((total_score / max_score) * 100, 2)
            if session.status == 'completed' and max_score > 0
            else 0
        )

        history.append({
            'session': session,
            'answered_questions': answered_questions,
            'total_questions': total_questions,
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
        })

    return render(
        request,
        'interviews/history.html',
        {'history': history}
    )
