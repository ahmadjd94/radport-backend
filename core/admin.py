# admin.py

from django.contrib import admin
from .models import Flow, StudyReport


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ("flow_type", "label", "version", "is_active", "updated_at")
    list_filter = ("flow_type", "is_active")
    readonly_fields = ("id", "created_at", "updated_at")
    search_fields = ("flow_type", "label")


@admin.register(StudyReport)
class StudyReportAdmin(admin.ModelAdmin):
    data = [
        "id",
        "flow",
        "study_uid",
        "report_data",
        "submitted_at",
        "created_at",
        "updated_at",
        "created_by",
        "submitted_by",
    ]
    list_display = (
        # "flow",
        "study_uid",
        "report_data",
        "created_by",
    )
    # list_filter = ("flow_type", "is_active")
    # readonly_fields = ("id", "created_at", "updated_at")
    # search_fields = ("flow_type", "label")
