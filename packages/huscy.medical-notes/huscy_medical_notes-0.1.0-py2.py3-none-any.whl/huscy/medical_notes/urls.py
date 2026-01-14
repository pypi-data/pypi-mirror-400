from django.urls import include, path

from . import viewsets
from huscy.subjects.urls import subject_router


subject_router.register('medical-notes', viewsets.MedicalNoteViewSet, basename='medicalnote')


urlpatterns = [
    path('api/', include(subject_router.urls)),
]
