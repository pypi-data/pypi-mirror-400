from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cluster_status import ClusterStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_cluster_request_config_type_0 import CreateClusterRequestConfigType0


T = TypeVar("T", bound="CreateClusterRequest")


@_attrs_define
class CreateClusterRequest:
    """
    Attributes:
        name (str):  Example: cluster-01.
        slurm_jwt (str):  Example: eyJhbxxxxiJIUzI1NixxxxR5cCI6IkpXVCJ9.eyJlexxxxjE4MzA0MzA0NDgsImlhdCI6MTc2NzM1xxxx0OCw
            ic3VuIjoicm9vdCJ9.qTfUxVdSbd2OgrK_2aVmri1UWJWdCv9fsRfMknvC5aA.
        slurmrestd_url (str):  Example: http://slurmrestd.example.com:6820.
        config (Union['CreateClusterRequestConfigType0', None, Unset]):  Example: {'retry': 3, 'timeout': 30}.
        description (Union[Unset, str]):  Example: Primary Slurm cluster.
        status (Union[Unset, ClusterStatus]):  Example: active.
    """

    name: str
    slurm_jwt: str
    slurmrestd_url: str
    config: Union["CreateClusterRequestConfigType0", None, Unset] = UNSET
    description: Union[Unset, str] = UNSET
    status: Union[Unset, ClusterStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.create_cluster_request_config_type_0 import CreateClusterRequestConfigType0

        name = self.name

        slurm_jwt = self.slurm_jwt

        slurmrestd_url = self.slurmrestd_url

        config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, CreateClusterRequestConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        description = self.description

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "slurm_jwt": slurm_jwt,
                "slurmrestd_url": slurmrestd_url,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config
        if description is not UNSET:
            field_dict["description"] = description
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_cluster_request_config_type_0 import CreateClusterRequestConfigType0

        d = dict(src_dict)
        name = d.pop("name")

        slurm_jwt = d.pop("slurm_jwt")

        slurmrestd_url = d.pop("slurmrestd_url")

        def _parse_config(data: object) -> Union["CreateClusterRequestConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = CreateClusterRequestConfigType0.from_dict(data)

                return config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CreateClusterRequestConfigType0", None, Unset], data)

        config = _parse_config(d.pop("config", UNSET))

        description = d.pop("description", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ClusterStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ClusterStatus(_status)

        create_cluster_request = cls(
            name=name,
            slurm_jwt=slurm_jwt,
            slurmrestd_url=slurmrestd_url,
            config=config,
            description=description,
            status=status,
        )

        create_cluster_request.additional_properties = d
        return create_cluster_request

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
