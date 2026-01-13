from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.assign_team_cluster_request_cluster_type import AssignTeamClusterRequestClusterType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.assign_team_cluster_request_quota import AssignTeamClusterRequestQuota


T = TypeVar("T", bound="AssignTeamClusterRequest")


@_attrs_define
class AssignTeamClusterRequest:
    """
    Attributes:
        cluster_id (int):  Example: 1.
        cluster_type (AssignTeamClusterRequestClusterType):  Example: slurm.
        quota (Union[Unset, AssignTeamClusterRequestQuota]): Quota limits (e.g., cpu, memory_gb, gpu) Example: {'cpu':
            100, 'gpu': 10, 'memory_gb': 500}.
    """

    cluster_id: int
    cluster_type: AssignTeamClusterRequestClusterType
    quota: Union[Unset, "AssignTeamClusterRequestQuota"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cluster_id = self.cluster_id

        cluster_type = self.cluster_type.value

        quota: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.quota, Unset):
            quota = self.quota.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cluster_id": cluster_id,
                "cluster_type": cluster_type,
            }
        )
        if quota is not UNSET:
            field_dict["quota"] = quota

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.assign_team_cluster_request_quota import AssignTeamClusterRequestQuota

        d = dict(src_dict)
        cluster_id = d.pop("cluster_id")

        cluster_type = AssignTeamClusterRequestClusterType(d.pop("cluster_type"))

        _quota = d.pop("quota", UNSET)
        quota: Union[Unset, AssignTeamClusterRequestQuota]
        if isinstance(_quota, Unset):
            quota = UNSET
        else:
            quota = AssignTeamClusterRequestQuota.from_dict(_quota)

        assign_team_cluster_request = cls(
            cluster_id=cluster_id,
            cluster_type=cluster_type,
            quota=quota,
        )

        assign_team_cluster_request.additional_properties = d
        return assign_team_cluster_request

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
