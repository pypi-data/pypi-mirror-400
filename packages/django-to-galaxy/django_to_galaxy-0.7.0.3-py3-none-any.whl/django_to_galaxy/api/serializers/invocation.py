from rest_framework import serializers

from django_to_galaxy.models.invocation import Invocation


class InvocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invocation
        fields = [
            "id",
            "galaxy_id",
            "galaxy_state",
            "status",
            "workflow",
            "history",
            "create_time",
        ]


class UpdateOutputFilesResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    galaxy_output_file_ids = serializers.ListField(child=serializers.IntegerField())
