import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateAPIKeyResponse")


@_attrs_define
class CreateAPIKeyResponse:
    """
    Attributes:
        api_key (Union[Unset, str]): The generated API key (only shown once, store it securely) Example:
            xck_1234567890abcdefghijklmnopqrstuvwxyz.
        expires_at (Union[None, Unset, datetime.datetime]):  Example: 2025-12-31T23:59:59Z.
        id (Union[Unset, int]):  Example: 1.
        message (Union[Unset, str]):  Example: API key created successfully.
        name (Union[Unset, str]):  Example: Production API Key.
        team_id (Union[Unset, int]):  Example: 1.
    """

    api_key: Union[Unset, str] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    id: Union[Unset, int] = UNSET
    message: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    team_id: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        api_key = self.api_key

        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        id = self.id

        message = self.message

        name = self.name

        team_id = self.team_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if api_key is not UNSET:
            field_dict["api_key"] = api_key
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if id is not UNSET:
            field_dict["id"] = id
        if message is not UNSET:
            field_dict["message"] = message
        if name is not UNSET:
            field_dict["name"] = name
        if team_id is not UNSET:
            field_dict["team_id"] = team_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        api_key = d.pop("api_key", UNSET)

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

        id = d.pop("id", UNSET)

        message = d.pop("message", UNSET)

        name = d.pop("name", UNSET)

        team_id = d.pop("team_id", UNSET)

        create_api_key_response = cls(
            api_key=api_key,
            expires_at=expires_at,
            id=id,
            message=message,
            name=name,
            team_id=team_id,
        )

        create_api_key_response.additional_properties = d
        return create_api_key_response

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
