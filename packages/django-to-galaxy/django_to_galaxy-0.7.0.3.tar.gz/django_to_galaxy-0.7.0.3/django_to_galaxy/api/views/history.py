from rest_framework import viewsets

from django_to_galaxy.models.history import History
from django_to_galaxy.api.serializers.history import HistorySerializer


class HistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows histories to be viewed.
    """

    queryset = History.objects.all()
    lookup_field = "galaxy_id"
    serializer_class = HistorySerializer
