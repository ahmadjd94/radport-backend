# serializers.py

from rest_framework import serializers

from core.models import Flow


class FlowSerializer(serializers.ModelSerializer):

    flow_type_display = serializers.CharField(
        source="get_flow_type_display",
        read_only=True,
    )

    class Meta:
        model = Flow
        fields = [
            "id",
            "flow_type",
            "flow_type_display",
            "version",
            "label",
            "structure",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_structure(self, value):
        """
        Enforce minimum structural integrity on the JSON before saving.
        Ensures sections is present and each section has the required keys.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("structure must be a JSON object.")

        sections = value.get("sections")
        if not sections or not isinstance(sections, dict):
            raise serializers.ValidationError(
                "structure must contain a 'sections' object."
            )

        required_section_keys = {"section_id", "section_label", "groups"}
        for section_id, section in sections.items():
            missing = required_section_keys - set(section.keys())
            if missing:
                raise serializers.ValidationError(
                    f"Section '{section_id}' is missing required keys: {missing}."
                )
            if not isinstance(section.get("groups"), list):
                raise serializers.ValidationError(
                    f"Section '{section_id}': 'groups' must be a list."
                )
            for group in section["groups"]:
                if "group_name" not in group or "items" not in group:
                    raise serializers.ValidationError(
                        f"Section '{section_id}': each group must have 'group_name' and 'items'."
                    )
                for item in group["items"]:
                    if "item_id" not in item or "item_text" not in item:
                        raise serializers.ValidationError(
                            f"Section '{section_id}', group '{group.get('group_name')}': "
                            f"each item must have 'item_id' and 'item_text'."
                        )
        return value

    def validate_flow_type(self, value):
        """
        On create: block duplicate flow_type.
        On update: block changing flow_type to one that already exists.
        """
        qs = Flow.objects.filter(flow_type=value, is_active=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"A Flow with type '{value}' already exists."
            )
        return value