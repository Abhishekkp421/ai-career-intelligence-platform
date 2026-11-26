
from django.urls import path
from . import views

app_name = 'interviews'

urlpatterns = [
    path('setup/', views.interview_setup, name='setup'),
    path('room/<int:session_id>/', views.interview_room, name='room'),
    path(
    'result/<int:session_id>/',
    views.interview_result,
    name='result'
),
path('history/', views.interview_history, name='history'),
]
