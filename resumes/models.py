
from django.db import models
from django.conf import settings


class Resume(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resumes'
    )

    file = models.FileField(upload_to='resumes/')

    extracted_text = models.TextField(
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    analysis_result = models.JSONField(null=True, blank=True)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Resume"
