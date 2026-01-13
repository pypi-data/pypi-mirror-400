from rest_framework import serializers


from django_to_galaxy.models.galaxy_instance import GalaxyInstance


class GalaxyInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalaxyInstance
        fields = ["id", "url", "name"]
