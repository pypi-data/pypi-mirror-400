from rest_framework import viewsets

from django_to_galaxy.models.galaxy_user import GalaxyUser
from django_to_galaxy.api.serializers.galaxy_user import GalaxyUserSerializer


class GalaxyUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows galaxy users to be viewed and edited.
    """

    queryset = GalaxyUser.objects.select_related("galaxy_instance")
    serializer_class = GalaxyUserSerializer
