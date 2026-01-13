from rest_framework import serializers

from django_to_galaxy.models.history import History


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = [
            "id",
            "galaxy_id",
            "name",
            "annotation",
            "published",
            "galaxy_owner",
            "galaxy_state",
        ]
