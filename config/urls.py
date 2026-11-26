from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),
    path('', include('dashboard.urls')),
    path('resumes/', include('resumes.urls')),
    path('interviews/', include('interviews.urls')),
    path('evaluation/', include('evaluation.urls')),
    path('jobs/', include('jobs.urls')),
    path('matching/', include('matching.urls')),
    path('career/', include('career.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
