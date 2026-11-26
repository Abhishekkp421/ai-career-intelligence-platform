
from django.db import models
from django.conf import settings


class JobRole(models.Model):

    title = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Question(models.Model):

    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('hr', 'HR'),
        ('dsa', 'DSA'),
        ('project', 'Project Based'),
        ('situational', 'Situational'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    question_text = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )

    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )

    reference_answer = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:60]


class InterviewSession(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interviews'
    )

    resume = models.ForeignKey(
        'resumes.Resume',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    job_role = models.ForeignKey(
        JobRole,
        on_delete=models.PROTECT
    )

    difficulty = models.CharField(
        max_length=20,
        choices=Question.DIFFICULTY_CHOICES,
        default='medium'
    )

    category = models.CharField(
        max_length=20,
        choices=Question.CATEGORY_CHOICES,
        default='technical'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total_questions = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.job_role.title}"


class InterviewQuestion(models.Model):

    session = models.ForeignKey(
        InterviewSession,
        on_delete=models.CASCADE,
        related_name='session_questions'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT
    )

    sequence = models.PositiveIntegerField()

    class Meta:
        ordering = ['sequence']
        constraints = [
            models.UniqueConstraint(
                fields=['session', 'sequence'],
                name='unique_session_question_sequence'
            )
        ]

    def __str__(self):
        return f"Question {self.sequence} - {self.session}"


class InterviewAnswer(models.Model):

    interview_question = models.OneToOneField(
        InterviewQuestion,
        on_delete=models.CASCADE,
        related_name='answer'
    )

    answer_text = models.TextField(blank=True)

    audio_file = models.FileField(
        upload_to='interviews/answers/',
        null=True,
        blank=True
    )

    score = models.PositiveSmallIntegerField(
        null=True,
        blank=True
    )

    ai_feedback = models.TextField(blank=True)

    answered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Answer - {self.interview_question}"
