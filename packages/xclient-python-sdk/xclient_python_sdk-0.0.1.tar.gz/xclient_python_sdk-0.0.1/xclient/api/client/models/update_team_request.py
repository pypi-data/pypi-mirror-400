from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_team_request_quota_type_0 import UpdateTeamRequestQuotaType0


T = TypeVar("T", bound="UpdateTeamRequest")


@_attrs_define
class UpdateTeamRequest:
    """
    Attributes:
        description (Union[None, Unset, str]):  Example: Research and Development Team.
        name (Union[Unset, str]):  Example: research-team.
        quota (Union['UpdateTeamRequestQuotaType0', None, Unset]):  Example: {'cpu': 100, 'gpu': 10, 'memory': '200GB'}.
    """

    description: Union[None, Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    quota: Union["UpdateTeamRequestQuotaType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.update_team_request_quota_type_0 import UpdateTeamRequestQuotaType0

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        name = self.name

        quota: Union[None, Unset, dict[str, Any]]
        if isinstance(self.quota, Unset):
            quota = UNSET
        elif isinstance(self.quota, UpdateTeamRequestQuotaType0):
            quota = self.quota.to_dict()
        else:
            quota = self.quota

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name
        if quota is not UNSET:
            field_dict["quota"] = quota

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_team_request_quota_type_0 import UpdateTeamRequestQuotaType0

        d = dict(src_dict)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        name = d.pop("name", UNSET)

        def _parse_quota(data: object) -> Union["UpdateTeamRequestQuotaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                quota_type_0 = UpdateTeamRequestQuotaType0.from_dict(data)

                return quota_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UpdateTeamRequestQuotaType0", None, Unset], data)

        quota = _parse_quota(d.pop("quota", UNSET))

        update_team_request = cls(
            description=description,
            name=name,
            quota=quota,
        )

        update_team_request.additional_properties = d
        return update_team_request

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
