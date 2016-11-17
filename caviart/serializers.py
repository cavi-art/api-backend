
from rest_framework.authentication import get_user_model
from rest_framework.fields import ListField, SerializerMethodField
from rest_framework.reverse import reverse
from rest_framework.serializers import HyperlinkedModelSerializer

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
    class Meta:
        model = models.Project
        depth = 0
        fields = ('url', 'owner', 'files')
        extra_kwargs = {
            'url': {
                'lookup_url_kwarg': 'project_id'
            }
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
    verify_url = NestedHyperlinkedIdentityField(
        view_name='verificationfile-list',
        lookup_map='caviart.viewsets.ProjectFileViewSet',
    )

    class Meta:
        model = models.ProjectFile
        fields = ('url', 'project', 'path', 'content', 'file_type', 'last_mod', 'verified', 'verify_url')
        extra_kwargs = {
            'url': {
                'lookup_map': 'caviart.viewsets.ProjectFileViewSet'
            },
            'project': {
                'lookup_map': 'caviart.viewsets.ProjectViewSet',
            },
        }


class VerificationFileSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = models.VerificationFile
        fields = ('url', 'source', 'content', 'last_mod', 'proof_obligations')
        extra_kwargs = {
            'url': {
                'lookup_map': 'caviart.viewsets.VerificationFileViewSet'
            },
            'source': {
                'lookup_map': 'caviart.viewsets.ProjectFileViewSet',
            },
            'content': {
                'use_url': False,
            },
            'proof_obligations': {
                'read_only': True,
                'lookup_map': 'caviart.viewsets.ProofObligationViewSet'
            },
        }


class ProofObligationSerializer(NestedHyperlinkedModelSerializer):
    class Meta:
        model = models.ProofObligation
        fields = ('url', 'clir', 'last_mod', 'goal', 'strategies', 'status')
        extra_kwargs = {
            'url': {
                'lookup_map': 'caviart.viewsets.ProofObligationViewSet',
            },
            'clir': {
                'lookup_map': 'caviart.viewsets.VerificationFileViewSet',
            },
            'strategies': {
                'allow_null': True,
            },
        }
