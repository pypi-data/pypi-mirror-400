from rest_framework import viewsets

from django_to_galaxy.models.galaxy_instance import GalaxyInstance
from django_to_galaxy.api.serializers.galaxy_instance import GalaxyInstanceSerializer


class GalaxyInstanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows different galaxy instances to be viewed and edited.
    """

    queryset = GalaxyInstance.objects.all()
    serializer_class = GalaxyInstanceSerializer
