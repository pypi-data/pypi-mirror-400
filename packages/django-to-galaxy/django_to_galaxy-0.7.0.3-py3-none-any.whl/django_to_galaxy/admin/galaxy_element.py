from django.contrib import admin


class GalaxyElementAdmin(admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs) -> bool:
        return False
