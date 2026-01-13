import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.api_key_status import APIKeyStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateAPIKeyRequest")


@_attrs_define
class UpdateAPIKeyRequest:
    """
    Attributes:
        description (Union[None, Unset, str]):  Example: Updated description.
        expires_at (Union[None, Unset, datetime.datetime]):  Example: 2025-12-31T23:59:59Z.
        name (Union[Unset, str]):  Example: Updated API Key Name.
        status (Union[Unset, APIKeyStatus]):  Example: active.
    """

    description: Union[None, Unset, str] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    name: Union[Unset, str] = UNSET
    status: Union[Unset, APIKeyStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        name = self.name

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        name = d.pop("name", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, APIKeyStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = APIKeyStatus(_status)

        update_api_key_request = cls(
            description=description,
            expires_at=expires_at,
            name=name,
            status=status,
        )

        update_api_key_request.additional_properties = d
        return update_api_key_request

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
