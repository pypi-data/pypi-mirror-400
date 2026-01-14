from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from huscy.subjects.models import Subject


class MedicalNote(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name=_('Subject'))

    note = models.TextField(_('Note'))

    created_at = models.DateTimeField(_('Created at'), auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                   verbose_name=_('Created by'))

    class Meta:
        ordering = 'created_at',
        verbose_name = _('Medical note')
        verbose_name_plural = _('Medical notes')
