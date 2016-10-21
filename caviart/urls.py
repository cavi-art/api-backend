
from jwt_knox.viewsets import JWTKnoxAPIViewSet

from . import viewsets
from rest_framework_extensions.routers import ExtendedDefaultRouter


router = ExtendedDefaultRouter(trailing_slash=False)
router.register(r'auth', JWTKnoxAPIViewSet, base_name='jwt_knox')
router.register(r'users', viewsets.UserProfileViewSet)

with router.register(r'projects',
                     viewsets.ProjectViewSet,
                     base_name='project') as project:

    project.register(r'ops',
                     viewsets.OperationViewSet,
                     base_name='operation')

    project.register(r'files',
                     viewsets.ProjectFileViewSet,
                     base_name='projectfile')

urlpatterns = []
urlpatterns += router.urls
