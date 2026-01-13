from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user import User


T = TypeVar("T", bound="UserListResponse")


@_attrs_define
class UserListResponse:
    """
    Attributes:
        page (Union[Unset, int]):  Example: 1.
        page_size (Union[Unset, int]):  Example: 20.
        total (Union[Unset, int]):  Example: 50.
        users (Union[Unset, list['User']]):
    """

    page: Union[Unset, int] = UNSET
    page_size: Union[Unset, int] = UNSET
    total: Union[Unset, int] = UNSET
    users: Union[Unset, list["User"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        page = self.page

        page_size = self.page_size

        total = self.total

        users: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.users, Unset):
            users = []
            for users_item_data in self.users:
                users_item = users_item_data.to_dict()
                users.append(users_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if page is not UNSET:
            field_dict["page"] = page
        if page_size is not UNSET:
            field_dict["page_size"] = page_size
        if total is not UNSET:
            field_dict["total"] = total
        if users is not UNSET:
            field_dict["users"] = users

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user import User

        d = dict(src_dict)
        page = d.pop("page", UNSET)

        page_size = d.pop("page_size", UNSET)

        total = d.pop("total", UNSET)

        users = []
        _users = d.pop("users", UNSET)
        for users_item_data in _users or []:
            users_item = User.from_dict(users_item_data)

            users.append(users_item)

        user_list_response = cls(
            page=page,
            page_size=page_size,
            total=total,
            users=users,
        )

        user_list_response.additional_properties = d
        return user_list_response

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
