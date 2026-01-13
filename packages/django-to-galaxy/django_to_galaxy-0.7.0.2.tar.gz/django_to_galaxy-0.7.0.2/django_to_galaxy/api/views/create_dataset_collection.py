from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response

from rest_framework.generics import GenericAPIView
from rest_framework.status import HTTP_404_NOT_FOUND

from django_to_galaxy.models import History
from django_to_galaxy.api.serializers.create_dataset_collection import (
    CollectionListSerializer,
    CollectionListPairedSerializer,
    CollectionPairedSerializer,
)

example_payload_list = {
    "200": openapi.Response(
        description="Dataset collection created successfully.",
        examples={
            "application/json": {
                "summary": "Example payload",
                "description": "An example of a payload to create a dataset collection.",
                "value": {
                    "history_id": 1,
                    "collection_name": "My Dataset Collection",
                    "elements_names": ["dataset1", "dataset2"],
                    "elements_ids": ["f4b5e6d8a9c0b1e2", "a1b2c3d4e5f60708"],
                },
            }
        },
    )
}

example_payload_list_paired = {
    "200": openapi.Response(
        description="Dataset collection created successfully.",
        examples={
            "application/json": {
                "summary": "Example payload",
                "description": "An example of a payload to create a paired dataset collection.",
                "value": {
                    "history_id": 1,
                    "collection_name": "My Paired Collection",
                    "pairs_names": ["pair1", "pair2"],
                    "first_elements_ids": ["id1", "id2"],
                    "second_elements_ids": ["id3", "id4"],
                },
            }
        },
    )
}

example_payload_paired = {
    "200": openapi.Response(
        description="Dataset collection created successfully.",
        examples={
            "application/json": {
                "summary": "Example payload",
                "description": "An example of a payload to create a paired dataset collection.",
                "value": {
                    "history_id": 1,
                    "collection_name": "My Paired Collection",
                    "first_element_id": "id1",
                    "second_element_id": "id2",
                },
            }
        },
    )
}


class CreateDatasetListCollectionView(GenericAPIView):
    """
    API endpoint to create a dataset collection (list) in a Galaxy history.

    - POST: Creates a dataset collection in a specified Galaxy history.
    - Serializer: CollectionListSerializer
    - Returns: JSON response with collection details or connection errors.
    """

    serializer_class = CollectionListSerializer

    @swagger_auto_schema(
        operation_description="Create a dataset collection with dataset of an Galaxy history.",
        operation_summary="Create a dataset collection with dataset of an Galaxy history.",
        tags=["collections"],
        responses=example_payload_list,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "history_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                "collection_name": openapi.Schema(
                    type=openapi.TYPE_STRING, example="My Dataset Collection"
                ),
                "elements_names": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["dataset1", "dataset2"],
                ),
                "elements_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["f4b5e6d8a9c0b1e2", "a1b2c3d4e5f60708"],
                ),
            },
            required=[
                "history_id",
                "collection_name",
                "elements_names",
                "elements_ids",
            ],
        ),
    )
    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

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

        history_association, errors = history.create_list_collection(
            name=data["collection_name"],
            elements_names=data["elements_names"],
            elements_ids=data["elements_ids"],
        )

        if errors:
            return Response({"connection_errors": errors}, status=HTTP_404_NOT_FOUND)

        message = (
            "Collection of list of dataset has "
            f"been created to Galaxy History <{str(history)}>"
        )
        return Response(
            {
                "message": message,
                "history_association_id": history_association.id,
                "history_id": history.id,
            }
        )


class CreateDatasetListPairedCollectionView(GenericAPIView):
    """
    API endpoint to create a paired dataset collection (list:paired) in a Galaxy history.

    - POST: Creates a paired dataset collection in a specified Galaxy history.
    - Serializer: CollectionListPairedSerializer
    - Returns: JSON response with collection details or connection errors.
    """

    serializer_class = CollectionListPairedSerializer

    @swagger_auto_schema(
        operation_description=(
            "Create a paired dataset collection " "(list:paired) in a Galaxy history."
        ),
        operation_summary="Create a paired dataset collection (list:paired) in a Galaxy history.",
        tags=["collections"],
        responses=example_payload_list_paired,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "history_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                "collection_name": openapi.Schema(
                    type=openapi.TYPE_STRING, example="My Paired Collection"
                ),
                "pairs_names": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["pair1", "pair2"],
                ),
                "first_elements_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["id1", "id2"],
                ),
                "second_elements_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    example=["id3", "id4"],
                ),
            },
            required=[
                "history_id",
                "collection_name",
                "pairs_names",
                "first_elements_ids",
                "second_elements_ids",
            ],
        ),
    )
    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

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

        history_association, errors = history.create_list_paired_collection(
            name=data["collection_name"],
            pairs_names=data["pairs_names"],
            first_ids=data["first_elements_ids"],
            second_ids=data["second_elements_ids"],
        )

        if errors:
            return Response({"connection_errors": errors}, status=HTTP_404_NOT_FOUND)

        message = (
            "Collection of paired dataset (list:paired) has been "
            f"created to Galaxy History <{str(history)}>"
        )
        return Response(
            {
                "message": message,
                "history_association_id": history_association.id,
                "history_id": history.id,
            }
        )


class CreateDatasetPairedCollectionView(GenericAPIView):
    """
    API endpoint to create a paired dataset collection in a Galaxy history.

    - POST: Creates a paired dataset collection in a specified Galaxy history.
    - Serializer: CollectionPairedSerializer
    - Returns: JSON response with collection details or connection errors.
    """

    serializer_class = CollectionPairedSerializer

    @swagger_auto_schema(
        operation_description="Create a paired dataset collection in a Galaxy history.",
        operation_summary="Create a paired dataset collection in a Galaxy history.",
        tags=["collections"],
        responses=example_payload_paired,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "history_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                "collection_name": openapi.Schema(
                    type=openapi.TYPE_STRING, example="My Paired Collection"
                ),
                "first_element_id": openapi.Schema(
                    type=openapi.TYPE_STRING, example="id1"
                ),
                "second_element_id": openapi.Schema(
                    type=openapi.TYPE_STRING, example="id2"
                ),
            },
            required=[
                "history_id",
                "collection_name",
                "first_element_id",
                "second_element_id",
            ],
        ),
    )
    def post(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

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

        history_association, errors = history.create_paired_collection(
            name=data["collection_name"],
            first_id=data["first_element_id"],
            second_id=data["second_element_id"],
        )
        if errors:
            return Response({"connection_errors": errors}, status=HTTP_404_NOT_FOUND)

        message = (
            "Collection of paired dataset has been "
            f"created to Galaxy History <{str(history)}>"
        )

        return Response(
            {
                "message": message,
                "history_association_id": history_association.id,
                "history_id": history.id,
            }
        )
