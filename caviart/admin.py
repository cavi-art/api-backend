from django.contrib import admin

from caviart.models import (Project, ProjectFile, ProofObligation,
    VerificationFile)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    pass

@admin.register(ProofObligation)
class VerificationFileAdmin(admin.ModelAdmin):
    pass

@admin.register(VerificationFile)
class ProofObligationAdmin(admin.ModelAdmin):
    pass

