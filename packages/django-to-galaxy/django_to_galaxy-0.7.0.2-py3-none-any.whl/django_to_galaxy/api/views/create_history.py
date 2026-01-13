from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView

from django_to_galaxy.models import GalaxyUser
from django_to_galaxy.api.serializers.create_history import HistoryCreatedSerializer


class CreateHistoryView(RetrieveAPIView):
    queryset = GalaxyUser.objects.all()
    serializer_class = None

    @swagger_auto_schema(
        operation_description="Create history from a user.",
        operation_summary="Create history from a user.",
        tags=["galaxy_users"],
        responses={200: HistoryCreatedSerializer},
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        history = instance.create_history()
        message = f"{str(history)} for {str(instance)} has been successfully created."
        return Response(data={"message": message, "history_id": history.id})
