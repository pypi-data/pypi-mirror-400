from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, viewsets

from huscy.medical_notes import serializers, services
from huscy.subjects.models import Subject


class DjangoModelPermissions(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class MedicalNoteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = serializers.MedicalNoteSerializer
    permission_classes = DjangoModelPermissions,

    def initial(self, request, *args, **kwargs):
        self.subject = get_object_or_404(Subject, pk=self.kwargs['subject_pk'])
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return services.get_medical_notes(self.subject)

    def perform_create(self, serializer):
        serializer.save(subject=self.subject)

    def perform_destroy(self, medical_note):
        services.delete_medical_note(medical_note)
