from django.contrib import admin

from .models import (
    JobRole,
    Question,
    InterviewSession,
    InterviewQuestion
)

admin.site.register(JobRole)
admin.site.register(Question)
admin.site.register(InterviewSession)
admin.site.register(InterviewQuestion)
