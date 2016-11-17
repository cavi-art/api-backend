from __future__ import unicode_literals

import os, shutil, uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from six import python_2_unicode_compatible
from . import tools


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

    def get_project_root(self):
        return os.path.join(settings.MEDIA_ROOT, self.id.hex)

    def __str__(self):
        return ("project-%s" % self.id)

@receiver(pre_save, sender=Project)
def create_dir_on_project_creation(sender, instance, **kwargs):
    os.mkdir(instance.get_project_root(), mode=0o775)

@receiver(pre_delete, sender=Project)
def remove_dir_recursively_on_project_deletion(sender, instance, **kwargs):
    shutil.rmtree(instance.get_project_root())


class Operation(models.Model):
    STATUS_CHOICES = (('P', 'Planned'),
                      ('R', 'Running'),
                      ('F', 'Finished'),
                      ('X', 'Crashed'),
    )

    type = models.CharField(
        max_length=40,
        choices=tools.default_task_queue.get_registered_tool_choices(),
    )
    project = models.ForeignKey(Project)
    triggered_by = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    sent_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(choices=STATUS_CHOICES, max_length=10)
    log = models.TextField(null=True, blank=True)


def get_file_storage(instance, filename):
    if hasattr(instance, 'project'):
        project = instance.project.id.hex

    path = ''
    if hasattr(instance, 'path'):
        path = instance.path

    return os.path.join(project, path)


@python_2_unicode_compatible
class ProjectFile(models.Model):
    project = models.ForeignKey(Project, related_name='files')
    path = models.CharField(max_length=255)
    file_type = models.CharField(max_length=80)
    last_mod = models.DateTimeField(auto_now=True)
    content = models.FileField(upload_to=get_file_storage)

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

@receiver(pre_delete, sender=ProjectFile)
def really_remove_file_on_database_deletion(sender, instance, **kwargs):
    os.unlink(os.path.join(
        instance.project.get_project_root(),
        instance.path
        )
    )
