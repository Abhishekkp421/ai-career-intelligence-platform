from django.urls import path
from . import views, chat_views

app_name = 'career'

urlpatterns = [
    path('', views.profile, name='profile'),

    path('dashboard/', views.career_dashboard, name='dashboard'),

    path(
        'generate-recommendations/',
        views.generate_recommendations,
        name='generate_recommendations'
    ),

    path(
        'recommendation/<int:pk>/',
        views.recommendation_detail,
        name='recommendation_detail'
    ),

    # AI Career Assistant
    path('assistant/', chat_views.chat_home, name='chat_home'),

    path(
        'assistant/new/',
        chat_views.create_conversation,
        name='create_conversation'
    ),

    path(
        'assistant/<int:pk>/',
        chat_views.chat_conversation,
        name='chat_conversation'
    ),

    path(
        'assistant/<int:pk>/send/',
        chat_views.send_chat_message,
        name='send_chat_message'
    ),
    path(
    'assistant/<int:pk>/delete/',
    chat_views.delete_conversation,
    name='delete_conversation'
    ),
]