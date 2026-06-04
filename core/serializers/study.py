# serializers.py
from django.utils import timezone
from rest_framework import serializers
from ..models import  StudyReport



class StudyReportSerializer(serializers.ModelSerializer):

    submitted_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault(),
    )
    flow_type = serializers.CharField(
        source="flow.flow_type",
        read_only=True,
    )
    flow_version = serializers.IntegerField(
        source="flow.version",
        read_only=True,
    )

    status = serializers.ChoiceField(StudyReport.Status, default=StudyReport.Status.DRAFT)

    class Meta:
        model = StudyReport
        fields = [
            "id",
            "flow",
            "flow_type",
            "flow_version",
            "study_uid",
            "status",
            "submitted_by",
            "created_by",
            "report_data",
            "report_document_md",
            "submitted_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "flow_type",
            "flow_version",
            "submitted_at",
            "created_at",
            "updated_at",
        ]

    def validate_report_data(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("report_data must be a JSON object.")
        # if "sections" not in value:
        #     raise serializers.ValidationError("report_data must contain a 'sections' key.")
        return value

    def validate(self, attrs):
        """
        On submission (status=submitted), enforce:
        1. All required items must have a status other than not_reviewed.
        2. Fetch the required item IDs from the linked flow structure.
        """
        status = attrs.get("status", self.instance.status if self.instance else None)

        if status == StudyReport.Status.SUBMITTED:
            flow = attrs.get("flow", self.instance.flow if self.instance else None)
            report_data = attrs.get("report_data", {})

            if flow:
                required_ids = self._get_required_item_ids(flow.structure)
                missing = self._find_incomplete_required(report_data, required_ids)
                if missing:
                    raise serializers.ValidationError({
                        "report_data": f"The following required items are not reviewed: {missing}"
                    })

        return attrs

    def _get_required_item_ids(self, structure):
        required = set()
        for section in structure.get("sections", {}).values():
            for group in section.get("groups", []):
                for item in group.get("items", []):
                    if item.get("required", False):
                        required.add(item["item_id"])
        return required

    def _find_incomplete_required(self, report_data, required_ids):
        missing = []
        for section in report_data.get("sections", {}).values():
            for item in section.get("items", []):
                iid = item.get("item_id")
                if iid in required_ids:
                    if item.get("status", "not_reviewed") == "not_reviewed":
                        missing.append(iid)
        return missing

    def update(self, instance, validated_data):
        # Stamp submitted_at when status transitions to submitted
        if (
            validated_data.get("status") == StudyReport.Status.SUBMITTED
            and instance.status != StudyReport.Status.SUBMITTED
        ):
            validated_data["submitted_at"] = timezone.now()
        return super().update(instance, validated_data)