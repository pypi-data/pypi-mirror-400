import django.apps
from django.core.exceptions import ValidationError
from rest_framework import serializers


class FileSerializer(serializers.Serializer):
    model = serializers.CharField()
    path_field = serializers.CharField()
    file_type = serializers.CharField()
    id = serializers.IntegerField()

    def validate(self, attrs):
        old_attrs = attrs.copy()
        for key, value in old_attrs.items():
            if key == "model":
                all_models = django.apps.apps.get_models()
                all_models_dict = {m.__name__.lower(): m for m in all_models}
                if value not in all_models_dict.keys():
                    raise ValidationError(f"model <{value}> does not exist on the app.")
        return attrs


class UploadHistorySerializer(serializers.Serializer):
    history_id = serializers.IntegerField()
    file = FileSerializer()
