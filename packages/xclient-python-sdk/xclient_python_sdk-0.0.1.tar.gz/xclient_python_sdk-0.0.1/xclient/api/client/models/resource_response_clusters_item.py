from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.resource_response_clusters_item_cpu import ResourceResponseClustersItemCpu
    from ..models.resource_response_clusters_item_gpu import ResourceResponseClustersItemGpu
    from ..models.resource_response_clusters_item_memory import ResourceResponseClustersItemMemory


T = TypeVar("T", bound="ResourceResponseClustersItem")


@_attrs_define
class ResourceResponseClustersItem:
    """
    Attributes:
        cluster_id (Union[Unset, int]):  Example: 1.
        cluster_name (Union[Unset, str]):  Example: cluster-01.
        cpu (Union[Unset, ResourceResponseClustersItemCpu]):
        gpu (Union[Unset, ResourceResponseClustersItemGpu]):
        memory (Union[Unset, ResourceResponseClustersItemMemory]):
    """

    cluster_id: Union[Unset, int] = UNSET
    cluster_name: Union[Unset, str] = UNSET
    cpu: Union[Unset, "ResourceResponseClustersItemCpu"] = UNSET
    gpu: Union[Unset, "ResourceResponseClustersItemGpu"] = UNSET
    memory: Union[Unset, "ResourceResponseClustersItemMemory"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cluster_id = self.cluster_id

        cluster_name = self.cluster_name

        cpu: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.cpu, Unset):
            cpu = self.cpu.to_dict()

        gpu: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.gpu, Unset):
            gpu = self.gpu.to_dict()

        memory: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.memory, Unset):
            memory = self.memory.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cluster_id is not UNSET:
            field_dict["cluster_id"] = cluster_id
        if cluster_name is not UNSET:
            field_dict["cluster_name"] = cluster_name
        if cpu is not UNSET:
            field_dict["cpu"] = cpu
        if gpu is not UNSET:
            field_dict["gpu"] = gpu
        if memory is not UNSET:
            field_dict["memory"] = memory

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_response_clusters_item_cpu import ResourceResponseClustersItemCpu
        from ..models.resource_response_clusters_item_gpu import ResourceResponseClustersItemGpu
        from ..models.resource_response_clusters_item_memory import ResourceResponseClustersItemMemory

        d = dict(src_dict)
        cluster_id = d.pop("cluster_id", UNSET)

        cluster_name = d.pop("cluster_name", UNSET)

        _cpu = d.pop("cpu", UNSET)
        cpu: Union[Unset, ResourceResponseClustersItemCpu]
        if isinstance(_cpu, Unset):
            cpu = UNSET
        else:
            cpu = ResourceResponseClustersItemCpu.from_dict(_cpu)

        _gpu = d.pop("gpu", UNSET)
        gpu: Union[Unset, ResourceResponseClustersItemGpu]
        if isinstance(_gpu, Unset):
            gpu = UNSET
        else:
            gpu = ResourceResponseClustersItemGpu.from_dict(_gpu)

        _memory = d.pop("memory", UNSET)
        memory: Union[Unset, ResourceResponseClustersItemMemory]
        if isinstance(_memory, Unset):
            memory = UNSET
        else:
            memory = ResourceResponseClustersItemMemory.from_dict(_memory)

        resource_response_clusters_item = cls(
            cluster_id=cluster_id,
            cluster_name=cluster_name,
            cpu=cpu,
            gpu=gpu,
            memory=memory,
        )

        resource_response_clusters_item.additional_properties = d
        return resource_response_clusters_item

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
