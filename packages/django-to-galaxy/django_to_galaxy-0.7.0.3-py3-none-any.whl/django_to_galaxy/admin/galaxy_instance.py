from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from django_to_galaxy.models.galaxy_instance import GalaxyInstance


@admin.register(GalaxyInstance)
class GalaxyInstanceAdmin(admin.ModelAdmin):
    list_display = ("url", "name", "get_registered_users", "is_online")

    def get_registered_users(self, obj):
        count = obj.users.count()
        url = (
            reverse("admin:django_to_galaxy_galaxyuser_changelist")
            + "?"
            + urlencode({"galaxy_instance__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, count)

    def is_online(self, obj):
        return obj.is_online()

    get_registered_users.short_description = "Registered users"
    is_online.boolean = True
