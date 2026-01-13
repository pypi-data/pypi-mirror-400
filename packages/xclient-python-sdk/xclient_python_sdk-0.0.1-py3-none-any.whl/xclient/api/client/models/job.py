import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.job_status import JobStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_alloc_tres_type_0 import JobAllocTresType0
    from ..models.job_gres_detail_type_0_item import JobGresDetailType0Item
    from ..models.job_job_resources_type_0 import JobJobResourcesType0
    from ..models.job_resources_type_0 import JobResourcesType0


T = TypeVar("T", bound="Job")


@_attrs_define
class Job:
    """
    Attributes:
        account (Union[None, Unset, str]):  Example: default.
        alloc_tres (Union['JobAllocTresType0', None, Unset]): Allocated TRES (Trackable Resources) Example: {'cpu': 4,
            'gpu': 1, 'mem': 8589934592}.
        array_job_id (Union[None, Unset, int]): Parent array job ID if this is an array task Example: 12345.
        array_task_id (Union[None, Unset, int]): Array task ID if this is an array task
        batch_host (Union[None, Unset, str]):  Example: xservice-slurm.
        cluster (Union[None, Unset, str]):  Example: single-node.
        cluster_id (Union[None, Unset, int]):  Example: 1.
        command (Union[None, Unset, str]):  Example: python train.py.
        comment (Union[None, Unset, str]):  Example: Training job.
        completed_at (Union[None, Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        cpus (Union[None, Unset, int]):  Example: 4.
        created_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        current_working_directory (Union[None, Unset, str]):  Example: /.
        exit_code (Union[None, Unset, int]):
        flags (Union[None, Unset, list[str]]):  Example: ['JOB_CPUS_SET', 'JOB_WAS_RUNNING'].
        gres_detail (Union[None, Unset, list['JobGresDetailType0Item']]):
        group_id (Union[None, Unset, int]):  Example: 1003.
        id (Union[Unset, int]):  Example: 1.
        job_id (Union[Unset, str]): Slurm Job ID Example: 12345.
        job_resources (Union['JobJobResourcesType0', None, Unset]): Job resource allocation details Example:
            {'allocated_cpus': 2, 'allocated_hosts': 1, 'allocated_nodes': {'0': {'cores': {'0': 'unassigned'}, 'cpus': 2,
            'memory': 0, 'sockets': {'0': 'unassigned'}}}, 'nodes': 'xservice-slurm'}.
        memory (Union[None, Unset, int]): Memory in bytes Example: 8589934592.
        minimum_cpus_per_node (Union[None, Unset, int]):  Example: 2.
        minimum_tmp_disk_per_node (Union[None, Unset, int]):
        name (Union[Unset, str]):  Example: training-job.
        node_count (Union[None, Unset, int]):  Example: 1.
        nodes (Union[None, Unset, list[str]]):  Example: ['node1', 'node2'].
        partition (Union[None, Unset, str]):  Example: debug.
        priority (Union[None, Unset, int]):  Example: 4294901756.
        qos (Union[None, Unset, str]):  Example: normal.
        resources (Union['JobResourcesType0', None, Unset]): Resource requirements (JSON format) Example: {'cpu': 4,
            'gpu': 1, 'memory': '8GB'}.
        script (Union[None, Unset, str]):  Example: #!/bin/bash
            python train.py.
        standard_error (Union[None, Unset, str]):  Example: /tmp/%x-%j.err.
        standard_input (Union[None, Unset, str]):
        standard_output (Union[None, Unset, str]):  Example: /tmp/%x-%j.out.
        started_at (Union[None, Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        state_description (Union[None, Unset, str]):
        state_reason (Union[None, Unset, str]):  Example: None.
        status (Union[Unset, JobStatus]):  Example: pending.
        tasks (Union[None, Unset, int]):  Example: 1.
        team_id (Union[None, Unset, int]):  Example: 1.
        time_limit (Union[None, Unset, int]): Time limit in seconds Example: 3600.
        time_used (Union[None, Unset, int]): Time used in seconds Example: 1800.
        tres_alloc_str (Union[None, Unset, str]):  Example: cpu=2,node=1,billing=2.
        tres_req_str (Union[None, Unset, str]):  Example: cpu=2,mem=27600M,node=1,billing=2.
        updated_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        user_id (Union[Unset, int]):  Example: 1.
        user_name (Union[None, Unset, str]):  Example: root.
        work_dir (Union[None, Unset, str]):  Example: /home/user.
    """

    account: Union[None, Unset, str] = UNSET
    alloc_tres: Union["JobAllocTresType0", None, Unset] = UNSET
    array_job_id: Union[None, Unset, int] = UNSET
    array_task_id: Union[None, Unset, int] = UNSET
    batch_host: Union[None, Unset, str] = UNSET
    cluster: Union[None, Unset, str] = UNSET
    cluster_id: Union[None, Unset, int] = UNSET
    command: Union[None, Unset, str] = UNSET
    comment: Union[None, Unset, str] = UNSET
    completed_at: Union[None, Unset, datetime.datetime] = UNSET
    cpus: Union[None, Unset, int] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    current_working_directory: Union[None, Unset, str] = UNSET
    exit_code: Union[None, Unset, int] = UNSET
    flags: Union[None, Unset, list[str]] = UNSET
    gres_detail: Union[None, Unset, list["JobGresDetailType0Item"]] = UNSET
    group_id: Union[None, Unset, int] = UNSET
    id: Union[Unset, int] = UNSET
    job_id: Union[Unset, str] = UNSET
    job_resources: Union["JobJobResourcesType0", None, Unset] = UNSET
    memory: Union[None, Unset, int] = UNSET
    minimum_cpus_per_node: Union[None, Unset, int] = UNSET
    minimum_tmp_disk_per_node: Union[None, Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    node_count: Union[None, Unset, int] = UNSET
    nodes: Union[None, Unset, list[str]] = UNSET
    partition: Union[None, Unset, str] = UNSET
    priority: Union[None, Unset, int] = UNSET
    qos: Union[None, Unset, str] = UNSET
    resources: Union["JobResourcesType0", None, Unset] = UNSET
    script: Union[None, Unset, str] = UNSET
    standard_error: Union[None, Unset, str] = UNSET
    standard_input: Union[None, Unset, str] = UNSET
    standard_output: Union[None, Unset, str] = UNSET
    started_at: Union[None, Unset, datetime.datetime] = UNSET
    state_description: Union[None, Unset, str] = UNSET
    state_reason: Union[None, Unset, str] = UNSET
    status: Union[Unset, JobStatus] = UNSET
    tasks: Union[None, Unset, int] = UNSET
    team_id: Union[None, Unset, int] = UNSET
    time_limit: Union[None, Unset, int] = UNSET
    time_used: Union[None, Unset, int] = UNSET
    tres_alloc_str: Union[None, Unset, str] = UNSET
    tres_req_str: Union[None, Unset, str] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    user_id: Union[Unset, int] = UNSET
    user_name: Union[None, Unset, str] = UNSET
    work_dir: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.job_alloc_tres_type_0 import JobAllocTresType0
        from ..models.job_job_resources_type_0 import JobJobResourcesType0
        from ..models.job_resources_type_0 import JobResourcesType0

        account: Union[None, Unset, str]
        if isinstance(self.account, Unset):
            account = UNSET
        else:
            account = self.account

        alloc_tres: Union[None, Unset, dict[str, Any]]
        if isinstance(self.alloc_tres, Unset):
            alloc_tres = UNSET
        elif isinstance(self.alloc_tres, JobAllocTresType0):
            alloc_tres = self.alloc_tres.to_dict()
        else:
            alloc_tres = self.alloc_tres

        array_job_id: Union[None, Unset, int]
        if isinstance(self.array_job_id, Unset):
            array_job_id = UNSET
        else:
            array_job_id = self.array_job_id

        array_task_id: Union[None, Unset, int]
        if isinstance(self.array_task_id, Unset):
            array_task_id = UNSET
        else:
            array_task_id = self.array_task_id

        batch_host: Union[None, Unset, str]
        if isinstance(self.batch_host, Unset):
            batch_host = UNSET
        else:
            batch_host = self.batch_host

        cluster: Union[None, Unset, str]
        if isinstance(self.cluster, Unset):
            cluster = UNSET
        else:
            cluster = self.cluster

        cluster_id: Union[None, Unset, int]
        if isinstance(self.cluster_id, Unset):
            cluster_id = UNSET
        else:
            cluster_id = self.cluster_id

        command: Union[None, Unset, str]
        if isinstance(self.command, Unset):
            command = UNSET
        else:
            command = self.command

        comment: Union[None, Unset, str]
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        completed_at: Union[None, Unset, str]
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        elif isinstance(self.completed_at, datetime.datetime):
            completed_at = self.completed_at.isoformat()
        else:
            completed_at = self.completed_at

        cpus: Union[None, Unset, int]
        if isinstance(self.cpus, Unset):
            cpus = UNSET
        else:
            cpus = self.cpus

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        current_working_directory: Union[None, Unset, str]
        if isinstance(self.current_working_directory, Unset):
            current_working_directory = UNSET
        else:
            current_working_directory = self.current_working_directory

        exit_code: Union[None, Unset, int]
        if isinstance(self.exit_code, Unset):
            exit_code = UNSET
        else:
            exit_code = self.exit_code

        flags: Union[None, Unset, list[str]]
        if isinstance(self.flags, Unset):
            flags = UNSET
        elif isinstance(self.flags, list):
            flags = self.flags

        else:
            flags = self.flags

        gres_detail: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.gres_detail, Unset):
            gres_detail = UNSET
        elif isinstance(self.gres_detail, list):
            gres_detail = []
            for gres_detail_type_0_item_data in self.gres_detail:
                gres_detail_type_0_item = gres_detail_type_0_item_data.to_dict()
                gres_detail.append(gres_detail_type_0_item)

        else:
            gres_detail = self.gres_detail

        group_id: Union[None, Unset, int]
        if isinstance(self.group_id, Unset):
            group_id = UNSET
        else:
            group_id = self.group_id

        id = self.id

        job_id = self.job_id

        job_resources: Union[None, Unset, dict[str, Any]]
        if isinstance(self.job_resources, Unset):
            job_resources = UNSET
        elif isinstance(self.job_resources, JobJobResourcesType0):
            job_resources = self.job_resources.to_dict()
        else:
            job_resources = self.job_resources

        memory: Union[None, Unset, int]
        if isinstance(self.memory, Unset):
            memory = UNSET
        else:
            memory = self.memory

        minimum_cpus_per_node: Union[None, Unset, int]
        if isinstance(self.minimum_cpus_per_node, Unset):
            minimum_cpus_per_node = UNSET
        else:
            minimum_cpus_per_node = self.minimum_cpus_per_node

        minimum_tmp_disk_per_node: Union[None, Unset, int]
        if isinstance(self.minimum_tmp_disk_per_node, Unset):
            minimum_tmp_disk_per_node = UNSET
        else:
            minimum_tmp_disk_per_node = self.minimum_tmp_disk_per_node

        name = self.name

        node_count: Union[None, Unset, int]
        if isinstance(self.node_count, Unset):
            node_count = UNSET
        else:
            node_count = self.node_count

        nodes: Union[None, Unset, list[str]]
        if isinstance(self.nodes, Unset):
            nodes = UNSET
        elif isinstance(self.nodes, list):
            nodes = self.nodes

        else:
            nodes = self.nodes

        partition: Union[None, Unset, str]
        if isinstance(self.partition, Unset):
            partition = UNSET
        else:
            partition = self.partition

        priority: Union[None, Unset, int]
        if isinstance(self.priority, Unset):
            priority = UNSET
        else:
            priority = self.priority

        qos: Union[None, Unset, str]
        if isinstance(self.qos, Unset):
            qos = UNSET
        else:
            qos = self.qos

        resources: Union[None, Unset, dict[str, Any]]
        if isinstance(self.resources, Unset):
            resources = UNSET
        elif isinstance(self.resources, JobResourcesType0):
            resources = self.resources.to_dict()
        else:
            resources = self.resources

        script: Union[None, Unset, str]
        if isinstance(self.script, Unset):
            script = UNSET
        else:
            script = self.script

        standard_error: Union[None, Unset, str]
        if isinstance(self.standard_error, Unset):
            standard_error = UNSET
        else:
            standard_error = self.standard_error

        standard_input: Union[None, Unset, str]
        if isinstance(self.standard_input, Unset):
            standard_input = UNSET
        else:
            standard_input = self.standard_input

        standard_output: Union[None, Unset, str]
        if isinstance(self.standard_output, Unset):
            standard_output = UNSET
        else:
            standard_output = self.standard_output

        started_at: Union[None, Unset, str]
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        state_description: Union[None, Unset, str]
        if isinstance(self.state_description, Unset):
            state_description = UNSET
        else:
            state_description = self.state_description

        state_reason: Union[None, Unset, str]
        if isinstance(self.state_reason, Unset):
            state_reason = UNSET
        else:
            state_reason = self.state_reason

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        tasks: Union[None, Unset, int]
        if isinstance(self.tasks, Unset):
            tasks = UNSET
        else:
            tasks = self.tasks

        team_id: Union[None, Unset, int]
        if isinstance(self.team_id, Unset):
            team_id = UNSET
        else:
            team_id = self.team_id

        time_limit: Union[None, Unset, int]
        if isinstance(self.time_limit, Unset):
            time_limit = UNSET
        else:
            time_limit = self.time_limit

        time_used: Union[None, Unset, int]
        if isinstance(self.time_used, Unset):
            time_used = UNSET
        else:
            time_used = self.time_used

        tres_alloc_str: Union[None, Unset, str]
        if isinstance(self.tres_alloc_str, Unset):
            tres_alloc_str = UNSET
        else:
            tres_alloc_str = self.tres_alloc_str

        tres_req_str: Union[None, Unset, str]
        if isinstance(self.tres_req_str, Unset):
            tres_req_str = UNSET
        else:
            tres_req_str = self.tres_req_str

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        user_id = self.user_id

        user_name: Union[None, Unset, str]
        if isinstance(self.user_name, Unset):
            user_name = UNSET
        else:
            user_name = self.user_name

        work_dir: Union[None, Unset, str]
        if isinstance(self.work_dir, Unset):
            work_dir = UNSET
        else:
            work_dir = self.work_dir

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if account is not UNSET:
            field_dict["account"] = account
        if alloc_tres is not UNSET:
            field_dict["alloc_tres"] = alloc_tres
        if array_job_id is not UNSET:
            field_dict["array_job_id"] = array_job_id
        if array_task_id is not UNSET:
            field_dict["array_task_id"] = array_task_id
        if batch_host is not UNSET:
            field_dict["batch_host"] = batch_host
        if cluster is not UNSET:
            field_dict["cluster"] = cluster
        if cluster_id is not UNSET:
            field_dict["cluster_id"] = cluster_id
        if command is not UNSET:
            field_dict["command"] = command
        if comment is not UNSET:
            field_dict["comment"] = comment
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if cpus is not UNSET:
            field_dict["cpus"] = cpus
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if current_working_directory is not UNSET:
            field_dict["current_working_directory"] = current_working_directory
        if exit_code is not UNSET:
            field_dict["exit_code"] = exit_code
        if flags is not UNSET:
            field_dict["flags"] = flags
        if gres_detail is not UNSET:
            field_dict["gres_detail"] = gres_detail
        if group_id is not UNSET:
            field_dict["group_id"] = group_id
        if id is not UNSET:
            field_dict["id"] = id
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if job_resources is not UNSET:
            field_dict["job_resources"] = job_resources
        if memory is not UNSET:
            field_dict["memory"] = memory
        if minimum_cpus_per_node is not UNSET:
            field_dict["minimum_cpus_per_node"] = minimum_cpus_per_node
        if minimum_tmp_disk_per_node is not UNSET:
            field_dict["minimum_tmp_disk_per_node"] = minimum_tmp_disk_per_node
        if name is not UNSET:
            field_dict["name"] = name
        if node_count is not UNSET:
            field_dict["node_count"] = node_count
        if nodes is not UNSET:
            field_dict["nodes"] = nodes
        if partition is not UNSET:
            field_dict["partition"] = partition
        if priority is not UNSET:
            field_dict["priority"] = priority
        if qos is not UNSET:
            field_dict["qos"] = qos
        if resources is not UNSET:
            field_dict["resources"] = resources
        if script is not UNSET:
            field_dict["script"] = script
        if standard_error is not UNSET:
            field_dict["standard_error"] = standard_error
        if standard_input is not UNSET:
            field_dict["standard_input"] = standard_input
        if standard_output is not UNSET:
            field_dict["standard_output"] = standard_output
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if state_description is not UNSET:
            field_dict["state_description"] = state_description
        if state_reason is not UNSET:
            field_dict["state_reason"] = state_reason
        if status is not UNSET:
            field_dict["status"] = status
        if tasks is not UNSET:
            field_dict["tasks"] = tasks
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if time_limit is not UNSET:
            field_dict["time_limit"] = time_limit
        if time_used is not UNSET:
            field_dict["time_used"] = time_used
        if tres_alloc_str is not UNSET:
            field_dict["tres_alloc_str"] = tres_alloc_str
        if tres_req_str is not UNSET:
            field_dict["tres_req_str"] = tres_req_str
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if user_name is not UNSET:
            field_dict["user_name"] = user_name
        if work_dir is not UNSET:
            field_dict["work_dir"] = work_dir

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_alloc_tres_type_0 import JobAllocTresType0
        from ..models.job_gres_detail_type_0_item import JobGresDetailType0Item
        from ..models.job_job_resources_type_0 import JobJobResourcesType0
        from ..models.job_resources_type_0 import JobResourcesType0

        d = dict(src_dict)

        def _parse_account(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        account = _parse_account(d.pop("account", UNSET))

        def _parse_alloc_tres(data: object) -> Union["JobAllocTresType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                alloc_tres_type_0 = JobAllocTresType0.from_dict(data)

                return alloc_tres_type_0
            except:  # noqa: E722
                pass
            return cast(Union["JobAllocTresType0", None, Unset], data)

        alloc_tres = _parse_alloc_tres(d.pop("alloc_tres", UNSET))

        def _parse_array_job_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        array_job_id = _parse_array_job_id(d.pop("array_job_id", UNSET))

        def _parse_array_task_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        array_task_id = _parse_array_task_id(d.pop("array_task_id", UNSET))

        def _parse_batch_host(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        batch_host = _parse_batch_host(d.pop("batch_host", UNSET))

        def _parse_cluster(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        cluster = _parse_cluster(d.pop("cluster", UNSET))

        def _parse_cluster_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        cluster_id = _parse_cluster_id(d.pop("cluster_id", UNSET))

        def _parse_command(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        command = _parse_command(d.pop("command", UNSET))

        def _parse_comment(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        comment = _parse_comment(d.pop("comment", UNSET))

        def _parse_completed_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                completed_at_type_0 = isoparse(data)

                return completed_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        completed_at = _parse_completed_at(d.pop("completed_at", UNSET))

        def _parse_cpus(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        cpus = _parse_cpus(d.pop("cpus", UNSET))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        def _parse_current_working_directory(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        current_working_directory = _parse_current_working_directory(d.pop("current_working_directory", UNSET))

        def _parse_exit_code(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        exit_code = _parse_exit_code(d.pop("exit_code", UNSET))

        def _parse_flags(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                flags_type_0 = cast(list[str], data)

                return flags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        flags = _parse_flags(d.pop("flags", UNSET))

        def _parse_gres_detail(data: object) -> Union[None, Unset, list["JobGresDetailType0Item"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                gres_detail_type_0 = []
                _gres_detail_type_0 = data
                for gres_detail_type_0_item_data in _gres_detail_type_0:
                    gres_detail_type_0_item = JobGresDetailType0Item.from_dict(gres_detail_type_0_item_data)

                    gres_detail_type_0.append(gres_detail_type_0_item)

                return gres_detail_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["JobGresDetailType0Item"]], data)

        gres_detail = _parse_gres_detail(d.pop("gres_detail", UNSET))

        def _parse_group_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        group_id = _parse_group_id(d.pop("group_id", UNSET))

        id = d.pop("id", UNSET)

        job_id = d.pop("job_id", UNSET)

        def _parse_job_resources(data: object) -> Union["JobJobResourcesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                job_resources_type_0 = JobJobResourcesType0.from_dict(data)

                return job_resources_type_0
            except:  # noqa: E722
                pass
            return cast(Union["JobJobResourcesType0", None, Unset], data)

        job_resources = _parse_job_resources(d.pop("job_resources", UNSET))

        def _parse_memory(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        memory = _parse_memory(d.pop("memory", UNSET))

        def _parse_minimum_cpus_per_node(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        minimum_cpus_per_node = _parse_minimum_cpus_per_node(d.pop("minimum_cpus_per_node", UNSET))

        def _parse_minimum_tmp_disk_per_node(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        minimum_tmp_disk_per_node = _parse_minimum_tmp_disk_per_node(d.pop("minimum_tmp_disk_per_node", UNSET))

        name = d.pop("name", UNSET)

        def _parse_node_count(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        node_count = _parse_node_count(d.pop("node_count", UNSET))

        def _parse_nodes(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                nodes_type_0 = cast(list[str], data)

                return nodes_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        nodes = _parse_nodes(d.pop("nodes", UNSET))

        def _parse_partition(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        partition = _parse_partition(d.pop("partition", UNSET))

        def _parse_priority(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        priority = _parse_priority(d.pop("priority", UNSET))

        def _parse_qos(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        qos = _parse_qos(d.pop("qos", UNSET))

        def _parse_resources(data: object) -> Union["JobResourcesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                resources_type_0 = JobResourcesType0.from_dict(data)

                return resources_type_0
            except:  # noqa: E722
                pass
            return cast(Union["JobResourcesType0", None, Unset], data)

        resources = _parse_resources(d.pop("resources", UNSET))

        def _parse_script(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        script = _parse_script(d.pop("script", UNSET))

        def _parse_standard_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        standard_error = _parse_standard_error(d.pop("standard_error", UNSET))

        def _parse_standard_input(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        standard_input = _parse_standard_input(d.pop("standard_input", UNSET))

        def _parse_standard_output(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        standard_output = _parse_standard_output(d.pop("standard_output", UNSET))

        def _parse_started_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        started_at = _parse_started_at(d.pop("started_at", UNSET))

        def _parse_state_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        state_description = _parse_state_description(d.pop("state_description", UNSET))

        def _parse_state_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        state_reason = _parse_state_reason(d.pop("state_reason", UNSET))

        _status = d.pop("status", UNSET)
        status: Union[Unset, JobStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = JobStatus(_status)

        def _parse_tasks(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        tasks = _parse_tasks(d.pop("tasks", UNSET))

        def _parse_team_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        team_id = _parse_team_id(d.pop("team_id", UNSET))

        def _parse_time_limit(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        time_limit = _parse_time_limit(d.pop("time_limit", UNSET))

        def _parse_time_used(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        time_used = _parse_time_used(d.pop("time_used", UNSET))

        def _parse_tres_alloc_str(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tres_alloc_str = _parse_tres_alloc_str(d.pop("tres_alloc_str", UNSET))

        def _parse_tres_req_str(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tres_req_str = _parse_tres_req_str(d.pop("tres_req_str", UNSET))

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        user_id = d.pop("user_id", UNSET)

        def _parse_user_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        user_name = _parse_user_name(d.pop("user_name", UNSET))

        def _parse_work_dir(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        work_dir = _parse_work_dir(d.pop("work_dir", UNSET))

        job = cls(
            account=account,
            alloc_tres=alloc_tres,
            array_job_id=array_job_id,
            array_task_id=array_task_id,
            batch_host=batch_host,
            cluster=cluster,
            cluster_id=cluster_id,
            command=command,
            comment=comment,
            completed_at=completed_at,
            cpus=cpus,
            created_at=created_at,
            current_working_directory=current_working_directory,
            exit_code=exit_code,
            flags=flags,
            gres_detail=gres_detail,
            group_id=group_id,
            id=id,
            job_id=job_id,
            job_resources=job_resources,
            memory=memory,
            minimum_cpus_per_node=minimum_cpus_per_node,
            minimum_tmp_disk_per_node=minimum_tmp_disk_per_node,
            name=name,
            node_count=node_count,
            nodes=nodes,
            partition=partition,
            priority=priority,
            qos=qos,
            resources=resources,
            script=script,
            standard_error=standard_error,
            standard_input=standard_input,
            standard_output=standard_output,
            started_at=started_at,
            state_description=state_description,
            state_reason=state_reason,
            status=status,
            tasks=tasks,
            team_id=team_id,
            time_limit=time_limit,
            time_used=time_used,
            tres_alloc_str=tres_alloc_str,
            tres_req_str=tres_req_str,
            updated_at=updated_at,
            user_id=user_id,
            user_name=user_name,
            work_dir=work_dir,
        )

        job.additional_properties = d
        return job

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
