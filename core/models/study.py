# models.py

import uuid
from django.db import models
from django.contrib.auth import get_user_model

from core.models import Flow

User = get_user_model()



class StudyReport(models.Model):

    # class Status(models.TextChoices):
    #     DRAFT     = "draft",     "Draft"
    #     SUBMITTED = "submitted", "Submitted"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    flow = models.ForeignKey(
        Flow,
        on_delete=models.PROTECT,
        related_name="reports",
        help_text="The flow definition this report was completed against.",
    )
    study_uid = models.CharField(
        max_length=255,
        db_index=True,
        help_text="DICOM Study Instance UID — links this report to the study in Orthanc.",
    )

    # status = models.CharField(
    #     max_length=16,
    #     choices=Status.choices,
    #     default=Status.DRAFT,
    # )
    # projection = models.CharField(
    #     max_length=16,
    #     choices=[
    #         ("PA",          "PA"),
    #         ("AP",          "AP"),
    #         ("Lateral",     "Lateral"),
    #         ("PA+Lateral",  "PA + Lateral"),
    #     ],
    #     null=True,
    #     blank=True,
    #     help_text="Film projection — affects validity of CTI and mediastinal width measurements.",
    # )
    # patient_position = models.CharField(
    #     max_length=16,
    #     choices=[
    #         ("Erect",      "Erect"),
    #         ("Supine",     "Supine"),
    #         ("Semi-erect", "Semi-erect"),
    #         ("Unknown",    "Unknown"),
    #     ],
    #     null=True,
    #     blank=True,
    # )
    # film_quality = models.CharField(
    #     max_length=64,
    #     choices=[
    #         ("Adequate",                   "Adequate"),
    #         ("Suboptimal — rotation",      "Suboptimal — rotation"),
    #         ("Suboptimal — inspiration",   "Suboptimal — inspiration"),
    #         ("Suboptimal — exposure",      "Suboptimal — exposure"),
    #         ("Non-diagnostic",             "Non-diagnostic"),
    #     ],
    #     null=True,
    #     blank=True,
    # )
    # The full completed checklist — mirrors the flow structure
    # with status, selected_options, free_text, and section_note per item
    report_data = models.JSONField(
        help_text=(
            "Completed checklist payload. Structure mirrors the flow's sections. "
            "Each item contains: item_id, status (normal|finding|not_reviewed), "
            "selected_options[], free_text. Each section may contain a section_note."
        ),
        default={},
        null=True
    )
    # summary_impression = models.TextField(
    #     blank=True,
    #     default="",
    #     help_text="Free-text overall impression entered at end of wizard.",
    # )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of final submission. Null while status=draft.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_reports",
        help_text="User who created this report (tracks drafts too)."
    )

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_reports",
        help_text="User who submitted this report (null while drafting)."
    )

    class Meta:
        verbose_name = "Flow Report"
        verbose_name_plural = "Flow Reports"
        ordering = ["-created_at"]
        # One submitted report per study per flow —
        # drafts are allowed to accumulate until submission
        constraints = [
            models.UniqueConstraint(
                fields=["study_uid", "flow","created_by"],
                name="unique_submitted_report_per_study_flow",
            )
        ]

    # def __str__(self):
    #     return f"{self.flow.flow_type} report — {self.study_uid} ({self.status})"