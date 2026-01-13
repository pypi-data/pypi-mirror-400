from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="JobAllocTresType0")


@_attrs_define
class JobAllocTresType0:
    """Allocated TRES (Trackable Resources)

    Example:
        {'cpu': 4, 'gpu': 1, 'mem': 8589934592}

    """

    additional_properties: dict[str, int] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_alloc_tres_type_0 = cls()

        job_alloc_tres_type_0.additional_properties = d
        return job_alloc_tres_type_0

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> int:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: int) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
