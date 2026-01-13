import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.api_key_status import APIKeyStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="APIKey")


@_attrs_define
class APIKey:
    """
    Attributes:
        created_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        description (Union[None, Unset, str]):  Example: API key for production environment.
        expires_at (Union[None, Unset, datetime.datetime]):  Example: 2025-12-31T23:59:59Z.
        id (Union[Unset, int]):  Example: 1.
        last_used_at (Union[None, Unset, datetime.datetime]):  Example: 2024-01-15T10:30:00Z.
        masked_key (Union[Unset, str]): Masked API key for display (shows first 8 and last 4 characters) Example:
            xck_1234••••••••••••••••••••abcd.
        name (Union[Unset, str]):  Example: Production API Key.
        status (Union[Unset, APIKeyStatus]):  Example: active.
        team_id (Union[Unset, int]):  Example: 1.
        updated_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
    """

    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[None, Unset, str] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    id: Union[Unset, int] = UNSET
    last_used_at: Union[None, Unset, datetime.datetime] = UNSET
    masked_key: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    status: Union[Unset, APIKeyStatus] = UNSET
    team_id: Union[Unset, int] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

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

        id = self.id

        last_used_at: Union[None, Unset, str]
        if isinstance(self.last_used_at, Unset):
            last_used_at = UNSET
        elif isinstance(self.last_used_at, datetime.datetime):
            last_used_at = self.last_used_at.isoformat()
        else:
            last_used_at = self.last_used_at

        masked_key = self.masked_key

        name = self.name

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        team_id = self.team_id

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if id is not UNSET:
            field_dict["id"] = id
        if last_used_at is not UNSET:
            field_dict["last_used_at"] = last_used_at
        if masked_key is not UNSET:
            field_dict["masked_key"] = masked_key
        if name is not UNSET:
            field_dict["name"] = name
        if status is not UNSET:
            field_dict["status"] = status
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

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

        id = d.pop("id", UNSET)

        def _parse_last_used_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_used_at_type_0 = isoparse(data)

                return last_used_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_used_at = _parse_last_used_at(d.pop("last_used_at", UNSET))

        masked_key = d.pop("masked_key", UNSET)

        name = d.pop("name", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, APIKeyStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = APIKeyStatus(_status)

        team_id = d.pop("team_id", UNSET)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        api_key = cls(
            created_at=created_at,
            description=description,
            expires_at=expires_at,
            id=id,
            last_used_at=last_used_at,
            masked_key=masked_key,
            name=name,
            status=status,
            team_id=team_id,
            updated_at=updated_at,
        )

        api_key.additional_properties = d
        return api_key

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
