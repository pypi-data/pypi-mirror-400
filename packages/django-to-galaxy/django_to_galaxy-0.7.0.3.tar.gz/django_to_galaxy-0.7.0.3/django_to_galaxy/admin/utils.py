from django_to_galaxy.models.workflow import Workflow
from django.db import transaction
from django_to_galaxy.models.accepted_input import (
    Format,
    WorkflowInput,
    DATA,
    COLLECTION,
    PARAMETER,
    P_TEXT,
    WorkflowInputTextOption,
)

"""
Update inputs information of a workflow functions
"""


def search_step_info_value(key, value_none, step_info):
    if key in step_info["tool_inputs"].keys():
        value = step_info["tool_inputs"][key]
    else:
        try:
            value = step_info["target_tools"][0]["tool_input"][key]
        except Exception:
            value = value_none

    return value


def update_workflowinputs(workflow_id):
    wf = Workflow.objects.get(id=workflow_id)
    try:
        with transaction.atomic():
            # Saving workflow inputs
            input_mapping = wf.get_workflow_inputs()

            # Remove existing inputs
            WorkflowInput.objects.filter(workflow=wf).delete()

            for step, step_info in input_mapping.items():
                input_type = step_info["type"]
                if input_type == DATA:
                    workflowinput, created = WorkflowInput.objects.get_or_create(
                        galaxy_step_id=step,
                        label=step_info["label"],
                        workflow=wf,
                        input_type=input_type,
                        parameter_type=None,
                        collection_type=None,
                        optional=step_info["tool_inputs"]["optional"],
                        default_value=None,
                        multiple=False,
                    )
                elif input_type == COLLECTION:
                    workflowinput, created = WorkflowInput.objects.get_or_create(
                        galaxy_step_id=step,
                        label=step_info["label"],
                        workflow=wf,
                        input_type=input_type,
                        parameter_type=None,
                        collection_type=step_info["tool_inputs"]["collection_type"],
                        optional=step_info["tool_inputs"]["optional"],
                        default_value=None,
                        multiple=False,
                    )
                elif input_type == PARAMETER:
                    parameter_type = step_info["tool_inputs"]["parameter_type"]
                    default_value = search_step_info_value("default", None, step_info)
                    multiple = search_step_info_value("multiple", False, step_info)

                    workflowinput, created = WorkflowInput.objects.get_or_create(
                        galaxy_step_id=step,
                        label=step_info["label"],
                        workflow=wf,
                        input_type=input_type,
                        parameter_type=parameter_type,
                        collection_type=None,
                        optional=step_info["tool_inputs"]["optional"],
                        default_value=default_value,
                        multiple=multiple,
                    )
                    if created and parameter_type == P_TEXT:
                        # Add TextOption
                        if "restrictions" in step_info["tool_inputs"].keys():
                            # If there are restrictions, we're saving them
                            for value in step_info["tool_inputs"]["restrictions"]:
                                (
                                    workflowinputtextoption,
                                    _,
                                ) = WorkflowInputTextOption.objects.get_or_create(
                                    workflow_input=workflowinput, text_option=value
                                )
                        else:
                            # If no restrictions, we are getting the options from the 1st tool
                            try:
                                tool_info = step_info["target_tools"][0]
                                for opt in tool_info["tool_input"]["options"]:
                                    (
                                        workflowinputtextoption,
                                        _,
                                    ) = WorkflowInputTextOption.objects.get_or_create(
                                        workflow_input=workflowinput, text_option=opt[1]
                                    )
                            except (KeyError, ValueError):
                                pass
                if "format" in step_info["tool_inputs"].keys():
                    for format in step_info["tool_inputs"]["format"]:
                        (
                            winputformat,
                            _,
                        ) = Format.objects.get_or_create(format=format.strip())
                        workflowinput.formats.add(winputformat.id)
    except Exception as e:
        raise e
    else:
        return
