from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.create_team_request_quota import CreateTeamRequestQuota


T = TypeVar("T", bound="CreateTeamRequest")


@_attrs_define
class CreateTeamRequest:
    """
    Attributes:
        name (str):  Example: research-team.
        description (Union[Unset, str]):  Example: Research and Development Team.
        quota (Union[Unset, CreateTeamRequestQuota]):  Example: {'cpu': 100, 'gpu': 10, 'memory': '200GB'}.
    """

    name: str
    description: Union[Unset, str] = UNSET
    quota: Union[Unset, "CreateTeamRequestQuota"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        quota: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.quota, Unset):
            quota = self.quota.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if quota is not UNSET:
            field_dict["quota"] = quota

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_team_request_quota import CreateTeamRequestQuota

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        _quota = d.pop("quota", UNSET)
        quota: Union[Unset, CreateTeamRequestQuota]
        if isinstance(_quota, Unset):
            quota = UNSET
        else:
            quota = CreateTeamRequestQuota.from_dict(_quota)

        create_team_request = cls(
            name=name,
            description=description,
            quota=quota,
        )

        create_team_request.additional_properties = d
        return create_team_request

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
