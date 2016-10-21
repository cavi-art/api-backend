
from collections import OrderedDict

from django.http import HttpResponse

from rest_framework import renderers, status
from rest_framework.authentication import get_user_model
from rest_framework.decorators import detail_route, list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ViewSet, ModelViewSet, ReadOnlyModelViewSet

from caviart import models, serializers, tools
from caviart.filters import IsOwnerFilterBackend, ParentLookupMapFilterBackend
from caviart.permissions import IsOwnerOrAdmin
from rest_framework_extensions.mixins import NestedViewSetMixin


class UserProfileViewSet(ReadOnlyModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated,)

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


class OperationViewSet(NestedViewSetMixin, ModelViewSet):
    """This implements different Operations that may exist at a given
point in time.

    """
    lookup_url_kwarg = 'operation_id'
    parent_lookup_map = {
        'project_id': 'project.id',
    }
    queryset = models.Operation.objects.all()
    serializer_class = serializers.OperationSerializer

    @list_route(url_path='list')
    def operations(self, request, **kwargs):
        tool_list = tools.default_task_queue.get_registered_tools()
        return Response({
            'operations': tool_list,
        })

    def list(self, request, **kwargs):
        data = super(OperationViewSet, self).list(self, request, **kwargs)
        response = OrderedDict()
        response['elements'] = data.data
        response['operations'] = tools.default_task_queue.get_registered_tools()
        return Response(response)

    @detail_route()
    def run(self, request, **kwargs):
        op = self.get_object()
        op = tools.default_task_queue.run_task(op)

        serializer = self.get_serializer(op)
        return Response(serializer.data)


    def perform_create(self, serializer):
        serializer.save(sent_by=self.request.user)
