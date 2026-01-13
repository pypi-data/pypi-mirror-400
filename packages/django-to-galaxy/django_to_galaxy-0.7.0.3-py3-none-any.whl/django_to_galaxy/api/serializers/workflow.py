from rest_framework import serializers

from django_to_galaxy.models.workflow import Workflow


class WorkflowSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    workflowinputs = serializers.SerializerMethodField()

    class Meta:
        model = Workflow
        fields = [
            "id",
            "galaxy_id",
            "name",
            "annotation",
            "tags",
            "published",
            "galaxy_owner",
            "workflowinputs",
        ]
        read_only_fields = ["tags", "workflowinputs"]

    def get_tags(self, obj):
        return [tag.label for tag in obj.tags.all()]

    def get_workflowinputs(self, obj):
        return [
            {
                "galaxy_step_id": input.galaxy_step_id,
                "label": input.label,
                "input_type": input.input_type,
                "formats": [format.format for format in input.formats.all()],
                "parameter_type": input.parameter_type,
                "collection_type": input.collection_type,
                "optional": input.optional,
                "default_value": input.default_value_casted,
                "multiple": input.multiple,
            }
            for input in obj.workflowinput_set.all()
        ]
