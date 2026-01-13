from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResourceResponseClustersItemGpu")


@_attrs_define
class ResourceResponseClustersItemGpu:
    """
    Attributes:
        available (Union[Unset, int]):  Example: 12.
        total (Union[Unset, int]):  Example: 20.
        used (Union[Unset, int]):  Example: 8.
    """

    available: Union[Unset, int] = UNSET
    total: Union[Unset, int] = UNSET
    used: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        available = self.available

        total = self.total

        used = self.used

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if available is not UNSET:
            field_dict["available"] = available
        if total is not UNSET:
            field_dict["total"] = total
        if used is not UNSET:
            field_dict["used"] = used

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        available = d.pop("available", UNSET)

        total = d.pop("total", UNSET)

        used = d.pop("used", UNSET)

        resource_response_clusters_item_gpu = cls(
            available=available,
            total=total,
            used=used,
        )

        resource_response_clusters_item_gpu.additional_properties = d
        return resource_response_clusters_item_gpu

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
