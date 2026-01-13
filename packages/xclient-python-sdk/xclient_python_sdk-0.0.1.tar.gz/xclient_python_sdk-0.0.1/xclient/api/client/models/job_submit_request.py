from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_submit_request_resources_type_0 import JobSubmitRequestResourcesType0


T = TypeVar("T", bound="JobSubmitRequest")


@_attrs_define
class JobSubmitRequest:
    """
    Attributes:
        name (str):  Example: training-job.
        script (str): Job script content Example: #!/bin/bash
            python train.py.
        cluster_id (Union[None, Unset, int]): Specify which cluster to submit to Example: 1.
        command (Union[None, Unset, str]):  Example: python train.py.
        resources (Union['JobSubmitRequestResourcesType0', None, Unset]): Resource requirements Example: {'cpu': 4,
            'gpu': 1, 'memory': '8GB'}.
        team_id (Union[None, Unset, int]):  Example: 1.
    """

    name: str
    script: str
    cluster_id: Union[None, Unset, int] = UNSET
    command: Union[None, Unset, str] = UNSET
    resources: Union["JobSubmitRequestResourcesType0", None, Unset] = UNSET
    team_id: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.job_submit_request_resources_type_0 import JobSubmitRequestResourcesType0

        name = self.name

        script = self.script

        cluster_id: Union[None, Unset, int]
        if isinstance(self.cluster_id, Unset):
            cluster_id = UNSET
        else:
            cluster_id = self.cluster_id

        command: Union[None, Unset, str]
        if isinstance(self.command, Unset):
            command = UNSET
        else:
            command = self.command

        resources: Union[None, Unset, dict[str, Any]]
        if isinstance(self.resources, Unset):
            resources = UNSET
        elif isinstance(self.resources, JobSubmitRequestResourcesType0):
            resources = self.resources.to_dict()
        else:
            resources = self.resources

        team_id: Union[None, Unset, int]
        if isinstance(self.team_id, Unset):
            team_id = UNSET
        else:
            team_id = self.team_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "script": script,
            }
        )
        if cluster_id is not UNSET:
            field_dict["cluster_id"] = cluster_id
        if command is not UNSET:
            field_dict["command"] = command
        if resources is not UNSET:
            field_dict["resources"] = resources
        if team_id is not UNSET:
            field_dict["team_id"] = team_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_submit_request_resources_type_0 import JobSubmitRequestResourcesType0

        d = dict(src_dict)
        name = d.pop("name")

        script = d.pop("script")

        def _parse_cluster_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        cluster_id = _parse_cluster_id(d.pop("cluster_id", UNSET))

        def _parse_command(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        command = _parse_command(d.pop("command", UNSET))

        def _parse_resources(data: object) -> Union["JobSubmitRequestResourcesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                resources_type_0 = JobSubmitRequestResourcesType0.from_dict(data)

                return resources_type_0
            except:  # noqa: E722
                pass
            return cast(Union["JobSubmitRequestResourcesType0", None, Unset], data)

        resources = _parse_resources(d.pop("resources", UNSET))

        def _parse_team_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        team_id = _parse_team_id(d.pop("team_id", UNSET))

        job_submit_request = cls(
            name=name,
            script=script,
            cluster_id=cluster_id,
            command=command,
            resources=resources,
            team_id=team_id,
        )

        job_submit_request.additional_properties = d
        return job_submit_request

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
