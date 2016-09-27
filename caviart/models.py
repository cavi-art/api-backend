from __future__ import unicode_literals

import uuid

from django.conf import settings
from django.db import models
from six import python_2_unicode_compatible


class OwningQuerySet(models.QuerySet):
    def for_owner(self, user=None):
        if not user.is_authenticated():
            user = None

        owner_field = 'owner'
        if hasattr(self.model, 'OWNER_FIELD'):
            owner_field = self.model.OWNER_FIELD
            # raise Exception("Owner field on model %s is %s" % (self.model, owner_field))
        return self.filter(**{owner_field: user})
    pass


@python_2_unicode_compatible
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)

    objects = OwningQuerySet.as_manager()

    OWNER_FIELD = 'owner'

    def __str__(self):
        return ("project-%s" % self.id)


@python_2_unicode_compatible
class ProjectFile(models.Model):
    project = models.ForeignKey(Project, related_name='files')
    path = models.CharField(max_length=255)
    file_type = models.CharField(max_length=80)
    last_mod = models.DateTimeField(auto_now=True)
    content = models.FileField()

    def natural_key(self):
        return (self.project, self.path)

    def verified(self):
        # FIXME check last_mod dates
        if self.verification_file_set.count() > 0:
            return all([file.verified() for file in self.verification_file_set.all()])
        return False

    def __str__(self):
        return ("file %s (%s) in %s" % (self.path, self.file_type, self.project))

    objects = OwningQuerySet.as_manager()

    OWNER_FIELD = 'project__' + Project.OWNER_FIELD

    class Meta:
        unique_together = (('project', 'path'),) # natural key


class VerificationFile(models.Model):
    source = models.ForeignKey(ProjectFile, related_name='verification_file_set')
    last_mod = models.DateTimeField(auto_now=True)
    content = models.FileField()

    OWNER_FIELD = 'source__' + ProjectFile.OWNER_FIELD

    def verified(self):
        return all([x == 'V' for x in self.proof_obligations.all().values('status')])


class ProofObligation(models.Model):
    STATUS_CHOICES = (('V', 'Verified'),
                      ('N', 'Not verified'),
                      ('X', 'Undetermined'))

    clir = models.ForeignKey(VerificationFile, related_name='proof_obligations')
    last_mod = models.DateTimeField(auto_now=True)
    goal = models.CharField(max_length=100)
    strategies = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='X')

    OWNER_FIELD = 'clir__' + VerificationFile.OWNER_FIELD
