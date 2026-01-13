from rest_framework import serializers

from .upload_to_history import FileSerializer


class DataEntryDatamapSerializer(serializers.Serializer):
    """
    Serializer for individual data entries in the datamap for Galaxy workflow invocation.
    """

    SRC_CHOICES = ("hda", "hdca", "lda")

    id = serializers.CharField(allow_blank=True)
    src = serializers.ChoiceField(choices=SRC_CHOICES)


class DatamapField(serializers.DictField):
    """
    Custom field to handle datamap for Galaxy workflow invocation serialization/deserialization.
    The datamap is as follows:
    {
        "0": {"id": "dataset_id_1", "src": "hda"},
        "1": "text_value"
    }
    Each key can have either a dict value with 'id' and 'src' or a simple string value.
    src can be one of 'hda', 'hdca' or 'lda'.
    """

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Datamap must be a dictionary.")

        if not data:
            raise serializers.ValidationError("Datamap must not be empty.")

        result = {}
        has_data_entry = False

        for key, value in data.items():
            # If value is a dict {id, src}
            if isinstance(value, dict):
                serializer = DataEntryDatamapSerializer(data=value)
                serializer.is_valid(raise_exception=True)
                result[key] = serializer.validated_data
                has_data_entry = True

            else:
                result[key] = value

        if not has_data_entry:
            raise serializers.ValidationError(
                "Datamap must contain at least one data entry with (id, src)."
            )

        return result

    def to_representation(self, value):
        return value


"""
class DatamapSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, default="")
    src = serializers.CharField()
"""


class InvokeWorkflowSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    history_id = serializers.IntegerField()
    datamap = DatamapField()


class ExecuteWorkflowSerializer(serializers.Serializer):
    workflow_id = serializers.IntegerField()
    galaxy_user_id = serializers.IntegerField()
    fake_datamap = serializers.DictField(child=FileSerializer())


class GenericDictSerializer(serializers.Serializer):
    data = serializers.DictField()
