import uuid

from django.conf import settings
from django.db import models


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        return ("project-%s" % self.uuid)


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, related_name='files')
    path = models.CharField(max_length=255)
    file_type = models.CharField(max_length=80)
    last_mod = models.DateField(auto_now=True)
    content = models.FileField()

    def natural_key(self):
        return (self.project, self.path)

    class Meta:
        unique_together = (('project', 'path'),) # natural key

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
    
