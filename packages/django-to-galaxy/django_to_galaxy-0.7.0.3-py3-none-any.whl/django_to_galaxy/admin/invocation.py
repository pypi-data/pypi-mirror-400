from typing import List

from django.contrib import admin, messages
from django.utils.translation import ngettext
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse

from django_to_galaxy.models.invocation import Invocation

from .galaxy_element import GalaxyElementAdmin


@admin.register(Invocation)
class InvocationAdmin(GalaxyElementAdmin):
    list_display = (
        "id",
        "galaxy_id",
        "display_percentage_done",
        "status",
        "workflow",
        "history",
        "create_time",
        "get_number_output_files",
    )
    readonly_fields = (
        "id",
        "galaxy_id",
        "display_percentage_done",
        "status",
        "workflow",
        "history",
        "create_time",
    )
    actions = ["synchronize_invocation", "update_output_files"]

    @admin.display(description="Percentage Done")
    def display_percentage_done(self, obj):
        return format_html(
            """
            <progress value="{0}" max="100"></progress>
            <span style="font-weight:bold">{0}%</span>
            """,
            obj.percentage_done,
        )

    def _get_message_invocation(
        self,
        request,
        invocations: List[Invocation],
        message_singular: str,
        message_plural: str,
        message_type: int,
    ):
        count = len(invocations)
        details = ", ".join([f"{i}" for i in invocations])
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

    def _get_message_output_files(
        self,
        request,
        invocations: List[Invocation],
        message_singular: str,
        message_plural: str,
        message_type: int,
    ):
        count = 0
        for inv in invocations:
            count += inv.output_files.count()
        details = ", ".join([f"{i}" for i in invocations])
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
    def synchronize_invocation(self, request, queryset):
        sync_invocations = []
        error_invocations = []
        for invocation in queryset:
            try:
                invocation.synchronize()
                sync_invocations.append(invocation)
            except:  # noqa
                error_invocations.append(invocation)
        if sync_invocations:
            self._get_message_invocation(
                request,
                sync_invocations,
                "invocation was successfully synchronized",
                "invocations were successfully synchronized",
                messages.SUCCESS,
            )
        if error_invocations:
            self._get_message_invocation(
                request,
                error_invocations,
                "invocation could not be synchronized",
                "invocations could not be synchronized",
                messages.ERROR,
            )

    @admin.action(description="Update Output files")
    def update_output_files(self, request, queryset):
        updated_invocations = []
        error_invocations = []
        for invocation in queryset:
            try:
                invocation.update_output_files()
                updated_invocations.append(invocation)
            except:  # noqa
                error_invocations.append(invocation)
        if updated_invocations:
            self._get_message_output_files(
                request,
                updated_invocations,
                "output file from invocation(s) were successfully updated",
                "output files from invocation(s) were successfully updated",
                messages.SUCCESS,
            )
        if error_invocations:
            self._get_message_output_files(
                request,
                error_invocations,
                "output file from invocation(s) could not be updated",
                "output files from invocation(s) could not be updated",
                messages.ERROR,
            )

    def get_number_output_files(self, obj):
        count = obj.output_files.count()
        url = (
            reverse("admin:django_to_galaxy_galaxyoutputfile_changelist")
            + "?"
            + urlencode({"invocation__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, count)

    get_number_output_files.short_description = "Output files"
