from typing import List

from django.contrib.auth import get_user_model

from huscy.medical_notes.models import MedicalNote
from huscy.subjects.models import Subject


User = get_user_model()


def create_medical_note(subject: Subject, note: str, created_by: User) -> MedicalNote:
    return MedicalNote.objects.create(
        note=note,
        subject=subject,
        created_by=created_by,
    )


def get_medical_notes(subject: Subject) -> List[MedicalNote]:
    return MedicalNote.objects.filter(subject=subject)


def delete_medical_note(medical_note: MedicalNote) -> None:
    medical_note.delete()
