from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_team_cluster_request_quota import UpdateTeamClusterRequestQuota


T = TypeVar("T", bound="UpdateTeamClusterRequest")


@_attrs_define
class UpdateTeamClusterRequest:
    """
    Attributes:
        quota (Union[Unset, UpdateTeamClusterRequestQuota]): Quota limits (e.g., cpu, memory_gb, gpu) Example: {'cpu':
            100, 'gpu': 10, 'memory_gb': 500}.
    """

    quota: Union[Unset, "UpdateTeamClusterRequestQuota"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        quota: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.quota, Unset):
            quota = self.quota.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if quota is not UNSET:
            field_dict["quota"] = quota

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_team_cluster_request_quota import UpdateTeamClusterRequestQuota

        d = dict(src_dict)
        _quota = d.pop("quota", UNSET)
        quota: Union[Unset, UpdateTeamClusterRequestQuota]
        if isinstance(_quota, Unset):
            quota = UNSET
        else:
            quota = UpdateTeamClusterRequestQuota.from_dict(_quota)

        update_team_cluster_request = cls(
            quota=quota,
        )

        update_team_cluster_request.additional_properties = d
        return update_team_cluster_request

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
