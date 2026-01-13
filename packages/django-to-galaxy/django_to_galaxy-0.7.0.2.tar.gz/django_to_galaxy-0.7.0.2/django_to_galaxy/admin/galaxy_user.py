from typing import List

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.translation import ngettext

from django_to_galaxy.models.galaxy_user import GalaxyUser
from django_to_galaxy.models.galaxy_element import Tag
from django_to_galaxy.admin.utils import update_workflowinputs


@admin.register(GalaxyUser)
class GalaxyUserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "hide_api_key",
        "galaxy_instance",
        "get_number_histories",
        "get_number_workflows",
    )
    list_filter = ("galaxy_instance",)
    actions = ["create_history", "import_workflows"]

    def get_urls(self):
        from django.urls import path

        return [
            path(
                "<path:object_id>/import_workflows/",
                self._import_workflows_view,
                name="Import workflow",
            ),
        ] + super().get_urls()

    def hide_api_key(self, obj):
        api_key = obj.api_key
        return api_key.replace(api_key[4:-4], len(api_key[4:-4]) * "*")

    def get_number_histories(self, obj):
        count = obj.histories.count()
        url = (
            reverse("admin:django_to_galaxy_history_changelist")
            + "?"
            + urlencode({"galaxy_owner__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, count)

    def get_number_workflows(self, obj):
        count = obj.workflows.count()
        url = (
            reverse("admin:django_to_galaxy_workflow_changelist")
            + "?"
            + urlencode({"galaxy_owner__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">{}</a>', url, count)

    def _get_message_history_creation(
        self,
        request,
        users: List[GalaxyUser],
        message_singular: str,
        message_plural: str,
        message_type: int,
    ):
        count = len(users)
        details = ", ".join([f"{u.email}->{u.galaxy_instance.url}" for u in users])
        self.message_user(
            request,
            ngettext(
                f"%d {message_singular} ({details}).",
                f"%d {message_plural} ({details}).",
                count,
            )
            % count,
            message_type,
        )

    @admin.action(description="Create history")
    def create_history(self, request, queryset):
        created_users = []
        skipped_users = []
        for user in queryset:
            try:
                user.create_history()
                created_users.append(user)
            except:  # noqa
                skipped_users.append(user)
        if created_users:
            self._get_message_history_creation(
                request,
                created_users,
                "history was successfully created",
                "histories were successfully created",
                messages.SUCCESS,
            )
        if skipped_users:
            self._get_message_history_creation(
                request,
                skipped_users,
                "history could not be created",
                "histories could not be created",
                messages.ERROR,
            )

    @admin.action(description="Import workflow(s) (1 user only)")
    def import_workflows(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                "You can import workflow from 1 user only at a time.",
                messages.ERROR,
            )
            return
        user = queryset[0]
        if not user.galaxy_instance.is_online():
            self.message_user(
                request,
                (
                    f"{user.galaxy_instance} is currently not available."
                    " Please try later or contact its administrator(s)."
                ),
                messages.ERROR,
            )
            return None
        return HttpResponseRedirect(f"{user.id}/import_workflows/")

    def _import_workflows_view(self, request, object_id):
        galaxy_user = GalaxyUser.objects.prefetch_related("workflows").get(id=object_id)
        existing_workflows = list(galaxy_user.workflows.all())
        existing_galaxy_ids = tuple(wf.galaxy_id for wf in existing_workflows)
        new_workflows = []
        for galaxy_wf, tags in galaxy_user.available_workflows:
            if galaxy_wf.galaxy_id not in existing_galaxy_ids:
                new_workflows.append((galaxy_wf, tags))
        if request.method == "POST":
            galaxy_id_to_save = tuple(request.POST.getlist("save_to_app"))
            for wf, tags in new_workflows:
                id_tags = []
                for tag in tags:
                    savedtag, created = Tag.objects.get_or_create(label=tag)
                    id_tags.append(savedtag.id)
                if wf.galaxy_id in galaxy_id_to_save:
                    wf.save()
                    try:
                        update_workflowinputs(wf.id)
                    except Exception as e:
                        self.message_user(
                            request,
                            f"Could not import '{wf.name}' workflow: {e}",
                            messages.ERROR,
                        )
                    else:
                        for tag in id_tags:
                            wf.tags.add(tag)
                        wf.save()
                        existing_workflows.append(wf)
                        new_workflows.remove((wf, tags))
                        self.message_user(
                            request,
                            f"Successfully imported '{wf.name}' workflow",
                            messages.SUCCESS,
                        )

        context = dict(
            self.admin_site.each_context(request),
            galaxy_user=galaxy_user,
            existing_workflows=existing_workflows,
            new_workflows=new_workflows,
        )
        return render(
            request,
            "admin/import_workflows.html",
            context=context,
        )

    hide_api_key.short_description = "API Key"
    get_number_histories.short_description = "Histories"
    get_number_workflows.short_description = "Workflows"
