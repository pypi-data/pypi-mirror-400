from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView

from django_to_galaxy.models.invocation import Invocation
from django_to_galaxy.api.serializers.invocation import (
    InvocationSerializer,
    UpdateOutputFilesResponseSerializer,
)


class InvocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows histories to be viewed.
    """

    queryset = Invocation.objects.all()
    serializer_class = InvocationSerializer


class UpdateOutputFilesView(RetrieveAPIView):
    queryset = Invocation.objects.all()
    serializer_class = UpdateOutputFilesResponseSerializer

    @swagger_auto_schema(
        operation_description="Update output files from an invocation.",
        operation_summary="Update output files from an invocation.",
        tags=["invocations"],
        responses={200: UpdateOutputFilesResponseSerializer},
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.update_output_files()
        output_files = instance.output_files.all()
        message = (
            f"output file(s) ({len(output_files)}) for {str(instance)}"
            " have been successfully updated."
        )
        return Response(
            data={
                "message": message,
                "galaxy_output_file_ids": [f.id for f in output_files],
            }
        )
