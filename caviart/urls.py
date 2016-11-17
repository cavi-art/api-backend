
from rest_framework_extensions.routers import ExtendedDefaultRouter

from . import viewsets

router = ExtendedDefaultRouter(trailing_slash=False)
router.register(r'users', viewsets.UserProfileViewSet)

with router.register(r'projects',
                     viewsets.ProjectViewSet,
                     base_name='project') as project:

    project.register(r'files',
                     viewsets.ProjectFileViewSet,
                     base_name='projectfile')


urlpatterns = []
urlpatterns += router.urls
