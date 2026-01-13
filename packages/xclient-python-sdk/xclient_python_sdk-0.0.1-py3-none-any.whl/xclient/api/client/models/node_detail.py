import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.node_detail_state import NodeDetailState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_detail_gres import NodeDetailGres
    from ..models.node_detail_gres_used import NodeDetailGresUsed
    from ..models.node_detail_tres import NodeDetailTres
    from ..models.node_detail_tres_used import NodeDetailTresUsed


T = TypeVar("T", bound="NodeDetail")


@_attrs_define
class NodeDetail:
    """
    Attributes:
        address (Union[None, Unset, str]):  Example: 192.168.1.100.
        architecture (Union[None, Unset, str]):  Example: x86_64.
        boards (Union[None, Unset, int]):  Example: 1.
        boot_time (Union[None, Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        burstbuffer_network_address (Union[None, Unset, str]):
        comment (Union[None, Unset, str]):
        cores (Union[None, Unset, int]):  Example: 32.
        cpu_binding (Union[None, Unset, int]):
        cpu_load (Union[None, Unset, int]):  Example: 1.
        cpus (Union[Unset, int]):  Example: 64.
        cpus_allocated (Union[Unset, int]):  Example: 32.
        cpus_idle (Union[Unset, int]):  Example: 32.
        extra (Union[None, Unset, str]):
        features (Union[Unset, list[str]]):  Example: ['gpu', 'nvme'].
        gres (Union[Unset, NodeDetailGres]): Generic Resources (GPU, etc.) Example: {'gpu': 4}.
        gres_drained (Union[None, Unset, str]):  Example: N/A.
        gres_used (Union[Unset, NodeDetailGresUsed]): Generic Resources Used Example: {'gpu': 2}.
        hostname (Union[None, Unset, str]):  Example: node001.
        last_update (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        mcs_label (Union[None, Unset, str]):
        memory (Union[Unset, int]): Total memory in bytes Example: 137438953472.
        memory_allocated (Union[Unset, int]): Allocated memory in bytes Example: 68719476736.
        memory_free (Union[Unset, int]): Free memory in bytes Example: 68719476736.
        name (Union[Unset, str]):  Example: node001.
        next_state_after_reboot (Union[None, Unset, str]):  Example: invalid.
        next_state_after_reboot_flags (Union[None, Unset, list[str]]):
        operating_system (Union[None, Unset, str]):  Example: Linux 5.15.0.
        owner (Union[None, Unset, str]):
        partitions (Union[Unset, list[str]]):  Example: ['compute', 'gpu'].
        port (Union[None, Unset, int]):  Example: 6818.
        reason (Union[None, Unset, str]):  Example: Not responding.
        reason_changed_at (Union[None, Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        reason_set_by_user (Union[None, Unset, str]):  Example: admin.
        slurmd_start_time (Union[None, Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        slurmd_version (Union[None, Unset, str]):  Example: 21.08.5.
        sockets (Union[None, Unset, int]):  Example: 2.
        state (Union[Unset, NodeDetailState]):  Example: IDLE.
        state_flags (Union[None, Unset, list[str]]):
        temporary_disk (Union[None, Unset, int]): Temporary disk space in bytes Example: 107374182400.
        threads (Union[None, Unset, int]):  Example: 16.
        tres (Union[Unset, NodeDetailTres]): Total Resource (CPU, Memory, GPU, etc.) Example: {'cpu': 64, 'gpu': 4,
            'mem': 137438953472}.
        tres_used (Union[Unset, NodeDetailTresUsed]): Total Resource Used Example: {'cpu': 32, 'gpu': 2, 'mem':
            68719476736}.
        tres_weighted (Union[None, Unset, float]):  Example: 0.5.
        weight (Union[None, Unset, int]):  Example: 1.
    """

    address: Union[None, Unset, str] = UNSET
    architecture: Union[None, Unset, str] = UNSET
    boards: Union[None, Unset, int] = UNSET
    boot_time: Union[None, Unset, datetime.datetime] = UNSET
    burstbuffer_network_address: Union[None, Unset, str] = UNSET
    comment: Union[None, Unset, str] = UNSET
    cores: Union[None, Unset, int] = UNSET
    cpu_binding: Union[None, Unset, int] = UNSET
    cpu_load: Union[None, Unset, int] = UNSET
    cpus: Union[Unset, int] = UNSET
    cpus_allocated: Union[Unset, int] = UNSET
    cpus_idle: Union[Unset, int] = UNSET
    extra: Union[None, Unset, str] = UNSET
    features: Union[Unset, list[str]] = UNSET
    gres: Union[Unset, "NodeDetailGres"] = UNSET
    gres_drained: Union[None, Unset, str] = UNSET
    gres_used: Union[Unset, "NodeDetailGresUsed"] = UNSET
    hostname: Union[None, Unset, str] = UNSET
    last_update: Union[Unset, datetime.datetime] = UNSET
    mcs_label: Union[None, Unset, str] = UNSET
    memory: Union[Unset, int] = UNSET
    memory_allocated: Union[Unset, int] = UNSET
    memory_free: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    next_state_after_reboot: Union[None, Unset, str] = UNSET
    next_state_after_reboot_flags: Union[None, Unset, list[str]] = UNSET
    operating_system: Union[None, Unset, str] = UNSET
    owner: Union[None, Unset, str] = UNSET
    partitions: Union[Unset, list[str]] = UNSET
    port: Union[None, Unset, int] = UNSET
    reason: Union[None, Unset, str] = UNSET
    reason_changed_at: Union[None, Unset, datetime.datetime] = UNSET
    reason_set_by_user: Union[None, Unset, str] = UNSET
    slurmd_start_time: Union[None, Unset, datetime.datetime] = UNSET
    slurmd_version: Union[None, Unset, str] = UNSET
    sockets: Union[None, Unset, int] = UNSET
    state: Union[Unset, NodeDetailState] = UNSET
    state_flags: Union[None, Unset, list[str]] = UNSET
    temporary_disk: Union[None, Unset, int] = UNSET
    threads: Union[None, Unset, int] = UNSET
    tres: Union[Unset, "NodeDetailTres"] = UNSET
    tres_used: Union[Unset, "NodeDetailTresUsed"] = UNSET
    tres_weighted: Union[None, Unset, float] = UNSET
    weight: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        address: Union[None, Unset, str]
        if isinstance(self.address, Unset):
            address = UNSET
        else:
            address = self.address

        architecture: Union[None, Unset, str]
        if isinstance(self.architecture, Unset):
            architecture = UNSET
        else:
            architecture = self.architecture

        boards: Union[None, Unset, int]
        if isinstance(self.boards, Unset):
            boards = UNSET
        else:
            boards = self.boards

        boot_time: Union[None, Unset, str]
        if isinstance(self.boot_time, Unset):
            boot_time = UNSET
        elif isinstance(self.boot_time, datetime.datetime):
            boot_time = self.boot_time.isoformat()
        else:
            boot_time = self.boot_time

        burstbuffer_network_address: Union[None, Unset, str]
        if isinstance(self.burstbuffer_network_address, Unset):
            burstbuffer_network_address = UNSET
        else:
            burstbuffer_network_address = self.burstbuffer_network_address

        comment: Union[None, Unset, str]
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        cores: Union[None, Unset, int]
        if isinstance(self.cores, Unset):
            cores = UNSET
        else:
            cores = self.cores

        cpu_binding: Union[None, Unset, int]
        if isinstance(self.cpu_binding, Unset):
            cpu_binding = UNSET
        else:
            cpu_binding = self.cpu_binding

        cpu_load: Union[None, Unset, int]
        if isinstance(self.cpu_load, Unset):
            cpu_load = UNSET
        else:
            cpu_load = self.cpu_load

        cpus = self.cpus

        cpus_allocated = self.cpus_allocated

        cpus_idle = self.cpus_idle

        extra: Union[None, Unset, str]
        if isinstance(self.extra, Unset):
            extra = UNSET
        else:
            extra = self.extra

        features: Union[Unset, list[str]] = UNSET
        if not isinstance(self.features, Unset):
            features = self.features

        gres: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.gres, Unset):
            gres = self.gres.to_dict()

        gres_drained: Union[None, Unset, str]
        if isinstance(self.gres_drained, Unset):
            gres_drained = UNSET
        else:
            gres_drained = self.gres_drained

        gres_used: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.gres_used, Unset):
            gres_used = self.gres_used.to_dict()

        hostname: Union[None, Unset, str]
        if isinstance(self.hostname, Unset):
            hostname = UNSET
        else:
            hostname = self.hostname

        last_update: Union[Unset, str] = UNSET
        if not isinstance(self.last_update, Unset):
            last_update = self.last_update.isoformat()

        mcs_label: Union[None, Unset, str]
        if isinstance(self.mcs_label, Unset):
            mcs_label = UNSET
        else:
            mcs_label = self.mcs_label

        memory = self.memory

        memory_allocated = self.memory_allocated

        memory_free = self.memory_free

        name = self.name

        next_state_after_reboot: Union[None, Unset, str]
        if isinstance(self.next_state_after_reboot, Unset):
            next_state_after_reboot = UNSET
        else:
            next_state_after_reboot = self.next_state_after_reboot

        next_state_after_reboot_flags: Union[None, Unset, list[str]]
        if isinstance(self.next_state_after_reboot_flags, Unset):
            next_state_after_reboot_flags = UNSET
        elif isinstance(self.next_state_after_reboot_flags, list):
            next_state_after_reboot_flags = self.next_state_after_reboot_flags

        else:
            next_state_after_reboot_flags = self.next_state_after_reboot_flags

        operating_system: Union[None, Unset, str]
        if isinstance(self.operating_system, Unset):
            operating_system = UNSET
        else:
            operating_system = self.operating_system

        owner: Union[None, Unset, str]
        if isinstance(self.owner, Unset):
            owner = UNSET
        else:
            owner = self.owner

        partitions: Union[Unset, list[str]] = UNSET
        if not isinstance(self.partitions, Unset):
            partitions = self.partitions

        port: Union[None, Unset, int]
        if isinstance(self.port, Unset):
            port = UNSET
        else:
            port = self.port

        reason: Union[None, Unset, str]
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        reason_changed_at: Union[None, Unset, str]
        if isinstance(self.reason_changed_at, Unset):
            reason_changed_at = UNSET
        elif isinstance(self.reason_changed_at, datetime.datetime):
            reason_changed_at = self.reason_changed_at.isoformat()
        else:
            reason_changed_at = self.reason_changed_at

        reason_set_by_user: Union[None, Unset, str]
        if isinstance(self.reason_set_by_user, Unset):
            reason_set_by_user = UNSET
        else:
            reason_set_by_user = self.reason_set_by_user

        slurmd_start_time: Union[None, Unset, str]
        if isinstance(self.slurmd_start_time, Unset):
            slurmd_start_time = UNSET
        elif isinstance(self.slurmd_start_time, datetime.datetime):
            slurmd_start_time = self.slurmd_start_time.isoformat()
        else:
            slurmd_start_time = self.slurmd_start_time

        slurmd_version: Union[None, Unset, str]
        if isinstance(self.slurmd_version, Unset):
            slurmd_version = UNSET
        else:
            slurmd_version = self.slurmd_version

        sockets: Union[None, Unset, int]
        if isinstance(self.sockets, Unset):
            sockets = UNSET
        else:
            sockets = self.sockets

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        state_flags: Union[None, Unset, list[str]]
        if isinstance(self.state_flags, Unset):
            state_flags = UNSET
        elif isinstance(self.state_flags, list):
            state_flags = self.state_flags

        else:
            state_flags = self.state_flags

        temporary_disk: Union[None, Unset, int]
        if isinstance(self.temporary_disk, Unset):
            temporary_disk = UNSET
        else:
            temporary_disk = self.temporary_disk

        threads: Union[None, Unset, int]
        if isinstance(self.threads, Unset):
            threads = UNSET
        else:
            threads = self.threads

        tres: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tres, Unset):
            tres = self.tres.to_dict()

        tres_used: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tres_used, Unset):
            tres_used = self.tres_used.to_dict()

        tres_weighted: Union[None, Unset, float]
        if isinstance(self.tres_weighted, Unset):
            tres_weighted = UNSET
        else:
            tres_weighted = self.tres_weighted

        weight: Union[None, Unset, int]
        if isinstance(self.weight, Unset):
            weight = UNSET
        else:
            weight = self.weight

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if address is not UNSET:
            field_dict["address"] = address
        if architecture is not UNSET:
            field_dict["architecture"] = architecture
        if boards is not UNSET:
            field_dict["boards"] = boards
        if boot_time is not UNSET:
            field_dict["boot_time"] = boot_time
        if burstbuffer_network_address is not UNSET:
            field_dict["burstbuffer_network_address"] = burstbuffer_network_address
        if comment is not UNSET:
            field_dict["comment"] = comment
        if cores is not UNSET:
            field_dict["cores"] = cores
        if cpu_binding is not UNSET:
            field_dict["cpu_binding"] = cpu_binding
        if cpu_load is not UNSET:
            field_dict["cpu_load"] = cpu_load
        if cpus is not UNSET:
            field_dict["cpus"] = cpus
        if cpus_allocated is not UNSET:
            field_dict["cpus_allocated"] = cpus_allocated
        if cpus_idle is not UNSET:
            field_dict["cpus_idle"] = cpus_idle
        if extra is not UNSET:
            field_dict["extra"] = extra
        if features is not UNSET:
            field_dict["features"] = features
        if gres is not UNSET:
            field_dict["gres"] = gres
        if gres_drained is not UNSET:
            field_dict["gres_drained"] = gres_drained
        if gres_used is not UNSET:
            field_dict["gres_used"] = gres_used
        if hostname is not UNSET:
            field_dict["hostname"] = hostname
        if last_update is not UNSET:
            field_dict["last_update"] = last_update
        if mcs_label is not UNSET:
            field_dict["mcs_label"] = mcs_label
        if memory is not UNSET:
            field_dict["memory"] = memory
        if memory_allocated is not UNSET:
            field_dict["memory_allocated"] = memory_allocated
        if memory_free is not UNSET:
            field_dict["memory_free"] = memory_free
        if name is not UNSET:
            field_dict["name"] = name
        if next_state_after_reboot is not UNSET:
            field_dict["next_state_after_reboot"] = next_state_after_reboot
        if next_state_after_reboot_flags is not UNSET:
            field_dict["next_state_after_reboot_flags"] = next_state_after_reboot_flags
        if operating_system is not UNSET:
            field_dict["operating_system"] = operating_system
        if owner is not UNSET:
            field_dict["owner"] = owner
        if partitions is not UNSET:
            field_dict["partitions"] = partitions
        if port is not UNSET:
            field_dict["port"] = port
        if reason is not UNSET:
            field_dict["reason"] = reason
        if reason_changed_at is not UNSET:
            field_dict["reason_changed_at"] = reason_changed_at
        if reason_set_by_user is not UNSET:
            field_dict["reason_set_by_user"] = reason_set_by_user
        if slurmd_start_time is not UNSET:
            field_dict["slurmd_start_time"] = slurmd_start_time
        if slurmd_version is not UNSET:
            field_dict["slurmd_version"] = slurmd_version
        if sockets is not UNSET:
            field_dict["sockets"] = sockets
        if state is not UNSET:
            field_dict["state"] = state
        if state_flags is not UNSET:
            field_dict["state_flags"] = state_flags
        if temporary_disk is not UNSET:
            field_dict["temporary_disk"] = temporary_disk
        if threads is not UNSET:
            field_dict["threads"] = threads
        if tres is not UNSET:
            field_dict["tres"] = tres
        if tres_used is not UNSET:
            field_dict["tres_used"] = tres_used
        if tres_weighted is not UNSET:
            field_dict["tres_weighted"] = tres_weighted
        if weight is not UNSET:
            field_dict["weight"] = weight

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.node_detail_gres import NodeDetailGres
        from ..models.node_detail_gres_used import NodeDetailGresUsed
        from ..models.node_detail_tres import NodeDetailTres
        from ..models.node_detail_tres_used import NodeDetailTresUsed

        d = dict(src_dict)

        def _parse_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        address = _parse_address(d.pop("address", UNSET))

        def _parse_architecture(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        architecture = _parse_architecture(d.pop("architecture", UNSET))

        def _parse_boards(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        boards = _parse_boards(d.pop("boards", UNSET))

        def _parse_boot_time(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                boot_time_type_0 = isoparse(data)

                return boot_time_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        boot_time = _parse_boot_time(d.pop("boot_time", UNSET))

        def _parse_burstbuffer_network_address(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        burstbuffer_network_address = _parse_burstbuffer_network_address(d.pop("burstbuffer_network_address", UNSET))

        def _parse_comment(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        comment = _parse_comment(d.pop("comment", UNSET))

        def _parse_cores(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        cores = _parse_cores(d.pop("cores", UNSET))

        def _parse_cpu_binding(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        cpu_binding = _parse_cpu_binding(d.pop("cpu_binding", UNSET))

        def _parse_cpu_load(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        cpu_load = _parse_cpu_load(d.pop("cpu_load", UNSET))

        cpus = d.pop("cpus", UNSET)

        cpus_allocated = d.pop("cpus_allocated", UNSET)

        cpus_idle = d.pop("cpus_idle", UNSET)

        def _parse_extra(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        extra = _parse_extra(d.pop("extra", UNSET))

        features = cast(list[str], d.pop("features", UNSET))

        _gres = d.pop("gres", UNSET)
        gres: Union[Unset, NodeDetailGres]
        if isinstance(_gres, Unset):
            gres = UNSET
        else:
            gres = NodeDetailGres.from_dict(_gres)

        def _parse_gres_drained(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        gres_drained = _parse_gres_drained(d.pop("gres_drained", UNSET))

        _gres_used = d.pop("gres_used", UNSET)
        gres_used: Union[Unset, NodeDetailGresUsed]
        if isinstance(_gres_used, Unset):
            gres_used = UNSET
        else:
            gres_used = NodeDetailGresUsed.from_dict(_gres_used)

        def _parse_hostname(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        hostname = _parse_hostname(d.pop("hostname", UNSET))

        _last_update = d.pop("last_update", UNSET)
        last_update: Union[Unset, datetime.datetime]
        if isinstance(_last_update, Unset):
            last_update = UNSET
        else:
            last_update = isoparse(_last_update)

        def _parse_mcs_label(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        mcs_label = _parse_mcs_label(d.pop("mcs_label", UNSET))

        memory = d.pop("memory", UNSET)

        memory_allocated = d.pop("memory_allocated", UNSET)

        memory_free = d.pop("memory_free", UNSET)

        name = d.pop("name", UNSET)

        def _parse_next_state_after_reboot(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        next_state_after_reboot = _parse_next_state_after_reboot(d.pop("next_state_after_reboot", UNSET))

        def _parse_next_state_after_reboot_flags(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                next_state_after_reboot_flags_type_0 = cast(list[str], data)

                return next_state_after_reboot_flags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        next_state_after_reboot_flags = _parse_next_state_after_reboot_flags(
            d.pop("next_state_after_reboot_flags", UNSET)
        )

        def _parse_operating_system(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        operating_system = _parse_operating_system(d.pop("operating_system", UNSET))

        def _parse_owner(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        owner = _parse_owner(d.pop("owner", UNSET))

        partitions = cast(list[str], d.pop("partitions", UNSET))

        def _parse_port(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        port = _parse_port(d.pop("port", UNSET))

        def _parse_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        reason = _parse_reason(d.pop("reason", UNSET))

        def _parse_reason_changed_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reason_changed_at_type_0 = isoparse(data)

                return reason_changed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        reason_changed_at = _parse_reason_changed_at(d.pop("reason_changed_at", UNSET))

        def _parse_reason_set_by_user(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        reason_set_by_user = _parse_reason_set_by_user(d.pop("reason_set_by_user", UNSET))

        def _parse_slurmd_start_time(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                slurmd_start_time_type_0 = isoparse(data)

                return slurmd_start_time_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        slurmd_start_time = _parse_slurmd_start_time(d.pop("slurmd_start_time", UNSET))

        def _parse_slurmd_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        slurmd_version = _parse_slurmd_version(d.pop("slurmd_version", UNSET))

        def _parse_sockets(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        sockets = _parse_sockets(d.pop("sockets", UNSET))

        _state = d.pop("state", UNSET)
        state: Union[Unset, NodeDetailState]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = NodeDetailState(_state)

        def _parse_state_flags(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                state_flags_type_0 = cast(list[str], data)

                return state_flags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        state_flags = _parse_state_flags(d.pop("state_flags", UNSET))

        def _parse_temporary_disk(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        temporary_disk = _parse_temporary_disk(d.pop("temporary_disk", UNSET))

        def _parse_threads(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        threads = _parse_threads(d.pop("threads", UNSET))

        _tres = d.pop("tres", UNSET)
        tres: Union[Unset, NodeDetailTres]
        if isinstance(_tres, Unset):
            tres = UNSET
        else:
            tres = NodeDetailTres.from_dict(_tres)

        _tres_used = d.pop("tres_used", UNSET)
        tres_used: Union[Unset, NodeDetailTresUsed]
        if isinstance(_tres_used, Unset):
            tres_used = UNSET
        else:
            tres_used = NodeDetailTresUsed.from_dict(_tres_used)

        def _parse_tres_weighted(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        tres_weighted = _parse_tres_weighted(d.pop("tres_weighted", UNSET))

        def _parse_weight(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        weight = _parse_weight(d.pop("weight", UNSET))

        node_detail = cls(
            address=address,
            architecture=architecture,
            boards=boards,
            boot_time=boot_time,
            burstbuffer_network_address=burstbuffer_network_address,
            comment=comment,
            cores=cores,
            cpu_binding=cpu_binding,
            cpu_load=cpu_load,
            cpus=cpus,
            cpus_allocated=cpus_allocated,
            cpus_idle=cpus_idle,
            extra=extra,
            features=features,
            gres=gres,
            gres_drained=gres_drained,
            gres_used=gres_used,
            hostname=hostname,
            last_update=last_update,
            mcs_label=mcs_label,
            memory=memory,
            memory_allocated=memory_allocated,
            memory_free=memory_free,
            name=name,
            next_state_after_reboot=next_state_after_reboot,
            next_state_after_reboot_flags=next_state_after_reboot_flags,
            operating_system=operating_system,
            owner=owner,
            partitions=partitions,
            port=port,
            reason=reason,
            reason_changed_at=reason_changed_at,
            reason_set_by_user=reason_set_by_user,
            slurmd_start_time=slurmd_start_time,
            slurmd_version=slurmd_version,
            sockets=sockets,
            state=state,
            state_flags=state_flags,
            temporary_disk=temporary_disk,
            threads=threads,
            tres=tres,
            tres_used=tres_used,
            tres_weighted=tres_weighted,
            weight=weight,
        )

        node_detail.additional_properties = d
        return node_detail

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
