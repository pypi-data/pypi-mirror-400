import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.cluster_status import ClusterStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cluster_config_type_0 import ClusterConfigType0


T = TypeVar("T", bound="Cluster")


@_attrs_define
class Cluster:
    """
    Attributes:
        config (Union['ClusterConfigType0', None, Unset]): Additional configuration (JSON format) Example: {'retry': 3,
            'timeout': 30}.
        created_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        description (Union[None, Unset, str]):  Example: Primary Slurm cluster.
        id (Union[Unset, int]):  Example: 1.
        name (Union[Unset, str]):  Example: cluster-01.
        slurm_api_version (Union[Unset, str]): Slurm REST API version (e.g., v0.0.40, v0.0.37) Default: 'v0.0.40'.
            Example: v0.0.40.
        slurm_jwt (Union[Unset, str]):  Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MzA0MzA0NDgsImlhdCI6MT
            c2NzM1ODQ0OCwic3VuIjoicm9vdCJ9.qTfUxVdSbd2OgrK_2aVmri1UWJWdCv9fsRfMknvC5aA.
        slurmrestd_url (Union[Unset, str]):  Example: http://slurmrestd.example.com:6820.
        status (Union[Unset, ClusterStatus]):  Example: active.
        updated_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
    """

    config: Union["ClusterConfigType0", None, Unset] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[None, Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    slurm_api_version: Union[Unset, str] = "v0.0.40"
    slurm_jwt: Union[Unset, str] = UNSET
    slurmrestd_url: Union[Unset, str] = UNSET
    status: Union[Unset, ClusterStatus] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.cluster_config_type_0 import ClusterConfigType0

        config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, ClusterConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        id = self.id

        name = self.name

        slurm_api_version = self.slurm_api_version

        slurm_jwt = self.slurm_jwt

        slurmrestd_url = self.slurmrestd_url

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config is not UNSET:
            field_dict["config"] = config
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if slurm_api_version is not UNSET:
            field_dict["slurm_api_version"] = slurm_api_version
        if slurm_jwt is not UNSET:
            field_dict["slurm_jwt"] = slurm_jwt
        if slurmrestd_url is not UNSET:
            field_dict["slurmrestd_url"] = slurmrestd_url
        if status is not UNSET:
            field_dict["status"] = status
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cluster_config_type_0 import ClusterConfigType0

        d = dict(src_dict)

        def _parse_config(data: object) -> Union["ClusterConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = ClusterConfigType0.from_dict(data)

                return config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ClusterConfigType0", None, Unset], data)

        config = _parse_config(d.pop("config", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        slurm_api_version = d.pop("slurm_api_version", UNSET)

        slurm_jwt = d.pop("slurm_jwt", UNSET)

        slurmrestd_url = d.pop("slurmrestd_url", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ClusterStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ClusterStatus(_status)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        cluster = cls(
            config=config,
            created_at=created_at,
            description=description,
            id=id,
            name=name,
            slurm_api_version=slurm_api_version,
            slurm_jwt=slurm_jwt,
            slurmrestd_url=slurmrestd_url,
            status=status,
            updated_at=updated_at,
        )

        cluster.additional_properties = d
        return cluster

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
