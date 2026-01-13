from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cluster import Cluster


T = TypeVar("T", bound="ClusterListResponse")


@_attrs_define
class ClusterListResponse:
    """
    Attributes:
        clusters (Union[Unset, list['Cluster']]):
        page (Union[Unset, int]):  Example: 1.
        page_size (Union[Unset, int]):  Example: 20.
        total (Union[Unset, int]):  Example: 5.
    """

    clusters: Union[Unset, list["Cluster"]] = UNSET
    page: Union[Unset, int] = UNSET
    page_size: Union[Unset, int] = UNSET
    total: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        clusters: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.clusters, Unset):
            clusters = []
            for clusters_item_data in self.clusters:
                clusters_item = clusters_item_data.to_dict()
                clusters.append(clusters_item)

        page = self.page

        page_size = self.page_size

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if clusters is not UNSET:
            field_dict["clusters"] = clusters
        if page is not UNSET:
            field_dict["page"] = page
        if page_size is not UNSET:
            field_dict["page_size"] = page_size
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cluster import Cluster

        d = dict(src_dict)
        clusters = []
        _clusters = d.pop("clusters", UNSET)
        for clusters_item_data in _clusters or []:
            clusters_item = Cluster.from_dict(clusters_item_data)

            clusters.append(clusters_item)

        page = d.pop("page", UNSET)

        page_size = d.pop("page_size", UNSET)

        total = d.pop("total", UNSET)

        cluster_list_response = cls(
            clusters=clusters,
            page=page,
            page_size=page_size,
            total=total,
        )

        cluster_list_response.additional_properties = d
        return cluster_list_response

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
