from typing import List

from django.contrib import admin, messages
from django.utils.translation import ngettext

from django_to_galaxy.models.history import History

from .galaxy_element import GalaxyElementAdmin


@admin.register(History)
class HistoryAdmin(GalaxyElementAdmin):
    list_display = (
        "id",
        "name",
        "annotation",
        "galaxy_id",
        "published",
        "galaxy_owner",
        "tags",
        "galaxy_state",
        "create_time",
    )
    readonly_fields = (
        "id",
        "name",
        "annotation",
        "galaxy_id",
        "published",
        "galaxy_owner",
        "tags",
        "galaxy_state",
        "create_time",
    )
    actions = ["synchronize_history"]

    def tags(self, obj):
        return ", ".join([p.label for p in obj.tags.all()])

    def delete_queryset(self, request, queryset):
        """Might be slow when dealing with lot of items."""
        for item in queryset:
            item.delete()

    def _get_message_history_synchronize(
        self,
        request,
        histories: List[History],
        message_singular: str,
        message_plural: str,
        message_type: int,
    ):
        count = len(histories)
        details = ", ".join([f"{h.galaxy_id} from {h.galaxy_owner}" for h in histories])
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
    def synchronize_history(self, request, queryset):
        sync_histories = []
        error_histories = []
        for history in queryset:
            try:
                history.synchronize()
                sync_histories.append(history)
            except:  # noqa
                error_histories.append(history)
        if sync_histories:
            self._get_message_history_synchronize(
                request,
                sync_histories,
                "history was successfully synchronized",
                "histories were successfully synchronized",
                messages.SUCCESS,
            )
        if error_histories:
            self._get_message_history_synchronize(
                request,
                error_histories,
                "history could not be synchronized",
                "histories could not be synchronized",
                messages.ERROR,
            )
