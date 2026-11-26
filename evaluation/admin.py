from django.contrib import admin

from .models import (
    Answer,
    Evaluation,
    PerformanceReport
)

admin.site.register(Answer)
admin.site.register(Evaluation)
admin.site.register(PerformanceReport)
