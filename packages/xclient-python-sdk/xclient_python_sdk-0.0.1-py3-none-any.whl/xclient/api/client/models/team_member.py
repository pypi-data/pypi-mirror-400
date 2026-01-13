import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.team_member_role import TeamMemberRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="TeamMember")


@_attrs_define
class TeamMember:
    """
    Attributes:
        email (Union[Unset, str]):  Example: john@example.com.
        is_active (Union[Unset, bool]):  Example: True.
        joined_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        role (Union[Unset, TeamMemberRole]):  Example: member.
        user_id (Union[Unset, int]):  Example: 1.
        username (Union[Unset, str]):  Example: john_doe.
    """

    email: Union[Unset, str] = UNSET
    is_active: Union[Unset, bool] = UNSET
    joined_at: Union[Unset, datetime.datetime] = UNSET
    role: Union[Unset, TeamMemberRole] = UNSET
    user_id: Union[Unset, int] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        is_active = self.is_active

        joined_at: Union[Unset, str] = UNSET
        if not isinstance(self.joined_at, Unset):
            joined_at = self.joined_at.isoformat()

        role: Union[Unset, str] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        user_id = self.user_id

        username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if email is not UNSET:
            field_dict["email"] = email
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if joined_at is not UNSET:
            field_dict["joined_at"] = joined_at
        if role is not UNSET:
            field_dict["role"] = role
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email", UNSET)

        is_active = d.pop("is_active", UNSET)

        _joined_at = d.pop("joined_at", UNSET)
        joined_at: Union[Unset, datetime.datetime]
        if isinstance(_joined_at, Unset):
            joined_at = UNSET
        else:
            joined_at = isoparse(_joined_at)

        _role = d.pop("role", UNSET)
        role: Union[Unset, TeamMemberRole]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = TeamMemberRole(_role)

        user_id = d.pop("user_id", UNSET)

        username = d.pop("username", UNSET)

        team_member = cls(
            email=email,
            is_active=is_active,
            joined_at=joined_at,
            role=role,
            user_id=user_id,
            username=username,
        )

        team_member.additional_properties = d
        return team_member

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
