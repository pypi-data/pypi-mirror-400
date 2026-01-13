from datetime import datetime
from typing import List

from bioblend.galaxy.objects import GalaxyInstance as BioblendGalaxyInstance
from django.db import models

from django_to_galaxy.apps import DjangoToGalaxyConfig
from django_to_galaxy.utils import load_galaxy_history_time_to_datetime
from .history import History
from .workflow import Workflow


class GalaxyUser(models.Model):
    """Table for Galaxy users."""

    email = models.EmailField(null=False)
    """Email used for the Galaxy account."""
    api_key = models.CharField(null=False, max_length=50)
    """API key of the user."""
    galaxy_instance = models.ForeignKey(
        "GalaxyInstance", null=False, on_delete=models.CASCADE, related_name="users"
    )
    """Galaxy instance the user comes from."""

    @property
    def obj_gi(self):
        """Bioblend object to interact with Galaxy instance."""
        if getattr(self, "_obj_gi", None) is None:
            self._obj_gi = self.get_bioblend_obj_gi()
        return self._obj_gi

    @obj_gi.setter
    def obj_gi(self, val):
        self._obj_gi = val

    def get_bioblend_obj_gi(self):
        """Retrieve bioblend object to interact with Galaxy instance."""
        return BioblendGalaxyInstance(self.galaxy_instance.url, self.api_key)

    @property
    def available_workflows(self) -> List[Workflow]:
        """Available workflows for the user."""
        if getattr(self, "_available_workflows", None) is None:
            self._available_workflows = self.get_available_workflows()
        return self._available_workflows

    def get_available_workflows(self) -> List[Workflow]:
        """List all available workflows for the user."""
        bioblend_wfs = self.obj_gi.workflows.list()
        wfs_tag = []
        for wf in bioblend_wfs:
            wfs_tag.append(
                (
                    Workflow(
                        galaxy_owner=self,
                        galaxy_id=wf.id,
                        name=wf.name,
                        published=wf.published,
                        annotation=wf.wrapped["annotation"],
                    ),
                    wf.wrapped["tags"],
                )
            )
        return wfs_tag

    def _generate_history_name(self) -> str:
        """
        Generate history name using current date.

        Returns:
            Generated history name.
        """
        current_time = datetime.now()
        str_date = current_time.strftime("%Y%m%d-%f")
        suffix = f"created_by_{DjangoToGalaxyConfig.name}"
        return f"{str_date}_{suffix}"

    def create_history(self, name=None):
        """Create history on the Galaxy instance."""
        name = self._generate_history_name() if name is None else name
        galaxy_history = self.obj_gi.histories.create(name=name)
        local_history = History(
            galaxy_id=galaxy_history.id,
            name=galaxy_history.name,
            published=galaxy_history.published,
            galaxy_state=galaxy_history.state,
            create_time=load_galaxy_history_time_to_datetime(galaxy_history),
            galaxy_owner=self,
        )
        local_history.save()
        return local_history

    def __str__(self):
        return f"{self.email} at {self.galaxy_instance}"
