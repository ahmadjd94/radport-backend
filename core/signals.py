from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StudyReport


@receiver(post_save, sender=StudyReport)
def study_report_on_submit(sender, instance, created, **kwargs):