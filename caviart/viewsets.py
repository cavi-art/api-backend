
from django.http import HttpResponse

from rest_framework import renderers, status
from rest_framework.authentication import get_user_model
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from caviart import models, serializers
from caviart.filters import IsOwnerFilterBackend, ParentLookupMapFilterBackend
from caviart.permissions import IsOwnerOrAdmin
from rest_framework_extensions.mixins import NestedViewSetMixin


class UserProfileViewSet(ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer

    @list_route(methods=['get'])
    def register(self, request, format=None):
        return Response({
            'msg': 'To test this application send an email to the system administrator. Registrations are disabled for the moment.'})


class ProjectViewSet(ModelViewSet):
    lookup_url_kwarg = 'project_id'
    queryset = models.Project.objects.all()
    filter_backends = (IsOwnerFilterBackend,)
    permission_classes = (IsOwnerOrAdmin,)
    serializer_class = serializers.ProjectSerializer


class ProjectFileViewSet(NestedViewSetMixin, ModelViewSet):
    lookup_field = 'id'
    lookup_url_kwarg = 'file_id'
    parent_lookup_map = { 'project_id': 'project.id' }
    queryset = models.ProjectFile.objects.all()
    filter_backends = (IsOwnerFilterBackend, ParentLookupMapFilterBackend,)
    permission_classes = (IsOwnerOrAdmin,)
    serializer_class = serializers.ProjectFileSerializer
    renderer_classes = (renderers.JSONRenderer, renderers.BrowsableAPIRenderer,)

    @detail_route(methods=['get'])
    def raw(self, request, project_id=None, file_id=None, format=None):
        instance = self.get_object()
        bytes = instance.content.read()
        instance.content.close()
        return HttpResponse(bytes, content_type=instance.file_type)

    def verify(self, request, project_id=None, file_id=None, format=None):
        return Response({'detail': 'Could not verify your file.'}, status=status.HTTP_200_OK)

    def retrieve(self, request, project_id=None, file_id=None, format=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        if not format or format == 'json' or format == 'api':
            data['content'] = reverse('projectfile-raw',
                                      request=request,
                                      kwargs={'project_id': project_id,
                                              'file_id': file_id,
                                      })
        return Response(data)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.ProjectFileReadSerializer
        return self.serializer_class
    

class VerificationFileViewSet(NestedViewSetMixin, ModelViewSet):
    lookup_field = 'id'
    lookup_url_kwarg = 'vfile_id'
    parent_lookup_map = {
        'project_id': 'source.project.id',
        'file_id': 'source.id',
    }
    queryset = models.VerificationFile.objects.all()
    filter_backends = (IsOwnerFilterBackend, ParentLookupMapFilterBackend,)
    permission_classes = (IsOwnerOrAdmin,)
    serializer_class = serializers.VerificationFileSerializer

    @detail_route(methods=['get'])
    def raw(self, request, project_id=None, file_id=None, vfile_id=None, format=None):
        """Debug endpoint for testing the CLIR output that we get from a
        program transformation.

        """

        instance = self.get_object()
        bytes = instance.content.read()
        instance.content.close()
        return HttpResponse(bytes, content_type='text/plain')

    def retrieve(self, request, project_id=None, file_id=None, vfile_id=None, format=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        if not format or format == 'json' or format == 'api':
            data['content'] = reverse('verificationfile-raw',
                                      request=request,
                                      kwargs={'project_id': project_id,
                                              'file_id': file_id,
                                              'vfile_id': vfile_id,
                                      })
        return Response(data)


class ProofObligationViewSet(NestedViewSetMixin, ModelViewSet):
    lookup_field = 'id'
    lookup_url_kwarg = 'po_id'
    parent_lookup_map = {
        'project_id': 'clir.source.project.id',
        'file_id': 'clir.source.id',
        'vfile_id': 'clir.id',
    }
    queryset = models.ProofObligation.objects.all()
    filter_backends = (IsOwnerFilterBackend, ParentLookupMapFilterBackend,)
    permission_classes = (IsOwnerOrAdmin,)
    serializer_class = serializers.ProofObligationSerializer
