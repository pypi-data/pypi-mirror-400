from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LoginResponse")


@_attrs_define
class LoginResponse:
    """
    Attributes:
        email (Union[Unset, str]):  Example: john@example.com.
        roles (Union[Unset, list[str]]):  Example: ['user'].
        token (Union[Unset, str]): JWT authentication token Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....
        user_id (Union[Unset, int]):  Example: 1.
        username (Union[Unset, str]):  Example: john_doe.
    """

    email: Union[Unset, str] = UNSET
    roles: Union[Unset, list[str]] = UNSET
    token: Union[Unset, str] = UNSET
    user_id: Union[Unset, int] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        roles: Union[Unset, list[str]] = UNSET
        if not isinstance(self.roles, Unset):
            roles = self.roles

        token = self.token

        user_id = self.user_id

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if roles is not UNSET:
            field_dict["roles"] = roles
        if token is not UNSET:
            field_dict["token"] = token
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email", UNSET)

        roles = cast(list[str], d.pop("roles", UNSET))

        token = d.pop("token", UNSET)

        user_id = d.pop("user_id", UNSET)

        username = d.pop("username", UNSET)

        login_response = cls(
            email=email,
            roles=roles,
            token=token,
            user_id=user_id,
            username=username,
        )

        login_response.additional_properties = d
        return login_response

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
