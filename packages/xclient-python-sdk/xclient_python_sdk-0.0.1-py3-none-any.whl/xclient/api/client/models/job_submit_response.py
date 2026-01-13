from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JobSubmitResponse")


@_attrs_define
class JobSubmitResponse:
    """
    Attributes:
        id (Union[Unset, int]):  Example: 1.
        job_id (Union[Unset, str]):  Example: 12345.
        message (Union[Unset, str]):  Example: Job submitted successfully.
    """

    id: Union[Unset, int] = UNSET
    job_id: Union[Unset, str] = UNSET
    message: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        job_id = self.job_id

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        job_id = d.pop("job_id", UNSET)

        message = d.pop("message", UNSET)

        job_submit_response = cls(
            id=id,
            job_id=job_id,
            message=message,
        )

        job_submit_response.additional_properties = d
        return job_submit_response

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
