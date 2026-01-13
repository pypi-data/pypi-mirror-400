import logging
from collections import defaultdict
from time import sleep
from typing import Any, List, Dict

from bioblend.galaxy.objects import wrappers
from django.db import models

from .galaxy_output_file import GalaxyOutputFile

from django_to_galaxy.utils import enabled_cache

from django.core.exceptions import ObjectDoesNotExist

RUNNING = "running"
DONE = "done"
ERROR = "error"
PAUSED = "paused"
STATUS_CHOICES = [
    (RUNNING, "Running"),
    (PAUSED, "Paused"),
    (ERROR, "Error"),
    (DONE, "Done"),
]

logger = logging.getLogger(__name__)


class Invocation(models.Model):
    """Table for invocations of workflow."""

    # Galaxy fields
    galaxy_id = models.CharField(null=False, max_length=50)
    """Invocation id used on the galaxy side."""
    galaxy_state = models.CharField(null=False, max_length=200)
    """State on the galaxy side."""
    # Django fields
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=RUNNING)
    """Status of the invocation."""
    workflow = models.ForeignKey(
        "Workflow", null=False, on_delete=models.CASCADE, related_name="workflows"
    )
    """Workflow the invocation comes from."""
    history = models.ForeignKey(
        "History", null=False, on_delete=models.CASCADE, related_name="histories"
    )
    """History used for the invocation."""
    create_time = models.DateTimeField()
    """Time the invocation was created."""

    def step_jobs_summary(self) -> List[Dict[str, Any]]:
        """Workaround self.galaxy_invocation.step_jobs_summary() due to v24.0 db issue"""
        step_jobs_summary = []
        for step_job in self.galaxy_invocation.steps:
            if step_job.job_id is not None:
                step_job_summary = {}
                step_job_summary["states"] = {}
                step_job_summary["id"] = step_job.job_id
                step_job_summary["states"][
                    self.galaxy_invocation.gi.jobs.get(step_job.job_id).state
                ] = 1
                step_jobs_summary.append(step_job_summary)

        return step_jobs_summary

    @property
    def galaxy_invocation(self) -> wrappers.Invocation:
        """Galaxy object using bioblend."""
        if getattr(self, "_galaxy_invocation", None) is None:
            self._galaxy_invocation = self._get_galaxy_invocation()
        return self._galaxy_invocation

    def _get_galaxy_invocation(self) -> wrappers.Invocation:
        """Get galaxy object using bioblend."""
        return self.workflow.galaxy_owner.obj_gi.invocations.get(self.galaxy_id)

    def complet_jobs_summary(self, step):
        subinv = self.galaxy_invocation.gi.invocations.get(
            step.wrapped["subworkflow_invocation_id"]
        )
        sub_jobs_summary = subinv.step_jobs_summary()
        for job in sub_jobs_summary:
            self.step_jobs_summary.append(job)
        for sub in subinv.steps:
            if "subworkflow_invocation_id" in sub.wrapped:
                if sub.wrapped["subworkflow_invocation_id"]:
                    self.complet_jobs_summary(sub)

    @property
    def percentage_done(self) -> float:
        """Retrieve percentage of steps done for the invocation."""
        if self.status == DONE:
            return 100.0
        self.step_jobs_summary = self.step_jobs_summary()

        inv_steps = self.galaxy_invocation.steps
        for step in inv_steps:
            if "subworkflow_invocation_id" in step.wrapped:
                if step.wrapped["subworkflow_invocation_id"]:
                    self.complet_jobs_summary(step)

        count_job_states = defaultdict(int)
        for step in self.step_jobs_summary:
            for key in step["states"].keys():
                count_job_states[key] += 1
        count_scheduled_steps = sum(step.state == "scheduled" for step in inv_steps)
        wf_step_count = self.workflow._step_count
        try:
            percentage_done = count_scheduled_steps / wf_step_count
        except ZeroDivisionError:
            percentage_done = 0
        if percentage_done == 1:
            last_job = inv_steps[wf_step_count - 1]
            if self.check_if_last_job_is_ok(last_job):
                self.status = DONE
                self.save()
            else:
                try:
                    percentage_done = (count_scheduled_steps - 1) / wf_step_count
                except ZeroDivisionError:
                    percentage_done = 0
        if "error" in count_job_states.keys():
            self.status = ERROR
            self.save()
        elif "paused" in count_job_states.keys():
            self.status = PAUSED
            self.save()
        return percentage_done * 100

    def check_if_last_job_is_ok(self, last_job):
        """Checks if the very last job is done"""
        if last_job.job_id:
            return self.galaxy_invocation.gi.jobs.get(last_job.job_id).state == "ok"
        if (
            "subworkflow_invocation_id" in last_job.wrapped
            and last_job.wrapped["subworkflow_invocation_id"]
            and len(
                self.galaxy_invocation.gi.invocations.get(
                    last_job.wrapped["subworkflow_invocation_id"]
                ).steps
            )
            > 0
        ):
            return self.check_if_last_job_is_ok(
                self.galaxy_invocation.gi.invocations.get(
                    last_job.wrapped["subworkflow_invocation_id"]
                ).steps[-1]
            )
        return False

    @property
    def job_id_to_tools(self) -> Dict[str, dict]:
        """Dict of job_id to wrapped tool."""
        if getattr(self, "_job_id_to_tools", None) is None:
            self._job_id_to_tools = self._build_job_id_to_tools()
        return self._job_id_to_tools

    def _build_job_id_to_tools(self) -> Dict[str, dict]:
        step_jobs_summary = self.step_jobs_summary()
        job_id_to_tools = {}
        for step in step_jobs_summary:
            job_id = step["id"]
            job = self.workflow.galaxy_owner.obj_gi.jobs.get(job_id)
            with enabled_cache():
                wrapped_tool = self.workflow.galaxy_owner.obj_gi.tools.get(
                    job.wrapped["tool_id"]
                ).wrapped
            job_id_to_tools[job_id] = wrapped_tool
        return job_id_to_tools

    @property
    def detailed_step_jobs_summary(self) -> List[dict]:
        """Retrive `step_jobs_summary` with details of tool used."""
        step_jobs_summary = self.step_jobs_summary()
        detailed_jobs_summary = []
        for step in step_jobs_summary:
            detailed_step = step
            job_id = step["id"]
            detailed_step["tool"] = self.job_id_to_tools.get(job_id, {})
            detailed_jobs_summary.append(detailed_step)
        return detailed_jobs_summary

    def synchronize(self):
        """Synchronize data from Galaxy instance."""
        galaxy_invocation = self._get_galaxy_invocation()
        self.galaxy_state = galaxy_invocation.state
        self.save()

    def create_output_files(self, max_retry: int = 3):
        """
        Create output files generated in the invocation.

        Args:
            max_retry: maximum number of time to try to retrieve info.
        """
        galaxy_inv_wrapped = self._get_galaxy_invocation().wrapped
        number_of_try = 1
        while not galaxy_inv_wrapped.get("outputs", {}) and (number_of_try < max_retry):
            sleep(0.25)
            galaxy_inv_wrapped = self._get_galaxy_invocation().wrapped
            number_of_try += 1
        if galaxy_inv_wrapped.get("outputs", {}):
            for output_name, output_content in galaxy_inv_wrapped["outputs"].items():
                try:
                    output_file = GalaxyOutputFile.objects.get(
                        galaxy_id=output_content["id"],
                        invocation=self,
                    )
                except ObjectDoesNotExist:
                    output_file = GalaxyOutputFile(
                        galaxy_id=output_content["id"],
                        workflow_name=output_name,
                        src=output_content["src"],
                        invocation=self,
                    )
                    output_file.save()
                output_file.synchronize()
        else:
            logger.warning(
                f"Could not create outputs from invocation: {self.galaxy_id}."
            )

    def update_output_files(self):
        """Update output files generated in the invocation."""
        galaxy_inv_wrapped = self._get_galaxy_invocation().wrapped
        if galaxy_inv_wrapped.get("outputs", {}):
            for output_name, output_content in galaxy_inv_wrapped["outputs"].items():
                try:
                    output_file = GalaxyOutputFile.objects.get(
                        galaxy_id=output_content["id"],
                        invocation=self,
                    )
                except ObjectDoesNotExist:
                    output_file = GalaxyOutputFile(
                        galaxy_id=output_content["id"],
                        workflow_name=output_name,
                        src=output_content["src"],
                        invocation=self,
                    )
                    output_file.save()
                output_file.synchronize()
        else:
            logger.warning(
                f"Could not update outputs from invocation: {self.galaxy_id}."
            )

    def __repr__(self):
        return f"Invocation: {self.__str__()}"

    def __str__(self):
        return f"{self.galaxy_id} [{self.workflow.name}]"
