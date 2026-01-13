from bioblend.galaxy.objects import wrappers
from django.db import models
from .history import History
from .invocation import Invocation
from .galaxy_element import GalaxyElement

from django_to_galaxy.utils import load_galaxy_invocation_time_to_datetime


class Workflow(GalaxyElement):
    """Table for Galaxy workflows."""

    galaxy_owner = models.ForeignKey(
        "GalaxyUser", null=False, on_delete=models.CASCADE, related_name="workflows"
    )
    """Galaxy user that owns the workflow."""
    _step_count = models.PositiveIntegerField(default=0)
    """Number of steps in the workflow."""
    _is_meta = models.BooleanField(null=True, default=None, blank=True)
    """Indicates whether the workflow is a meta (i.e., has sub-workflows) or not."""

    @property
    def galaxy_workflow(self) -> wrappers.Workflow:
        """Galaxy object using bioblend."""
        if getattr(self, "_galaxy_workflow", None) is None:
            self._galaxy_workflow = self._get_galaxy_workflow()
        return self._galaxy_workflow

    def _get_galaxy_workflow(self) -> wrappers.Workflow:
        """Get galaxy object using bioblend."""
        return self.galaxy_owner.obj_gi.workflows.get(self.galaxy_id)

    def get_is_meta(self):
        """Sets / returns _is_meta value."""
        if self._is_meta is None:
            self._is_meta = False
            for key, step_dict in self.galaxy_workflow.steps.items():
                w = step_dict.wrapped
                if "workflow_id" in w:
                    self._is_meta = True
                    break
            self.save(update_fields=["_is_meta"])
        return self._is_meta

    def get_step_count(self):
        """Sets / returns _step_jobs_count value."""
        if self._step_count == 0:
            self._step_count = len(self.galaxy_workflow.steps)
            self.save(update_fields=["_step_count"])
        return self._step_count

    def _get_tool_input(self, tool_label, tool):
        """
        Retrieve a specific tool input dictionary from a Galaxy tool definition.

        This method navigates the nested structure of a tool's inputs or conditional cases
        to locate the input corresponding to `tool_label`. It supports labels that reference
        nested inputs using a "|" separator.

        Args:
            tool_label (str): The label of the input to retrieve. Can be a simple label
                or a nested label separated by "|", e.g. "param_group|param_name".
            tool (dict): The tool definition dictionary returned by Galaxy
            (from gi.tools.show_tool),
                which may contain:
                - "inputs": a list of input dictionaries
                - "cases": a list of conditional input cases

        Returns:
            dict: The dictionary representing the requested input, including all its parameters.
                If the input cannot be found, raises a ValueError or returns the original `tool`
                if it has no matching inputs/cases.

        Raises:
            ValueError: If the target input cannot be found when navigating a nested label.

        Notes:
            - Nested labels separated by "|" are resolved recursively.
            - Handles both regular "inputs" and conditional "cases".
            - If no inputs or cases match the label, the original `tool` dictionary is returned
            (for non-nested top-level tool access).

        Example:
            tool = {
                "inputs": [{"name": "param1", "type": "text"},
                           {"name": "param2", "type": "integer"}]
            }

            _get_tool_input("param1", tool)
            # Returns: {"name": "param1", "type": "text"}

            tool = {
                "cases": [{"inputs": [{"name": "choice1", "type": "text"}]}]
            }

            _get_tool_input("choice1", tool)
            # Returns: {"name": "choice1", "type": "text"}
        """
        if "|" in tool_label:
            first, tool_label = tool_label.split("|", maxsplit=1)
            if "inputs" in tool.keys():
                for x in tool["inputs"]:
                    if x["name"] == first:
                        return self._get_tool_input(tool_label, x)
            elif "cases" in tool.keys():
                for x in tool["cases"]:
                    if x["inputs"]:
                        if x["inputs"][0]["name"] == first:
                            return self._get_tool_input(tool_label, x["inputs"][0])
            else:
                raise ValueError(
                    f"Cannot find the target tool from this tool label: {tool_label}."
                )
        else:
            if "inputs" in tool.keys():
                for x in tool["inputs"]:
                    if x["name"] == tool_label:
                        return x
            elif "cases" in tool.keys():
                for x in tool["cases"]:
                    if x["inputs"]:
                        if x["inputs"][0]["name"] == tool_label:
                            return x["inputs"][0]
            else:
                return tool

    def _get_subworkflow_inputs(self, gi, input_mapping):
        """
        Recursively retrieve input information from subworkflows linked to a parameter input.

        This private method inspects the subworkflow referenced in `input_mapping["target_subwf"]`
        and updates the mapping with tools or nested subworkflows that consume the input.
        It handles multiple levels of nested subworkflows recursively.

        Args:
            gi (GalaxyInstance): The Galaxy instance object (typically
            `self.galaxy_owner.obj_gi.gi`) used to query workflows and tool details.
            input_mapping (dict): A dictionary representing a single parameter input.
            It must contain:
                - `has_subwf` (bool): True if the input is consumed by a subworkflow.
                - `target_subwf` (dict): Information about the first subworkflow that consumes
                the input:
                    - `workflow_id` (str): ID of the subworkflow
                    - `input_name` (str): Name of the input in the subworkflow
                - `target_tools` (list): List of tools that consume the input (will be updated)
                - `has_tool` (bool): Flag indicating whether a tool consumes the input (may be
                updated)

        Returns:
            dict: The updated `input_mapping` with:
                - `target_tools` populated with tools consuming the input from the subworkflow
                - `target_subwf` updated if nested subworkflows exist
                - `has_subwf` set to False once all subworkflow inputs have been resolved

        Notes:
            - This function uses recursion to traverse multiple levels of nested subworkflows.
            - It only processes the first subworkflow consuming the input at each level.
            - The function distinguishes between steps of type `"tool"` and `"subworkflow"`.

        Example:
            Before:
            {
                "label": "Parameter X",
                "type": "parameter_input",
                "target_tools": [],
                "target_subwf": {"input_name": "sub_input", "workflow_id": "wf_123"},
                "has_subwf": True
            }

            After:
            {
                "label": "Parameter X",
                "type": "parameter_input",
                "target_tools": [
                    {"input_name": "param1", "tool_id": "tool_456"}
                ],
                "target_subwf": None,
                "has_subwf": False
            }
        """

        if not input_mapping["has_subwf"]:
            return input_mapping

        subworkflow_id = input_mapping["target_subwf"]["workflow_id"]
        input_label = input_mapping["target_subwf"]["input_name"]

        # Get the subworkflow information
        data = gi.workflows.show_workflow(subworkflow_id, instance=True)

        input_keys = {v["label"]: k for k, v in data["inputs"].items()}
        steps = data["steps"]
        source_id = str(steps[input_keys[input_label]]["id"])

        step_ids = list(steps.keys())

        for step_id in step_ids:
            input_steps = steps[step_id].get("input_steps", {})
            for input_name, input_details in input_steps.items():
                if str(input_details.get("source_step")) == source_id:
                    if steps[step_id].get("type") == "tool":
                        input_mapping["target_tools"].append(
                            {
                                "input_name": input_name,
                                "tool_id": steps[step_id]["tool_id"],
                            }
                        )
                        input_mapping["has_subwf"] = False

                    elif steps[step_id].get("type") == "subworkflow":
                        if not input_mapping["has_subwf"]:
                            input_mapping["target_subwf"] = {
                                "input_name": input_name,
                                "workflow_id": steps[step_id]["workflow_id"],
                            }
                            input_mapping["has_subwf"] = True

        return self._get_subworkflow_inputs(gi, input_mapping)

    def get_workflow_inputs(self):
        """
        Retrieve detailed information about all inputs of a Galaxy workflow.

        This method processes a `Workflow` instance from `django-to-galaxy` and returns
        a dictionary describing each input, whether it is a `data_input` or a `parameter_input`.

        For each input, the returned information includes:
            - `label`: the human-readable label of the input
            - `type`: the type of input (`data_input` or `parameter_input`)
            - `tool_inputs`: the dictionary of tool inputs associated with the step
            - `target_tools`: for parameter inputs, a list of tools that consume this input
                - Each entry includes:
                    - `input_name`: the name of the input in the target tool
                    - `tool_id`: the Galaxy ID of the tool
                    - `tool_input`: the detailed tool input specification (retrieved later)
            - `target_subwf`: for parameter inputs, the first subworkflow that consumes this input
                - Includes:
                    - `input_name`: the name of the input in the subworkflow
                    - `workflow_id`: the ID of the subworkflow
            - `has_tool`: boolean flag indicating if any tool consumes this input
            - `has_subwf`: boolean flag indicating if any subworkflow consumes this input

        The function also handles nested subworkflows and retrieves input information
        for subworkflow parameters using `_get_subworkflow_inputs`. Tool-specific input
        details are retrieved using `_get_tool_input`.

        Args:
            self: A workflow wrapper instance containing:
                - `self.galaxy_workflow`: the Galaxy workflow object
                - `self.galaxy_owner.obj_gi.gi`: Galaxy instance handle

        Returns:
            dict: A mapping of input IDs to detailed information, for example:

            {
                "0": {
                    "label": "Input dataset",
                    "type": "data_input",
                    "tool_inputs": {...},
                },
                "1": {
                    "label": "Threshold",
                    "type": "parameter_input",
                    "tool_inputs": {...},
                    "target_tools": [
                        {
                            "input_name": "param1",
                            "tool_id": "toolshed.g2.bx.psu.edu/repos/.../tool/1",
                            "tool_input": {...},
                        }
                    ],
                    "target_subwf": {
                        "input_name": "subwf_input",
                        "workflow_id": "wf_123",
                    },
                    "has_tool": True,
                    "has_subwf": True,
                },
            }

        Known caveats:
            - Cannot retrieve the tool input if the tool has sections (e.g., `tooldistillator`
            tool).
            - Only the first subworkflow consuming a parameter input is inspected.

        """
        gi = self.galaxy_owner.obj_gi.gi

        inputs = self.galaxy_workflow.inputs
        steps = self.galaxy_workflow.steps
        steps = {k: v.wrapped for k, v in steps.items()}
        steps_ids = list(steps.keys())

        # Initialization
        input_mapping = {}
        parameter_input_ids = []

        for input_id, input_dict in inputs.items():
            input_mapping[input_id] = {}
            input_mapping[input_id]["label"] = input_dict["label"]
            input_mapping[input_id]["type"] = steps[input_id]["type"]
            input_mapping[input_id]["tool_inputs"] = steps[input_id]["tool_inputs"]

            if steps[input_id]["type"] == "parameter_input":
                parameter_input_ids.append(input_id)
                steps_ids.remove(input_id)
                input_mapping[input_id]["target_tools"] = []
                input_mapping[input_id]["target_subwf"] = None
                input_mapping[input_id]["has_tool"] = False
                input_mapping[input_id]["has_subwf"] = False

        for target_id in parameter_input_ids:
            for step_id in steps_ids:
                input_steps = steps[step_id].get("input_steps", {})
                for input_name, input_details in input_steps.items():
                    if input_details.get("source_step") == target_id:
                        if steps[step_id].get("type") == "tool":
                            input_mapping[target_id]["target_tools"].append(
                                {
                                    "input_name": input_name,
                                    "tool_id": steps[step_id]["tool_id"],
                                }
                            )
                            input_mapping[target_id]["has_tool"] = True
                        elif steps[step_id].get("type") == "subworkflow":
                            if not input_mapping[target_id]["has_subwf"]:
                                input_mapping[target_id]["target_subwf"] = {
                                    "input_name": input_name,
                                    "workflow_id": steps[step_id]["workflow_id"],
                                }
                                input_mapping[target_id]["has_subwf"] = True

        # Then search for subworkflows
        # For each input just search in the first subworkflow to get the parameters information
        for k in input_mapping.keys():
            if "target_subwf" in input_mapping[k].keys():
                input_mapping[k] = self._get_subworkflow_inputs(gi, input_mapping[k])

        # Then search input information in tools
        for k in input_mapping.keys():
            if "target_tools" in input_mapping[k].keys():
                for kk in input_mapping[k]["target_tools"]:
                    tool_label = kk["input_name"]
                    tool = gi.tools.show_tool(
                        kk["tool_id"],
                        io_details=True,
                        link_details=True,
                    )
                    kk["tool_input"] = self._get_tool_input(tool_label, tool)

        return input_mapping

    def get_workflow_datamap_template(self):
        """
        Generate a template of the datamap required to invoke a Galaxy workflow.

        This method inspects the workflow's inputs and steps, and constructs:
            1. `input_mapping`: a dictionary describing each input, including its label and type.
            2. `datamap_template`: a dictionary with default placeholders for input values
            suitable for workflow invocation.

        Input types are handled as follows:
            - "parameter_input": the parameter type from the tool inputs is returned as default.
            - "data_input": a dictionary with {"id": "", "src": "hda"}.
            - "data_collection_input": a dictionary with {"id": "", "src": "hdca"}.

        Returns:
            dict: A dictionary containing two keys:
                - "input_mapping" (dict): maps input IDs to dictionaries with:
                    - "label": human-readable label of the input
                    - "type": type of input ("parameter_input", "data_input", or
                    "data_collection_input")
                - "datamap_template" (dict): maps input IDs to default values/placeholders
                appropriate for workflow invocation.

        Example:
            {
                "input_mapping": {
                    "0": {"label": "Input dataset", "type": "data_input"},
                    "1": {"label": "Threshold", "type": "parameter_input"}
                },
                "datamap_template": {
                    "0": {"id": "", "src": "hda"},
                    "1": "integer"
                }
            }
        """

        inputs = self.galaxy_workflow.inputs
        steps = self.galaxy_workflow.steps
        steps = {k: v.wrapped for k, v in steps.items()}

        input_mapping = {}
        datamap_template = {}

        for input_id, input_dict in inputs.items():
            input_mapping[input_id] = {}
            input_mapping[input_id]["label"] = input_dict["label"]
            input_mapping[input_id]["type"] = steps[input_id]["type"]

            if steps[input_id]["type"] == "parameter_input":
                datamap_template[input_id] = steps[input_id]["tool_inputs"][
                    "parameter_type"
                ]
            elif steps[input_id]["type"] == "data_input":
                datamap_template[input_id] = {"id": "", "src": "hda"}
            elif steps[input_id]["type"] == "data_collection_input":
                datamap_template[input_id] = {"id": "", "src": "hdca"}

        return {"input_mapping": input_mapping, "datamap_template": datamap_template}

    def invoke(self, datamap: dict, history: History) -> wrappers.Invocation:
        """
        Invoke workflow using bioblend.

        Args:
            datamap: dictionnary to link dataset to workflow inputs
            history: history obj the dataset(s) come from

        Returns:
            Invocation object from bioblend
        """
        galaxy_inv = self.galaxy_workflow.invoke(
            datamap, history=history.galaxy_history
        )
        # Create invocations
        invocation = Invocation(
            galaxy_id=galaxy_inv.id,
            galaxy_state=galaxy_inv.state,
            workflow=self,
            history=history,
            create_time=load_galaxy_invocation_time_to_datetime(galaxy_inv),
        )
        invocation.save()
        # Create output files
        invocation.create_output_files()
        return invocation

    def __repr__(self):
        return f"Workflow: {super().__str__()}"
