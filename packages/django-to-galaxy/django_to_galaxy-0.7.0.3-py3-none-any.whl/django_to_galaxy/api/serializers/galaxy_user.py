from rest_framework import serializers

from django_to_galaxy.api.serializers.galaxy_instance import GalaxyInstanceSerializer
from django_to_galaxy.models.galaxy_user import GalaxyUser
from django_to_galaxy.models.galaxy_instance import GalaxyInstance

from .asymetricslugrelatedfield import AsymetricSlugRelatedField


class GalaxyUserSerializer(serializers.ModelSerializer):
    galaxy_instance = AsymetricSlugRelatedField.from_serializer(
        GalaxyInstanceSerializer,
        queryset=GalaxyInstance.objects.all(),
        slug_field="id",
        required=False,
    )

    class Meta:
        model = GalaxyUser
        fields = ["id", "email", "galaxy_instance"]
