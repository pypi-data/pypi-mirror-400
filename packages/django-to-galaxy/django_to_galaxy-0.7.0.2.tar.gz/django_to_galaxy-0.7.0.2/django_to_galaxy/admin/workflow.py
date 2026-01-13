from django.contrib import admin, messages
from django_to_galaxy.admin.utils import update_workflowinputs

from django_to_galaxy.models.workflow import Workflow
from django_to_galaxy.models.accepted_input import (
    Format,
    WorkflowInput,
    WorkflowInputTextOption,
)

from .galaxy_element import GalaxyElementAdmin


@admin.register(Workflow)
class WorkflowAdmin(GalaxyElementAdmin):
    list_display = (
        "id",
        "name",
        "annotation",
        "galaxy_id",
        "get_is_meta",
        "get_step_count",
        "published",
        "galaxy_owner",
        "get_tags",
    )
    readonly_fields = (
        "id",
        "name",
        "annotation",
        "galaxy_id",
        "get_is_meta",
        "get_step_count",
        "published",
        "galaxy_owner",
        "get_tags",
    )
    actions = ["update_workflow_inputs"]

    def get_is_meta(self, obj):
        return obj.get_is_meta()

    def get_step_count(self, obj):
        return obj.get_step_count()

    def get_tags(self, obj):
        return ", ".join([p.label for p in obj.tags.all()])

    @admin.action(description="Update workflow inputs (1 workflow only)")
    def update_workflow_inputs(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                "You can update the workflow inputs of 1 workflow only at a time.",
                messages.ERROR,
            )
            return
        workflow = queryset[0]

        try:
            update_workflowinputs(workflow.id)
        except Exception as e:
            self.message_user(
                request,
                f"Could not update workflow inputs of '{workflow.name}' workflow: {e}",
                messages.ERROR,
            )
        else:
            self.message_user(
                request,
                f"Successfully updated workflow inputs of '{workflow.name}' workflow",
                messages.SUCCESS,
            )


@admin.register(Format)
class FormatAdmin(GalaxyElementAdmin):
    list_display = (
        "id",
        "format",
    )
    readonly_fields = (
        "id",
        "format",
    )


@admin.register(WorkflowInputTextOption)
class WorkflowInputTextOptionAdmin(GalaxyElementAdmin):
    list_display = ("id", "get_workflow", "workflow_input", "text_option")

    readonly_fields = ("id", "get_workflow", "workflow_input", "text_option")

    def get_workflow(self, obj):
        return obj.workflow_input.workflow


@admin.register(WorkflowInput)
class WorkflowInputAdmin(GalaxyElementAdmin):
    # Limit 20 items per page
    list_per_page = 20
    list_max_show_all = 50

    list_display = (
        "id",
        "galaxy_step_id",
        "label",
        "workflow",
        "input_type",
        "get_formats",
        "parameter_type",
        "collection_type",
        "optional",
        "default_value",
        "multiple",
    )
    readonly_fields = (
        "id",
        "galaxy_step_id",
        "label",
        "workflow",
        "get_formats",
        "parameter_type",
        "collection_type",
        "optional",
        "default_value",
        "multiple",
    )

    def get_formats(self, obj):
        return ", ".join([p.format for p in obj.formats.all()])
