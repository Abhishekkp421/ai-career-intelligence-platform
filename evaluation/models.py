from django.db import models


class Answer(models.Model):

    session = models.ForeignKey(
        'interviews.InterviewSession',
        on_delete=models.CASCADE,
        related_name='answers'
    )

    question = models.ForeignKey(
        'interviews.Question',
        on_delete=models.PROTECT
    )

    answer_text = models.TextField(blank=True)

    audio_file = models.FileField(
        upload_to='recordings/',
        blank=True,
        null=True
    )

    transcript = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer - {self.session}"


class Evaluation(models.Model):

    answer = models.OneToOneField(
        Answer,
        on_delete=models.CASCADE,
        related_name='evaluation'
    )

    accuracy_score = models.FloatField(default=0)

    relevance_score = models.FloatField(default=0)

    completeness_score = models.FloatField(default=0)

    clarity_score = models.FloatField(default=0)

    total_score = models.FloatField(default=0)

    feedback = models.TextField(blank=True)

    evaluated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evaluation - {self.answer_id}"


class PerformanceReport(models.Model):

    session = models.OneToOneField(
        'interviews.InterviewSession',
        on_delete=models.CASCADE,
        related_name='performance_report'
    )

    overall_score = models.FloatField(default=0)

    strengths = models.JSONField(default=list)

    weaknesses = models.JSONField(default=list)

    recommendations = models.JSONField(default=list)

    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report - {self.session}"
