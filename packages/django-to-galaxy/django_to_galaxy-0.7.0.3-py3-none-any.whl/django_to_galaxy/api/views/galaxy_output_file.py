from rest_framework import viewsets

from django_to_galaxy.models.galaxy_output_file import GalaxyOutputFile
from django_to_galaxy.api.serializers.galaxy_output_file import (
    GalaxyOutputFileSerializer,
)


class GalaxyOutputFileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows histories to be viewed.
    """

    queryset = GalaxyOutputFile.objects.all()
    serializer_class = GalaxyOutputFileSerializer
