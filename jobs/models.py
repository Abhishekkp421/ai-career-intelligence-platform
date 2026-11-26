from django.db import models
from django.conf import settings


class JobDescription(models.Model):

    SOURCE_CHOICES = [
        ('text', 'Pasted Text'),
        ('pdf', 'PDF Upload'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_descriptions'
    )

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True)

    source_type = models.CharField(
        max_length=10,
        choices=SOURCE_CHOICES,
        default='text'
    )

    description_text = models.TextField()

    uploaded_file = models.FileField(
        upload_to='job_descriptions/',
        blank=True,
        null=True
    )

    parsed_data = models.JSONField(default=dict, blank=True)
    is_analyzed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.company or 'Unknown Company'}"