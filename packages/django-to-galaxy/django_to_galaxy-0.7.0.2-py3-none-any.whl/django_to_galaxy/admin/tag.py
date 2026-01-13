from django.contrib import admin

from django_to_galaxy.models.galaxy_element import Tag

from .galaxy_element import GalaxyElementAdmin


@admin.register(Tag)
class TagAdmin(GalaxyElementAdmin):
    list_display = (
        "id",
        "label",
    )
    readonly_fields = (
        "id",
        "label",
    )
