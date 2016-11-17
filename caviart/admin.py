from django.contrib import admin

from . import models

@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

@admin.register(models.ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Operation)
class OperationAdmin(admin.ModelAdmin):
    pass
