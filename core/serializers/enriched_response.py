from rest_framework import serializers

from core.utils import merge_flow_with_report


class EnrichedChecklistSerializer(serializers.Serializer):
    """Merged checklist + answers structure."""

    study_uid = serializers.CharField()
    flow_id = serializers.UUIDField(source='flow.id')
    flow_type = serializers.CharField(source='flow.flow_type')
    flow_label = serializers.CharField(source='flow.label')
    flow_version = serializers.IntegerField(source='flow.version')

    structure = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()

    def get_structure(self, obj):
        return merge_flow_with_report(obj.flow, obj)

    def get_metadata(self, obj):
        return {
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'submitted_by': obj.submitted_by.username if obj.submitted_by else None,
        }