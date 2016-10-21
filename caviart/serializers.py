
from django.utils import timezone

from rest_framework.authentication import get_user_model
from rest_framework.fields import HiddenField, ListField, ModelField, SerializerMethodField
from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedModelSerializer, SlugRelatedField, ValidationError

from caviart import models
from rest_framework_extensions.fields import NestedHyperlinkedIdentityField
from rest_framework_extensions.serializers import (
    NestedHyperlinkedModelSerializer)


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'username', 'first_name', 'last_name', 'email')


class ProjectSerializer(HyperlinkedModelSerializer):
    files = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name='projectfile-list',
    )
    operations = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name='operation-list',
    )
    class Meta:
        model = models.Project
        depth = 0
        fields = ('url', 'owner', 'files', 'operations')
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'project_id'
            }
        }

class OperationSerializer(NestedHyperlinkedModelSerializer):
    sent_at = HiddenField(default=timezone.now)
    class Meta:
        model = models.Operation
        depth = 0
        extra_kwargs = {
            'url': {
                'lookup_map': 'caviart.viewsets.OperationViewSet'
            },
            'project': {
                'lookup_map': 'caviart.viewsets.ProjectViewSet'
            },
            'sent_by': {
                'lookup_map': 'caviart.viewsets.UserProfileViewSet',
                'read_only': True,
            },
        }

class ProjectFileSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = models.ProjectFile
        fields = ('url', 'project', 'path', 'content', 'file_type', 'last_mod')
        extra_kwargs = {
            'url': {
                'lookup_map': 'caviart.viewsets.ProjectFileViewSet'
            },
            'project': {
                'lookup_map': 'caviart.viewsets.ProjectViewSet',
            },
            'content': {
                'use_url': False,
            }
        }

class ProjectFileReadSerializer(NestedHyperlinkedModelSerializer):
    content = NestedHyperlinkedIdentityField(
        read_only=True,
        view_name='projectfile-raw',
    )

    class Meta:
        model = models.ProjectFile
        fields = ('url', 'project', 'path', 'content', 'file_type', 'last_mod')
        extra_kwargs = {
            'url': {
                'lookup_map': 'caviart.viewsets.ProjectFileViewSet'
            },
            'project': {
                'lookup_map': 'caviart.viewsets.ProjectViewSet',
            },
        }
