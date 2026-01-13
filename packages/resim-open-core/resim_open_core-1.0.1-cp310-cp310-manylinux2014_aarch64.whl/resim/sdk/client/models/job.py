from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.conflated_job_status import ConflatedJobStatus
from ..models.job_status import JobStatus
from ..models.metric_status import MetricStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
import datetime

if TYPE_CHECKING:
  from ..models.environment_variable import EnvironmentVariable
  from ..models.job_status_history_type import JobStatusHistoryType
  from ..models.batch_parameters import BatchParameters
  from ..models.execution_error import ExecutionError





T = TypeVar("T", bound="Job")



@_attrs_define
class Job:
    """ 
        Attributes:
            job_id (str | Unset):
            project_id (str | Unset):
            batch_id (str | Unset):
            system_id (str | Unset):
            branch_id (str | Unset):
            conflated_status (ConflatedJobStatus | Unset):
            description (str | Unset):
            job_status (JobStatus | Unset):
            job_metrics_status (MetricStatus | Unset):
            last_run_timestamp (datetime.datetime | Unset):
            status_history (list[JobStatusHistoryType] | Unset):
            last_updated_timestamp (datetime.datetime | Unset):
            output_location (str | Unset):
            execution_error (ExecutionError | Unset):
            execution_errors (list[ExecutionError] | None | Unset):
            experience_id (str | Unset):
            experience_name (str | Unset):
            experience_profile (str | Unset):
            experience_environment_variables (list[EnvironmentVariable] | Unset):
            build_id (str | Unset):
            creation_timestamp (datetime.datetime | Unset):
            parameters (BatchParameters | Unset):
            user_id (str | Unset):
            org_id (str | Unset):
            run_counter (int | Unset):
            worker_id (str | Unset):
     """

    job_id: str | Unset = UNSET
    project_id: str | Unset = UNSET
    batch_id: str | Unset = UNSET
    system_id: str | Unset = UNSET
    branch_id: str | Unset = UNSET
    conflated_status: ConflatedJobStatus | Unset = UNSET
    description: str | Unset = UNSET
    job_status: JobStatus | Unset = UNSET
    job_metrics_status: MetricStatus | Unset = UNSET
    last_run_timestamp: datetime.datetime | Unset = UNSET
    status_history: list[JobStatusHistoryType] | Unset = UNSET
    last_updated_timestamp: datetime.datetime | Unset = UNSET
    output_location: str | Unset = UNSET
    execution_error: ExecutionError | Unset = UNSET
    execution_errors: list[ExecutionError] | None | Unset = UNSET
    experience_id: str | Unset = UNSET
    experience_name: str | Unset = UNSET
    experience_profile: str | Unset = UNSET
    experience_environment_variables: list[EnvironmentVariable] | Unset = UNSET
    build_id: str | Unset = UNSET
    creation_timestamp: datetime.datetime | Unset = UNSET
    parameters: BatchParameters | Unset = UNSET
    user_id: str | Unset = UNSET
    org_id: str | Unset = UNSET
    run_counter: int | Unset = UNSET
    worker_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.environment_variable import EnvironmentVariable
        from ..models.job_status_history_type import JobStatusHistoryType
        from ..models.batch_parameters import BatchParameters
        from ..models.execution_error import ExecutionError
        job_id = self.job_id

        project_id = self.project_id

        batch_id = self.batch_id

        system_id = self.system_id

        branch_id = self.branch_id

        conflated_status: str | Unset = UNSET
        if not isinstance(self.conflated_status, Unset):
            conflated_status = self.conflated_status.value


        description = self.description

        job_status: str | Unset = UNSET
        if not isinstance(self.job_status, Unset):
            job_status = self.job_status.value


        job_metrics_status: str | Unset = UNSET
        if not isinstance(self.job_metrics_status, Unset):
            job_metrics_status = self.job_metrics_status.value


        last_run_timestamp: str | Unset = UNSET
        if not isinstance(self.last_run_timestamp, Unset):
            last_run_timestamp = self.last_run_timestamp.isoformat()

        status_history: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.status_history, Unset):
            status_history = []
            for componentsschemasjob_status_history_item_data in self.status_history:
                componentsschemasjob_status_history_item = componentsschemasjob_status_history_item_data.to_dict()
                status_history.append(componentsschemasjob_status_history_item)



        last_updated_timestamp: str | Unset = UNSET
        if not isinstance(self.last_updated_timestamp, Unset):
            last_updated_timestamp = self.last_updated_timestamp.isoformat()

        output_location = self.output_location

        execution_error: dict[str, Any] | Unset = UNSET
        if not isinstance(self.execution_error, Unset):
            execution_error = self.execution_error.to_dict()

        execution_errors: list[dict[str, Any]] | None | Unset
        if isinstance(self.execution_errors, Unset):
            execution_errors = UNSET
        elif isinstance(self.execution_errors, list):
            execution_errors = []
            for execution_errors_type_0_item_data in self.execution_errors:
                execution_errors_type_0_item = execution_errors_type_0_item_data.to_dict()
                execution_errors.append(execution_errors_type_0_item)


        else:
            execution_errors = self.execution_errors

        experience_id = self.experience_id

        experience_name = self.experience_name

        experience_profile = self.experience_profile

        experience_environment_variables: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.experience_environment_variables, Unset):
            experience_environment_variables = []
            for experience_environment_variables_item_data in self.experience_environment_variables:
                experience_environment_variables_item = experience_environment_variables_item_data.to_dict()
                experience_environment_variables.append(experience_environment_variables_item)



        build_id = self.build_id

        creation_timestamp: str | Unset = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        user_id = self.user_id

        org_id = self.org_id

        run_counter = self.run_counter

        worker_id = self.worker_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if job_id is not UNSET:
            field_dict["jobID"] = job_id
        if project_id is not UNSET:
            field_dict["projectID"] = project_id
        if batch_id is not UNSET:
            field_dict["batchID"] = batch_id
        if system_id is not UNSET:
            field_dict["systemID"] = system_id
        if branch_id is not UNSET:
            field_dict["branchID"] = branch_id
        if conflated_status is not UNSET:
            field_dict["conflatedStatus"] = conflated_status
        if description is not UNSET:
            field_dict["description"] = description
        if job_status is not UNSET:
            field_dict["jobStatus"] = job_status
        if job_metrics_status is not UNSET:
            field_dict["jobMetricsStatus"] = job_metrics_status
        if last_run_timestamp is not UNSET:
            field_dict["lastRunTimestamp"] = last_run_timestamp
        if status_history is not UNSET:
            field_dict["statusHistory"] = status_history
        if last_updated_timestamp is not UNSET:
            field_dict["lastUpdatedTimestamp"] = last_updated_timestamp
        if output_location is not UNSET:
            field_dict["outputLocation"] = output_location
        if execution_error is not UNSET:
            field_dict["executionError"] = execution_error
        if execution_errors is not UNSET:
            field_dict["executionErrors"] = execution_errors
        if experience_id is not UNSET:
            field_dict["experienceID"] = experience_id
        if experience_name is not UNSET:
            field_dict["experienceName"] = experience_name
        if experience_profile is not UNSET:
            field_dict["experienceProfile"] = experience_profile
        if experience_environment_variables is not UNSET:
            field_dict["experienceEnvironmentVariables"] = experience_environment_variables
        if build_id is not UNSET:
            field_dict["buildID"] = build_id
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if user_id is not UNSET:
            field_dict["userID"] = user_id
        if org_id is not UNSET:
            field_dict["orgID"] = org_id
        if run_counter is not UNSET:
            field_dict["runCounter"] = run_counter
        if worker_id is not UNSET:
            field_dict["workerID"] = worker_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_variable import EnvironmentVariable
        from ..models.job_status_history_type import JobStatusHistoryType
        from ..models.batch_parameters import BatchParameters
        from ..models.execution_error import ExecutionError
        d = dict(src_dict)
        job_id = d.pop("jobID", UNSET)

        project_id = d.pop("projectID", UNSET)

        batch_id = d.pop("batchID", UNSET)

        system_id = d.pop("systemID", UNSET)

        branch_id = d.pop("branchID", UNSET)

        _conflated_status = d.pop("conflatedStatus", UNSET)
        conflated_status: ConflatedJobStatus | Unset
        if isinstance(_conflated_status,  Unset):
            conflated_status = UNSET
        else:
            conflated_status = ConflatedJobStatus(_conflated_status)




        description = d.pop("description", UNSET)

        _job_status = d.pop("jobStatus", UNSET)
        job_status: JobStatus | Unset
        if isinstance(_job_status,  Unset):
            job_status = UNSET
        else:
            job_status = JobStatus(_job_status)




        _job_metrics_status = d.pop("jobMetricsStatus", UNSET)
        job_metrics_status: MetricStatus | Unset
        if isinstance(_job_metrics_status,  Unset):
            job_metrics_status = UNSET
        else:
            job_metrics_status = MetricStatus(_job_metrics_status)




        _last_run_timestamp = d.pop("lastRunTimestamp", UNSET)
        last_run_timestamp: datetime.datetime | Unset
        if isinstance(_last_run_timestamp,  Unset):
            last_run_timestamp = UNSET
        else:
            last_run_timestamp = isoparse(_last_run_timestamp)




        status_history = []
        _status_history = d.pop("statusHistory", UNSET)
        for componentsschemasjob_status_history_item_data in (_status_history or []):
            componentsschemasjob_status_history_item = JobStatusHistoryType.from_dict(componentsschemasjob_status_history_item_data)



            status_history.append(componentsschemasjob_status_history_item)


        _last_updated_timestamp = d.pop("lastUpdatedTimestamp", UNSET)
        last_updated_timestamp: datetime.datetime | Unset
        if isinstance(_last_updated_timestamp,  Unset):
            last_updated_timestamp = UNSET
        else:
            last_updated_timestamp = isoparse(_last_updated_timestamp)




        output_location = d.pop("outputLocation", UNSET)

        _execution_error = d.pop("executionError", UNSET)
        execution_error: ExecutionError | Unset
        if isinstance(_execution_error,  Unset):
            execution_error = UNSET
        else:
            execution_error = ExecutionError.from_dict(_execution_error)




        def _parse_execution_errors(data: object) -> list[ExecutionError] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                execution_errors_type_0 = []
                _execution_errors_type_0 = data
                for execution_errors_type_0_item_data in (_execution_errors_type_0):
                    execution_errors_type_0_item = ExecutionError.from_dict(execution_errors_type_0_item_data)



                    execution_errors_type_0.append(execution_errors_type_0_item)

                return execution_errors_type_0
            except: # noqa: E722
                pass
            return cast(list[ExecutionError] | None | Unset, data)

        execution_errors = _parse_execution_errors(d.pop("executionErrors", UNSET))


        experience_id = d.pop("experienceID", UNSET)

        experience_name = d.pop("experienceName", UNSET)

        experience_profile = d.pop("experienceProfile", UNSET)

        experience_environment_variables = []
        _experience_environment_variables = d.pop("experienceEnvironmentVariables", UNSET)
        for experience_environment_variables_item_data in (_experience_environment_variables or []):
            experience_environment_variables_item = EnvironmentVariable.from_dict(experience_environment_variables_item_data)



            experience_environment_variables.append(experience_environment_variables_item)


        build_id = d.pop("buildID", UNSET)

        _creation_timestamp = d.pop("creationTimestamp", UNSET)
        creation_timestamp: datetime.datetime | Unset
        if isinstance(_creation_timestamp,  Unset):
            creation_timestamp = UNSET
        else:
            creation_timestamp = isoparse(_creation_timestamp)




        _parameters = d.pop("parameters", UNSET)
        parameters: BatchParameters | Unset
        if isinstance(_parameters,  Unset):
            parameters = UNSET
        else:
            parameters = BatchParameters.from_dict(_parameters)




        user_id = d.pop("userID", UNSET)

        org_id = d.pop("orgID", UNSET)

        run_counter = d.pop("runCounter", UNSET)

        worker_id = d.pop("workerID", UNSET)

        job = cls(
            job_id=job_id,
            project_id=project_id,
            batch_id=batch_id,
            system_id=system_id,
            branch_id=branch_id,
            conflated_status=conflated_status,
            description=description,
            job_status=job_status,
            job_metrics_status=job_metrics_status,
            last_run_timestamp=last_run_timestamp,
            status_history=status_history,
            last_updated_timestamp=last_updated_timestamp,
            output_location=output_location,
            execution_error=execution_error,
            execution_errors=execution_errors,
            experience_id=experience_id,
            experience_name=experience_name,
            experience_profile=experience_profile,
            experience_environment_variables=experience_environment_variables,
            build_id=build_id,
            creation_timestamp=creation_timestamp,
            parameters=parameters,
            user_id=user_id,
            org_id=org_id,
            run_counter=run_counter,
            worker_id=worker_id,
        )


        job.additional_properties = d
        return job

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
