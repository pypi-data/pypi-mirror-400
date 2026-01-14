from rest_framework import serializers

from huscy.medical_notes.models import MedicalNote
from huscy.users.serializer import UserSerializer


class MedicalNoteSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MedicalNote
        fields = (
            'id',
            'created_at',
            'created_by',
            'note',
            'subject',
        )
        read_only_fields = 'subject',

    def to_representation(self, medical_note):
        representation = super().to_representation(medical_note)
        representation['created_by'] = UserSerializer(medical_note.created_by).data
        return representation
