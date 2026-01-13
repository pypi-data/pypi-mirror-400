from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cluster_status import ClusterStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_cluster_request_config_type_0 import UpdateClusterRequestConfigType0


T = TypeVar("T", bound="UpdateClusterRequest")


@_attrs_define
class UpdateClusterRequest:
    """
    Attributes:
        config (Union['UpdateClusterRequestConfigType0', None, Unset]):  Example: {'retry': 3, 'timeout': 30}.
        description (Union[None, Unset, str]):  Example: Primary Slurm cluster.
        name (Union[Unset, str]):  Example: cluster-01.
        slurm_jwt (Union[Unset, str]):  Example: eyJhbxxxxiJIUzI1NixxxxR5cCI6IkpXVCJ9.eyJlexxxxjE4MzA0MzA0NDgsImlhdCI6MT
            c2NzM1xxxx0OCwic3VuIjoicm9vdCJ9.qTfUxVdSbd2OgrK_2aVmri1UWJWdCv9fsRfMknvC5aA.
        slurmrestd_url (Union[Unset, str]):  Example: http://slurmrestd.example.com:6820.
        status (Union[Unset, ClusterStatus]):  Example: active.
    """

    config: Union["UpdateClusterRequestConfigType0", None, Unset] = UNSET
    description: Union[None, Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    slurm_jwt: Union[Unset, str] = UNSET
    slurmrestd_url: Union[Unset, str] = UNSET
    status: Union[Unset, ClusterStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.update_cluster_request_config_type_0 import UpdateClusterRequestConfigType0

        config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, UpdateClusterRequestConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        name = self.name

        slurm_jwt = self.slurm_jwt

        slurmrestd_url = self.slurmrestd_url

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config is not UNSET:
            field_dict["config"] = config
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name
        if slurm_jwt is not UNSET:
            field_dict["slurm_jwt"] = slurm_jwt
        if slurmrestd_url is not UNSET:
            field_dict["slurmrestd_url"] = slurmrestd_url
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_cluster_request_config_type_0 import UpdateClusterRequestConfigType0

        d = dict(src_dict)

        def _parse_config(data: object) -> Union["UpdateClusterRequestConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = UpdateClusterRequestConfigType0.from_dict(data)

                return config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UpdateClusterRequestConfigType0", None, Unset], data)

        config = _parse_config(d.pop("config", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        name = d.pop("name", UNSET)

        slurm_jwt = d.pop("slurm_jwt", UNSET)

        slurmrestd_url = d.pop("slurmrestd_url", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ClusterStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ClusterStatus(_status)

        update_cluster_request = cls(
            config=config,
            description=description,
            name=name,
            slurm_jwt=slurm_jwt,
            slurmrestd_url=slurmrestd_url,
            status=status,
        )

        update_cluster_request.additional_properties = d
        return update_cluster_request

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
