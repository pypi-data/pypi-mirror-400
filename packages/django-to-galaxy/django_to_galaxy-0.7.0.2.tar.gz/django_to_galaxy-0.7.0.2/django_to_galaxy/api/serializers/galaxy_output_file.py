from rest_framework import serializers

from django_to_galaxy.models.galaxy_output_file import GalaxyOutputFile


class GalaxyOutputFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalaxyOutputFile
        fields = [
            "id",
            "galaxy_id",
            "workflow_name",
            "galaxy_state",
            "history_name",
            "src",
            "invocation",
        ]
