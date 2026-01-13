from rest_framework import serializers


class HistoryCreatedSerializer(serializers.Serializer):
    message = serializers.CharField()
    history_id = serializers.IntegerField()
