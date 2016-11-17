from django.db import models
from rest_framework.authentication import get_user_model


class Project(models.Model):
    uuid = models.ShortUUIDField(primary_key=True)
    owner = models.ForeignKey(get_user_model())

class ProjectFile(models.Model):
    path = models.FilePathField(max_length=255)
    file_type = models.CharField(max_length=10)
    last_mod = models.DateField(auto_now=True)
    content = models.FileField()

class VerificationFile(models.Model):
    source = models.ForeignKey(ProjectFile)
    last_mod = models.DateField(auto_now=True)
    content = models.FileField()

class ProofObligation(models.Model):
    clir = models.ForeignKey(VerificationFile)
    last_mod = models.DateField(auto_now=True)
    goal = models.CharField(max_length=100)
    strategies = models.TextField()
    status = models.CharField(max_length=1)
    
