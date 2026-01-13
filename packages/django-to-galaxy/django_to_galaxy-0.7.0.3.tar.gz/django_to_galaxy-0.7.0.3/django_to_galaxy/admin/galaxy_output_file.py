from typing import List

from django.contrib import admin, messages
from django.utils.translation import ngettext

from django_to_galaxy.models.galaxy_output_file import GalaxyOutputFile

from .galaxy_element import GalaxyElementAdmin


@admin.register(GalaxyOutputFile)
class GalaxyOutputFileAdmin(GalaxyElementAdmin):
    list_display = (
        "id",
        "galaxy_id",
        "workflow_name",
        "history_name",
        "galaxy_state",
        "src",
        "invocation",
    )
    readonly_fields = (
        "id",
        "galaxy_id",
        "workflow_name",
        "history_name",
        "galaxy_state",
        "src",
        "invocation",
    )
    actions = ["synchronize_file"]

    def _get_message_output_file_synchronize(
        self,
        request,
        output_files: List[GalaxyOutputFile],
        message_singular: str,
        message_plural: str,
        message_type: int,
    ):
        count = len(output_files)
        details = ", ".join([f"{i}" for i in output_files])
        self.message_user(
            request,
            ngettext(
                f"%d {message_singular} [{details}].",
                f"%d {message_plural} [{details}].",
                count,
            )
            % count,
            message_type,
        )

    @admin.action(description="Synchronize data from Galaxy")
    def synchronize_file(self, request, queryset):
        sync_output_files = []
        error_output_files = []
        for output_file in queryset:
            try:
                output_file.synchronize()
                sync_output_files.append(output_file)
            except:  # noqa
                error_output_files.append(output_file)
        if sync_output_files:
            self._get_message_output_file_synchronize(
                request,
                sync_output_files,
                "output_file was successfully synchronized",
                "output_files were successfully synchronized",
                messages.SUCCESS,
            )
        if error_output_files:
            self._get_message_output_file_synchronize(
                request,
                error_output_files,
                "output_file could not be synchronized",
                "output_files could not be synchronized",
                messages.ERROR,
            )
