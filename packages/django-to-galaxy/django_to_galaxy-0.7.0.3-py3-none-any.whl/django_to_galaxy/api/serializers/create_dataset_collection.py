from rest_framework import serializers
from django.core.exceptions import ValidationError

dataset_id_error_messages = {
    "min_length": "Dataset ID must be at least 16 characters long.",
}


class CollectionListSerializer(serializers.Serializer):
    history_id = serializers.IntegerField(
        required=True,
        help_text=(
            "Internal Django to galaxy ID of the Galaxy "
            "history where the collection will be created."
        ),
    )
    collection_name = serializers.CharField(
        required=True, help_text="Name of the dataset collection to be created."
    )
    elements_names = serializers.ListSerializer(
        child=serializers.CharField(required=True),
        help_text="List of names for each element in the collection.",
    )
    elements_ids = serializers.ListSerializer(
        child=serializers.CharField(
            required=True, min_length=16, error_messages=dataset_id_error_messages
        ),
        help_text="List of galaxy dataset IDs corresponding to each element in the collection.",
    )

    def validate(self, attrs):
        if len(attrs["elements_names"]) != len(attrs["elements_ids"]):
            raise ValidationError(
                {
                    "lists_lengths": (
                        "List of elements_names and list of "
                        "elements_ids must be of same length."
                    )
                }
            )
        return attrs


class CollectionListPairedSerializer(serializers.Serializer):
    history_id = serializers.IntegerField(
        required=True,
        help_text=(
            "Internal Django to galaxy ID of the Galaxy "
            "history where the collection will be created."
        ),
    )
    collection_name = serializers.CharField(
        required=True, help_text="Name of the dataset collection to be created."
    )
    pairs_names = serializers.ListSerializer(
        child=serializers.CharField(),
        help_text="List of names for each paired datasets in the collection.",
    )
    first_elements_ids = serializers.ListSerializer(
        child=serializers.CharField(
            required=True, min_length=16, error_messages=dataset_id_error_messages
        ),
        help_text=(
            "List of galaxy dataset IDs corresponding to "
            "the first element in each paired datasets."
        ),
    )
    second_elements_ids = serializers.ListSerializer(
        child=serializers.CharField(
            required=True, min_length=16, error_messages=dataset_id_error_messages
        ),
        help_text=(
            "List of galaxy dataset IDs corresponding to "
            "the second element in each paired datasets."
        ),
    )

    def validate(self, attrs):
        if (
            len(attrs["first_elements_ids"]) != len(attrs["second_elements_ids"])
            or len(attrs["first_elements_ids"]) != len(attrs["pairs_names"])
            or len(attrs["pairs_names"]) != len(attrs["second_elements_ids"])
        ):
            raise ValidationError(
                {
                    "lists_lengths": (
                        "List of pairs names and list "
                        "of elements ids must be of same length."
                    )
                }
            )

        return attrs


class CollectionPairedSerializer(serializers.Serializer):
    history_id = serializers.IntegerField(
        required=True,
        help_text=(
            "Internal Django to galaxy ID of the Galaxy history"
            " where the collection will be created."
        ),
    )
    collection_name = serializers.CharField(
        required=True, help_text="Name of the dataset collection to be created."
    )
    first_element_id = serializers.CharField(
        required=True,
        min_length=16,
        error_messages=dataset_id_error_messages,
        help_text="Galaxy dataset IDs corresponding to the first element of the paired dataset.",
    )
    second_element_id = serializers.CharField(
        required=True,
        min_length=16,
        error_messages=dataset_id_error_messages,
        help_text="Galaxy dataset IDs corresponding to the second element of the paired dataset.",
    )
