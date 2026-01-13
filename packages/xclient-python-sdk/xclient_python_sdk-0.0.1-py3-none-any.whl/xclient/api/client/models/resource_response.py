from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.resource_response_clusters_item import ResourceResponseClustersItem


T = TypeVar("T", bound="ResourceResponse")


@_attrs_define
class ResourceResponse:
    """
    Attributes:
        clusters (Union[Unset, list['ResourceResponseClustersItem']]):
    """

    clusters: Union[Unset, list["ResourceResponseClustersItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        clusters: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.clusters, Unset):
            clusters = []
            for clusters_item_data in self.clusters:
                clusters_item = clusters_item_data.to_dict()
                clusters.append(clusters_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if clusters is not UNSET:
            field_dict["clusters"] = clusters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_response_clusters_item import ResourceResponseClustersItem

        d = dict(src_dict)
        clusters = []
        _clusters = d.pop("clusters", UNSET)
        for clusters_item_data in _clusters or []:
            clusters_item = ResourceResponseClustersItem.from_dict(clusters_item_data)

            clusters.append(clusters_item)

        resource_response = cls(
            clusters=clusters,
        )

        resource_response.additional_properties = d
        return resource_response

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
