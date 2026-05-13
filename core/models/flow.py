# models.py

import uuid
from django.db import models


class Flow(models.Model):

    class FlowType(models.TextChoices):
        CXR  = "CXR",  "Chest X-Ray"
        # Future types — add here as flows are built out:
        # CCTA = "CCTA", "Coronary CT Angiography"
        # CT_ABDOMEN = "CT_ABDOMEN", "CT Abdomen & Pelvis"
        # MRI_BRAIN  = "MRI_BRAIN",  "MRI Brain"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    flow_type = models.CharField(
        max_length=32,
        choices=FlowType.choices,
        unique=False,
        help_text="Modality/exam type this flow applies to. One active flow definition per type.",
    )
    version = models.PositiveIntegerField(
        default=1,
        help_text="Increment when the structure changes. Frontend can cache by flow_type + version.",
    )
    label = models.CharField(
        max_length=128,
        help_text="Human-readable display name, e.g. 'Chest X-Ray Systematic Review'.",
    )
    structure = models.JSONField(
        help_text=(
            "Full checklist structure as JSON. "
            "Top-level keys are section IDs (A, B, C, D, E, 2H, HG). "
            "Each section contains: section_id, section_label, groups[] → group_name, items[] → item_id, item_text, options[]."
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active flows are served to the frontend. Deactivate rather than delete when retiring a version.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Flow"
        verbose_name_plural = "Flows"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_flow_type_display()} v{self.version}"