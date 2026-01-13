import django.apps
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.db.models.fields.files import FieldFile

from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_404_NOT_FOUND

from django_to_galaxy.models import History
from django_to_galaxy.api.serializers.upload_to_history import UploadHistorySerializer


class UploadToHistoryView(GenericAPIView):
    serializer_class = UploadHistorySerializer

    @swagger_auto_schema(
        operation_description="Upload file from django file system to a Galaxy history.",
        operation_summary="Upload file from a model with filepath to history.",
        tags=["histories"],
    )
    def post(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        # Retrieve history
        try:
            history = History.objects.get(id=data["history_id"])
        except ObjectDoesNotExist:
            return Response(
                {
                    "message": (
                        "Galaxy history with id ",
                        f"<{data['history_id']}> not found!",
                    )
                },
                status=HTTP_404_NOT_FOUND,
            )
        # Retrieve file & file path
        all_models = django.apps.apps.get_models()
        all_models_dict = {m.__name__.lower(): m for m in all_models}
        try:
            file = all_models_dict[data["file"]["model"]].objects.get(
                id=data["file"]["id"]
            )
        except ObjectDoesNotExist:
            return Response(
                {"message": f"File with id <{data['file']['id']}> not found!"},
                status=HTTP_404_NOT_FOUND,
            )
        try:
            file_path = getattr(file, data["file"]["path_field"])
        except AttributeError:
            return Response(
                {"message": f"File with id <{data['file']['id']}> not found!"},
                status=HTTP_404_NOT_FOUND,
            )
        if isinstance(file_path, FieldFile):
            file_path = file_path.path
        try:
            file_type = data["file"]["file_type"]
        except AttributeError:
            return Response(
                {"message": f"File with id <{data['file']['id']}> not found!"},
                status=HTTP_404_NOT_FOUND,
            )
        history_association = history.upload_file(file_path, file_type=file_type)
        message = (
            f"File <{str(file)}> has been uploaded to Galaxy History <{str(history)}>"
        )
        return Response(
            {
                "message": message,
                "file_galaxy_id": history_association.id,
                "history_id": history.id,
            }
        )
