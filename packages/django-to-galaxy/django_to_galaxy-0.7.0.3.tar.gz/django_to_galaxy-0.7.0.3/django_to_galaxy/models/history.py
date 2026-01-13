from typing import List

from bioblend.galaxy.objects import wrappers
from django.db import models

from django_to_galaxy.schemas.dataset import SimpleDataset
from .galaxy_element import GalaxyElement


class History(GalaxyElement):
    """Table for Galaxy history."""

    galaxy_state = models.CharField(max_length=100)
    """State on the galaxy side."""
    galaxy_owner = models.ForeignKey(
        "GalaxyUser", null=False, on_delete=models.CASCADE, related_name="histories"
    )
    """Galaxy user that owns the workflow."""
    create_time = models.DateTimeField()
    """Time the invocation was created."""

    @property
    def galaxy_history(self) -> wrappers.History:
        """Galaxy object using bioblend."""
        if getattr(self, "_galaxy_history", None) is None:
            self._galaxy_history = self._get_galaxy_history()
        return self._galaxy_history

    def _get_galaxy_history(self) -> wrappers.History:
        """Get galaxy object using bioblend."""
        return self.galaxy_owner.obj_gi.histories.get(self.galaxy_id)

    @property
    def simplify_datasets(self) -> List[SimpleDataset]:
        """Simplified version of datasets from history."""
        if getattr(self, "_simplify_datasets", None) is None:
            self._simplify_datasets = self._get_simplified_datasets()
        return self._simplify_datasets

    def _get_simplified_datasets(self) -> List[SimpleDataset]:
        """Get simplified version of datasets from history."""
        return [
            SimpleDataset(**dataset.wrapped)
            for dataset in self.galaxy_history.get_datasets()
        ]

    def delete(self, **kwargs):
        """Overloaded method to also delete history on Galaxy side."""
        self.galaxy_owner.obj_gi.histories.delete(id_=self.galaxy_id, purge=True)
        return super().delete(**kwargs)

    def synchronize(self):
        """Synchronize data from Galaxy instance."""
        galaxy_history = self._get_galaxy_history()
        self.name = galaxy_history.name
        self.published = galaxy_history.published
        self.galaxy_state = galaxy_history.state
        if self.galaxy_history.annotation is not None:
            self.annotation = galaxy_history.annotation
        self.save()

    def upload_file(
        self, file_path: str, **kwargs
    ) -> wrappers.HistoryDatasetAssociation:
        """Upload file to history."""
        return self.galaxy_history.upload_file(file_path, **kwargs)

    def check_dataset(self, dataset_id: str):
        """Return dataset object or raise ConnectionError if not found."""
        return self.galaxy_owner.obj_gi.gi.datasets.show_dataset(dataset_id)

    def create_list_collection(self, name: str, elements_names, elements_ids):
        """
        Create a list collection in the history.
        Args:
            name (str): Name of the collection.
            elements_names (list): List of names for each element in the collection.
            elements_ids (list): List of dataset IDs for each element in the collection.
        Returns:
            tuple: (association, errors)
        """

        errors = []
        element_identifiers = []

        for i, (element_name, element_id) in enumerate(
            zip(elements_names, elements_ids)
        ):
            try:
                self.check_dataset(element_id)
                element_identifiers.append(
                    {"name": element_name, "src": "hda", "id": element_id}
                )
            except ConnectionError as e:
                errors.append(
                    {
                        "index": i,
                        "type": "elements_ids",
                        "id": element_id,
                        "error": str(e),
                    }
                )
            if errors:
                return None, errors

            collection_datamap = {
                "name": name,
                "collection_type": "list",
                "element_identifiers": element_identifiers,
            }

        try:
            association = self.galaxy_history.create_dataset_collection(
                collection_description=collection_datamap
            )
            return association, None
        except Exception as e:
            return None, [{"type": "create_dataset_collection", "error": str(e)}]

    def create_list_paired_collection(self, name, pairs_names, first_ids, second_ids):
        """
        Create a list:paired collection in the history.
        Args:
            name (str): Name of the collection.
            pairs_names (list): List of names for each pair in the collection.
            first_ids (list): List of dataset IDs for the first element in each pair.
            second_ids (list): List of dataset IDs for the second element in each pair.
        Returns:
            tuple: (association, errors)
        """

        errors = []
        element_identifiers = []

        for i, pair_name in enumerate(pairs_names):
            try:
                self.check_dataset(first_ids[i])
                self.check_dataset(second_ids[i])
            except ConnectionError as e:
                errors.append(
                    {
                        "index": i,
                        "pair_name": pair_name,
                        "first_id": first_ids[i],
                        "second_id": second_ids[i],
                        "error": str(e),
                    }
                )
                continue

            element_identifiers.append(
                {
                    "name": pair_name,
                    "src": "new_collection",
                    "collection_type": "paired",
                    "element_identifiers": [
                        {"name": "forward", "src": "hda", "id": first_ids[i]},
                        {"name": "reverse", "src": "hda", "id": second_ids[i]},
                    ],
                }
            )

        if errors:
            return None, errors

        description = {
            "name": name,
            "collection_type": "list:paired",
            "element_identifiers": element_identifiers,
        }

        try:
            association = self.galaxy_history.create_dataset_collection(
                collection_description=description
            )
            return association, None
        except ConnectionError as e:
            return None, [{"type": "create_dataset_collection", "error": str(e)}]

    def create_paired_collection(self, name, first_id, second_id):
        """
        Create a paired collection in the history.
        Args:
            name (str): Name of the collection.
            first_id (str): Dataset ID for the first element.
            second_id (str): Dataset ID for the second element.
        Returns:
            tuple: (association, errors)
        """

        errors = []

        try:
            self.check_dataset(first_id)
        except ConnectionError as e:
            errors.append({"field": "first_element_id", "error": str(e)})

        try:
            self.check_dataset(second_id)
        except ConnectionError as e:
            errors.append({"field": "second_element_id", "error": str(e)})

        if errors:
            return None, errors

        description = {
            "name": name,
            "collection_type": "paired",
            "element_identifiers": [
                {"name": "forward", "src": "hda", "id": first_id},
                {"name": "reverse", "src": "hda", "id": second_id},
            ],
        }

        try:
            association = self.galaxy_history.create_dataset_collection(
                collection_description=description
            )
            return association, None
        except ConnectionError as e:
            return None, [{"error": str(e)}]

    def __repr__(self):
        return f"History: {super().__str__()}"

    class Meta:
        verbose_name_plural = "Histories"
        unique_together = ("galaxy_id", "galaxy_owner")
