from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.user_status import UserStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateUserRequest")


@_attrs_define
class CreateUserRequest:
    """
    Attributes:
        email (str):  Example: john@example.com.
        password (str):  Example: password123.
        username (str):  Example: john_doe.
        full_name (Union[Unset, str]):  Example: John Doe.
        status (Union[Unset, UserStatus]):  Example: active.
    """

    email: str
    password: str
    username: str
    full_name: Union[Unset, str] = UNSET
    status: Union[Unset, UserStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        password = self.password

        username = self.username

        full_name = self.full_name

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "password": password,
                "username": username,
            }
        )
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        password = d.pop("password")

        username = d.pop("username")

        full_name = d.pop("full_name", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, UserStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = UserStatus(_status)

        create_user_request = cls(
            email=email,
            password=password,
            username=username,
            full_name=full_name,
            status=status,
        )

        create_user_request.additional_properties = d
        return create_user_request

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
