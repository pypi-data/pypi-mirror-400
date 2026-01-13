from bioblend.galaxy.objects import wrappers
from django.db import models


class GalaxyOutputFile(models.Model):
    """Handle output files."""

    galaxy_id = models.CharField(null=False, max_length=50)
    """Dataset id used on the galaxy side."""
    workflow_name = models.CharField(null=False, max_length=200)
    """Name used in the workflow on the galaxy side."""
    galaxy_state = models.CharField(max_length=100, null=True)
    """State on the galaxy side."""
    history_name = models.CharField(null=True, max_length=200)
    """Name used in the history on the galaxy side."""
    src = models.CharField(null=False, max_length=50)
    """Src type on the galaxy side."""
    invocation = models.ForeignKey(
        "Invocation", null=False, on_delete=models.CASCADE, related_name="output_files"
    )
    """Invocation that generated the output."""

    @property
    def galaxy_dataset(self) -> wrappers.Invocation:
        """Galaxy object using bioblend."""
        if getattr(self, "_galaxy_dataset", None) is None:
            self._galaxy_dataset = self._get_galaxy_dataset()
        return self._galaxy_dataset

    def _get_galaxy_dataset(self) -> wrappers.Invocation:
        """Get galaxy object using bioblend."""
        return self.invocation.history.galaxy_history.get_dataset(self.galaxy_id)

    def synchronize(self):
        """Synchronize state from Galaxy instance."""
        dataset = self._get_galaxy_dataset()
        self.galaxy_state = dataset.state
        self.history_name = dataset.name
        self.save()

    def __str__(self):
        return f"{self.history_name} (from {self.invocation.galaxy_id})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "galaxy_id",
                    "invocation",
                ),
                name="unique_galaxy_id_per_invocation",
            )
        ]
