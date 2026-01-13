from abc import abstractmethod

from django.db import models


class Tag(models.Model):
    label = models.CharField(null=False, max_length=200, unique=True)

    def __str__(self):
        return f"{self.label}"

    def __repr__(self):
        return f"Tag: {self!s}"


class GalaxyElement(models.Model):
    """Base class for all Galaxy elements with galaxy id that are likely to evolve or change."""

    galaxy_id = models.CharField(null=False, max_length=50)
    """Invocation id used on the galaxy side."""
    name = models.CharField(null=False, max_length=200)
    """Name used on the galaxy side."""
    annotation = models.CharField(max_length=200)
    """Annotation on the galaxy side."""
    tags = models.ManyToManyField("Tag", blank=True)
    """tags on the galaxy side."""
    published = models.BooleanField(null=False)
    """Whether it is published or not on the galaxy side."""
    galaxy_owner = models.ForeignKey("GalaxyUser", null=False, on_delete=models.CASCADE)
    """Galaxy user that owns this element."""

    @abstractmethod
    def synchronize(self):
        """
        @TODO
        method to synchronize entry in django from galaxy based on galaxy_id.
        """
        raise NotImplementedError

    @abstractmethod
    def is_valid(self):
        """
        @TODO
        method to check if galaxy_id is still pointing to a valid element.
        """
        raise NotImplementedError

    def __str__(self):
        return f"{self.name} ({self.galaxy_id})"

    class Meta:
        abstract = True
