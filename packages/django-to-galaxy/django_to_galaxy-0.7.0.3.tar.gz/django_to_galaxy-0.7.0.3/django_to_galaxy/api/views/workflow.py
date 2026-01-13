from rest_framework import viewsets

from django_to_galaxy.models.workflow import Workflow
from django_to_galaxy.api.serializers.workflow import WorkflowSerializer


class WorkflowViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows workflows to be viewed.
    """

    queryset = Workflow.objects.all()
    lookup_field = "galaxy_id"
    serializer_class = WorkflowSerializer
