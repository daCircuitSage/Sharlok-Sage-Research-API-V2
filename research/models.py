from django.db import models

from django.conf import settings
from django.db import models


class ResearchResults(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True,
                             related_name='research_user')
    topic = models.CharField(max_length=800)
    report = models.TextField(blank=True)
    confidence = models.FloatField(default=0.0)
    plan = models.TextField(blank=True)
    verification = models.JSONField(default=dict, blank=True)
    critic = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username} - {self.topic}"