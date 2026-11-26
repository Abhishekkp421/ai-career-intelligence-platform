from django.db import models
from django.conf import settings


class CandidateProfile(models.Model):

    EXPERIENCE_CHOICES = [
        ('fresher', 'Fresher'),
        ('0-1', '0-1 Years'),
        ('1-3', '1-3 Years'),
        ('3+', '3+ Years'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='career_profile'
    )

    full_name = models.CharField(max_length=150, blank=True)

    phone = models.CharField(max_length=15, blank=True)

    education = models.CharField(
        max_length=200,
        blank=True
    )

    specialization = models.CharField(
        max_length=150,
        blank=True
    )

    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    technical_skills = models.JSONField(
        default=list,
        blank=True
    )

    soft_skills = models.JSONField(
        default=list,
        blank=True
    )

    target_role = models.CharField(
        max_length=150,
        blank=True
    )

    career_interests = models.TextField(blank=True)

    preferred_location = models.CharField(
        max_length=150,
        blank=True
    )

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='fresher'
    )

    career_goal = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name or self.user} - Career Profile"
class CareerRecommendation(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='career_recommendations'
    )

    target_role = models.CharField(max_length=150)

    strengths = models.JSONField(default=list, blank=True)

    skill_gaps = models.JSONField(default=list, blank=True)

    recommended_roles = models.JSONField(default=list, blank=True)

    recommended_projects = models.JSONField(default=list, blank=True)

    career_advice = models.TextField(blank=True)

    readiness_level = models.CharField(
        max_length=50,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.target_role}"


class LearningRoadmap(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_roadmaps'
    )

    recommendation = models.ForeignKey(
        CareerRecommendation,
        on_delete=models.CASCADE,
        related_name='roadmaps'
    )

    duration = models.CharField(
        max_length=20,
        default='90 days'
    )

    roadmap_data = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.duration} Roadmap"

# ==========================================
# AI CAREER ASSISTANT CHATBOT MODELS
# ==========================================

class ChatConversation(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='career_chat_conversations'
    )

    title = models.CharField(
        max_length=200,
        default='New Career Conversation'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user} - {self.title}"


class ChatMessage(models.Model):

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(
                fields=['conversation', 'created_at'],
                name='chat_conv_created_idx'
            )
        ]

    def __str__(self):
        return f"{self.role} - {self.conversation_id}"
