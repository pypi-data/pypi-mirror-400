import requests

from django.db import models


class GalaxyInstance(models.Model):
    """Table for Galaxy instances."""

    url = models.URLField(max_length=100)
    """url of the Galaxy instance."""
    name = models.CharField(max_length=100, unique=True)
    """Name of the Galaxy Instance."""

    def __str__(self):
        return f"{self.name} [{self.url}]"

    def is_online(self) -> bool:
        """
        Check the status of the instance.

        Returns:
            Whether the instance is available or not.
        """
        try:
            response = requests.head(self.url, timeout=30)
            response.raise_for_status()
            return True
        except Exception:
            return False
