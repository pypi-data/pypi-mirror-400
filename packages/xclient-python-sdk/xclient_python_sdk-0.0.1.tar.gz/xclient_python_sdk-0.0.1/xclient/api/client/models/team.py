import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.team_quota_type_0 import TeamQuotaType0


T = TypeVar("T", bound="Team")


@_attrs_define
class Team:
    """
    Attributes:
        created_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        description (Union[None, Unset, str]):  Example: Research and Development Team.
        id (Union[Unset, int]):  Example: 1.
        name (Union[Unset, str]):  Example: research-team.
        owner_id (Union[Unset, int]):  Example: 1.
        quota (Union['TeamQuotaType0', None, Unset]): Quota information (JSON format) Example: {'cpu': 100, 'gpu': 10,
            'memory': '200GB'}.
        updated_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
    """

    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[None, Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    owner_id: Union[Unset, int] = UNSET
    quota: Union["TeamQuotaType0", None, Unset] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.team_quota_type_0 import TeamQuotaType0

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        id = self.id

        name = self.name

        owner_id = self.owner_id

        quota: Union[None, Unset, dict[str, Any]]
        if isinstance(self.quota, Unset):
            quota = UNSET
        elif isinstance(self.quota, TeamQuotaType0):
            quota = self.quota.to_dict()
        else:
            quota = self.quota

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
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if owner_id is not UNSET:
            field_dict["owner_id"] = owner_id
        if quota is not UNSET:
            field_dict["quota"] = quota
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team_quota_type_0 import TeamQuotaType0

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

        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        owner_id = d.pop("owner_id", UNSET)

        def _parse_quota(data: object) -> Union["TeamQuotaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                quota_type_0 = TeamQuotaType0.from_dict(data)

                return quota_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TeamQuotaType0", None, Unset], data)

        quota = _parse_quota(d.pop("quota", UNSET))

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        team = cls(
            created_at=created_at,
            description=description,
            id=id,
            name=name,
            owner_id=owner_id,
            quota=quota,
            updated_at=updated_at,
        )

        team.additional_properties = d
        return team

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
