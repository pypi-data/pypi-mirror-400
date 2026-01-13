import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.node_state import NodeState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_gres import NodeGres


T = TypeVar("T", bound="Node")


@_attrs_define
class Node:
    """
    Attributes:
        cpus (Union[Unset, int]):  Example: 64.
        cpus_allocated (Union[Unset, int]):  Example: 32.
        cpus_idle (Union[Unset, int]):  Example: 32.
        features (Union[Unset, list[str]]):  Example: ['gpu', 'nvme'].
        gres (Union[Unset, NodeGres]): Generic Resources (GPU, etc.) Example: {'gpu': 4}.
        last_update (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        memory (Union[Unset, int]): Total memory in bytes Example: 137438953472.
        memory_allocated (Union[Unset, int]): Allocated memory in bytes Example: 68719476736.
        memory_free (Union[Unset, int]): Free memory in bytes Example: 68719476736.
        name (Union[Unset, str]):  Example: node001.
        partitions (Union[Unset, list[str]]):  Example: ['compute', 'gpu'].
        reason (Union[None, Unset, str]):  Example: Not responding.
        state (Union[Unset, NodeState]):  Example: IDLE.
    """

    cpus: Union[Unset, int] = UNSET
    cpus_allocated: Union[Unset, int] = UNSET
    cpus_idle: Union[Unset, int] = UNSET
    features: Union[Unset, list[str]] = UNSET
    gres: Union[Unset, "NodeGres"] = UNSET
    last_update: Union[Unset, datetime.datetime] = UNSET
    memory: Union[Unset, int] = UNSET
    memory_allocated: Union[Unset, int] = UNSET
    memory_free: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    partitions: Union[Unset, list[str]] = UNSET
    reason: Union[None, Unset, str] = UNSET
    state: Union[Unset, NodeState] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cpus = self.cpus

        cpus_allocated = self.cpus_allocated

        cpus_idle = self.cpus_idle

        features: Union[Unset, list[str]] = UNSET
        if not isinstance(self.features, Unset):
            features = self.features

        gres: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.gres, Unset):
            gres = self.gres.to_dict()

        last_update: Union[Unset, str] = UNSET
        if not isinstance(self.last_update, Unset):
            last_update = self.last_update.isoformat()

        memory = self.memory

        memory_allocated = self.memory_allocated

        memory_free = self.memory_free

        name = self.name

        partitions: Union[Unset, list[str]] = UNSET
        if not isinstance(self.partitions, Unset):
            partitions = self.partitions

        reason: Union[None, Unset, str]
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cpus is not UNSET:
            field_dict["cpus"] = cpus
        if cpus_allocated is not UNSET:
            field_dict["cpus_allocated"] = cpus_allocated
        if cpus_idle is not UNSET:
            field_dict["cpus_idle"] = cpus_idle
        if features is not UNSET:
            field_dict["features"] = features
        if gres is not UNSET:
            field_dict["gres"] = gres
        if last_update is not UNSET:
            field_dict["last_update"] = last_update
        if memory is not UNSET:
            field_dict["memory"] = memory
        if memory_allocated is not UNSET:
            field_dict["memory_allocated"] = memory_allocated
        if memory_free is not UNSET:
            field_dict["memory_free"] = memory_free
        if name is not UNSET:
            field_dict["name"] = name
        if partitions is not UNSET:
            field_dict["partitions"] = partitions
        if reason is not UNSET:
            field_dict["reason"] = reason
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.node_gres import NodeGres

        d = dict(src_dict)
        cpus = d.pop("cpus", UNSET)

        cpus_allocated = d.pop("cpus_allocated", UNSET)

        cpus_idle = d.pop("cpus_idle", UNSET)

        features = cast(list[str], d.pop("features", UNSET))

        _gres = d.pop("gres", UNSET)
        gres: Union[Unset, NodeGres]
        if isinstance(_gres, Unset):
            gres = UNSET
        else:
            gres = NodeGres.from_dict(_gres)

        _last_update = d.pop("last_update", UNSET)
        last_update: Union[Unset, datetime.datetime]
        if isinstance(_last_update, Unset):
            last_update = UNSET
        else:
            last_update = isoparse(_last_update)

        memory = d.pop("memory", UNSET)

        memory_allocated = d.pop("memory_allocated", UNSET)

        memory_free = d.pop("memory_free", UNSET)

        name = d.pop("name", UNSET)

        partitions = cast(list[str], d.pop("partitions", UNSET))

        def _parse_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        reason = _parse_reason(d.pop("reason", UNSET))

        _state = d.pop("state", UNSET)
        state: Union[Unset, NodeState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = NodeState(_state)

        node = cls(
            cpus=cpus,
            cpus_allocated=cpus_allocated,
            cpus_idle=cpus_idle,
            features=features,
            gres=gres,
            last_update=last_update,
            memory=memory,
            memory_allocated=memory_allocated,
            memory_free=memory_free,
            name=name,
            partitions=partitions,
            reason=reason,
            state=state,
        )

        node.additional_properties = d
        return node

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
