from django.db import models
from django.conf import settings
from resumes.models import Resume
from jobs.models import JobDescription


class ResumeJobMatch(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume_job_matches'
    )

    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='job_matches'
    )

    job = models.ForeignKey(
        JobDescription,
        on_delete=models.CASCADE,
        related_name='resume_matches'
    )

    match_score = models.FloatField(default=0)

    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    preferred_matched_skills = models.JSONField(default=list)

    score_breakdown = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'resume', 'job'],
                name='unique_user_resume_job_match'
            )
        ]

    def __str__(self):
        return f"{self.resume} - {self.job} ({self.match_score}%)"
