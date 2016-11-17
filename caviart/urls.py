
from jwt_knox.viewsets import JWTKnoxAPIViewSet

from . import viewsets
from rest_framework_extensions.routers import ExtendedDefaultRouter


router = ExtendedDefaultRouter(trailing_slash=False)
router.register(r'auth', JWTKnoxAPIViewSet, base_name='jwt_knox')
router.register(r'users', viewsets.UserProfileViewSet)

with router.register(r'projects',
                     viewsets.ProjectViewSet,
                     base_name='project') as project:

    with project.register(r'files',
                          viewsets.ProjectFileViewSet,
                          base_name='projectfile') as file:
        with file.register(r'vu', # verification-unit
                           viewsets.VerificationFileViewSet,
                           base_name='verificationfile') as verification:
            verification.register(r'proofs',
                                  viewsets.ProofObligationViewSet,
                                  base_name='proofobligation')


urlpatterns = []
urlpatterns += router.urls
