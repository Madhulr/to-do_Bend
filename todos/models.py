from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    admin_reply = models.TextField(blank=True, null=True)
    user = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Feedback from {self.user or 'anonymous'}"
