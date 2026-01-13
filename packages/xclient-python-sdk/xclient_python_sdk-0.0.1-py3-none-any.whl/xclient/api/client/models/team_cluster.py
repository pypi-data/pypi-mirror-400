import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.team_cluster_cluster_type import TeamClusterClusterType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cluster import Cluster
    from ..models.k8s_cluster import K8SCluster
    from ..models.team_cluster_quota import TeamClusterQuota


T = TypeVar("T", bound="TeamCluster")


@_attrs_define
class TeamCluster:
    """
    Attributes:
        cluster (Union['Cluster', 'K8SCluster', Unset]): Cluster details (Slurm or K8s cluster)
        cluster_id (Union[Unset, int]):  Example: 1.
        cluster_type (Union[Unset, TeamClusterClusterType]):  Example: slurm.
        created_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        id (Union[Unset, int]):  Example: 1.
        quota (Union[Unset, TeamClusterQuota]): Quota limits (e.g., cpu, memory_gb, gpu) Example: {'cpu': 100, 'gpu':
            10, 'memory_gb': 500}.
        team_id (Union[Unset, int]):  Example: 1.
        updated_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
    """

    cluster: Union["Cluster", "K8SCluster", Unset] = UNSET
    cluster_id: Union[Unset, int] = UNSET
    cluster_type: Union[Unset, TeamClusterClusterType] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    id: Union[Unset, int] = UNSET
    quota: Union[Unset, "TeamClusterQuota"] = UNSET
    team_id: Union[Unset, int] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.cluster import Cluster

        cluster: Union[Unset, dict[str, Any]]
        if isinstance(self.cluster, Unset):
            cluster = UNSET
        elif isinstance(self.cluster, Cluster):
            cluster = self.cluster.to_dict()
        else:
            cluster = self.cluster.to_dict()

        cluster_id = self.cluster_id

        cluster_type: Union[Unset, str] = UNSET
        if not isinstance(self.cluster_type, Unset):
            cluster_type = self.cluster_type.value

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        id = self.id

        quota: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.quota, Unset):
            quota = self.quota.to_dict()

        team_id = self.team_id

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cluster is not UNSET:
            field_dict["cluster"] = cluster
        if cluster_id is not UNSET:
            field_dict["cluster_id"] = cluster_id
        if cluster_type is not UNSET:
            field_dict["cluster_type"] = cluster_type
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if id is not UNSET:
            field_dict["id"] = id
        if quota is not UNSET:
            field_dict["quota"] = quota
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cluster import Cluster
        from ..models.k8s_cluster import K8SCluster
        from ..models.team_cluster_quota import TeamClusterQuota

        d = dict(src_dict)

        def _parse_cluster(data: object) -> Union["Cluster", "K8SCluster", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                cluster_type_0 = Cluster.from_dict(data)

                return cluster_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            cluster_type_1 = K8SCluster.from_dict(data)

            return cluster_type_1

        cluster = _parse_cluster(d.pop("cluster", UNSET))

        cluster_id = d.pop("cluster_id", UNSET)

        _cluster_type = d.pop("cluster_type", UNSET)
        cluster_type: Union[Unset, TeamClusterClusterType]
        if isinstance(_cluster_type, Unset):
            cluster_type = UNSET
        else:
            cluster_type = TeamClusterClusterType(_cluster_type)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        id = d.pop("id", UNSET)

        _quota = d.pop("quota", UNSET)
        quota: Union[Unset, TeamClusterQuota]
        if isinstance(_quota, Unset):
            quota = UNSET
        else:
            quota = TeamClusterQuota.from_dict(_quota)

        team_id = d.pop("team_id", UNSET)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        team_cluster = cls(
            cluster=cluster,
            cluster_id=cluster_id,
            cluster_type=cluster_type,
            created_at=created_at,
            id=id,
            quota=quota,
            team_id=team_id,
            updated_at=updated_at,
        )

        team_cluster.additional_properties = d
        return team_cluster

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
