import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.user_status import UserStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        created_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        email (Union[Unset, str]):  Example: john@example.com.
        full_name (Union[None, Unset, str]):  Example: John Doe.
        id (Union[Unset, int]):  Example: 1.
        last_login_at (Union[None, Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        roles (Union[Unset, list[str]]): User role list Example: ['user'].
        status (Union[Unset, UserStatus]):  Example: active.
        updated_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        username (Union[Unset, str]):  Example: john_doe.
    """

    created_at: Union[Unset, datetime.datetime] = UNSET
    email: Union[Unset, str] = UNSET
    full_name: Union[None, Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    last_login_at: Union[None, Unset, datetime.datetime] = UNSET
    roles: Union[Unset, list[str]] = UNSET
    status: Union[Unset, UserStatus] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        email = self.email

        full_name: Union[None, Unset, str]
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name

        id = self.id

        last_login_at: Union[None, Unset, str]
        if isinstance(self.last_login_at, Unset):
            last_login_at = UNSET
        elif isinstance(self.last_login_at, datetime.datetime):
            last_login_at = self.last_login_at.isoformat()
        else:
            last_login_at = self.last_login_at

        roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if email is not UNSET:
            field_dict["email"] = email
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if id is not UNSET:
            field_dict["id"] = id
        if last_login_at is not UNSET:
            field_dict["last_login_at"] = last_login_at
        if roles is not UNSET:
            field_dict["roles"] = roles
        if status is not UNSET:
            field_dict["status"] = status
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if username is not UNSET:
            field_dict["username"] = username

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

        email = d.pop("email", UNSET)

        def _parse_full_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))

        id = d.pop("id", UNSET)

        def _parse_last_login_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_login_at_type_0 = isoparse(data)

                return last_login_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_login_at = _parse_last_login_at(d.pop("last_login_at", UNSET))

        roles = cast(list[str], d.pop("roles", UNSET))

        _status = d.pop("status", UNSET)
        status: Union[Unset, UserStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = UserStatus(_status)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        username = d.pop("username", UNSET)

        user = cls(
            created_at=created_at,
            email=email,
            full_name=full_name,
            id=id,
            last_login_at=last_login_at,
            roles=roles,
            status=status,
            updated_at=updated_at,
            username=username,
        )

        user.additional_properties = d
        return user

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
