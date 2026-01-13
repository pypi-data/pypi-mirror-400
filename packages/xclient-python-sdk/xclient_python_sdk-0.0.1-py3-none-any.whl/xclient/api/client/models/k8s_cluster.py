import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.cluster_status import ClusterStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.k8s_cluster_config_type_0 import K8SClusterConfigType0


T = TypeVar("T", bound="K8SCluster")


@_attrs_define
class K8SCluster:
    """
    Attributes:
        api_server (Union[Unset, str]):  Example: https://k8s-api.example.com:6443.
        config (Union['K8SClusterConfigType0', None, Unset]): Additional configuration (JSON format) Example: {'retry':
            3, 'timeout': 30}.
        created_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
        description (Union[None, Unset, str]):  Example: Primary Kubernetes cluster.
        id (Union[Unset, int]):  Example: 1.
        kubeconfig_content (Union[None, Unset, str]): Kubeconfig content (base64 encoded, optional) Example:
            base64encodedkubeconfigcontent.
        kubeconfig_path (Union[None, Unset, str]):  Example: /path/to/kubeconfig.
        name (Union[Unset, str]):  Example: k8s-cluster-01.
        namespace (Union[Unset, str]):  Example: default.
        status (Union[Unset, ClusterStatus]):  Example: active.
        updated_at (Union[Unset, datetime.datetime]):  Example: 2024-01-01T00:00:00Z.
    """

    api_server: Union[Unset, str] = UNSET
    config: Union["K8SClusterConfigType0", None, Unset] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    description: Union[None, Unset, str] = UNSET
    id: Union[Unset, int] = UNSET
    kubeconfig_content: Union[None, Unset, str] = UNSET
    kubeconfig_path: Union[None, Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    namespace: Union[Unset, str] = UNSET
    status: Union[Unset, ClusterStatus] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.k8s_cluster_config_type_0 import K8SClusterConfigType0

        api_server = self.api_server

        config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, K8SClusterConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        id = self.id

        kubeconfig_content: Union[None, Unset, str]
        if isinstance(self.kubeconfig_content, Unset):
            kubeconfig_content = UNSET
        else:
            kubeconfig_content = self.kubeconfig_content

        kubeconfig_path: Union[None, Unset, str]
        if isinstance(self.kubeconfig_path, Unset):
            kubeconfig_path = UNSET
        else:
            kubeconfig_path = self.kubeconfig_path

        name = self.name

        namespace = self.namespace

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if api_server is not UNSET:
            field_dict["api_server"] = api_server
        if config is not UNSET:
            field_dict["config"] = config
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if id is not UNSET:
            field_dict["id"] = id
        if kubeconfig_content is not UNSET:
            field_dict["kubeconfig_content"] = kubeconfig_content
        if kubeconfig_path is not UNSET:
            field_dict["kubeconfig_path"] = kubeconfig_path
        if name is not UNSET:
            field_dict["name"] = name
        if namespace is not UNSET:
            field_dict["namespace"] = namespace
        if status is not UNSET:
            field_dict["status"] = status
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.k8s_cluster_config_type_0 import K8SClusterConfigType0

        d = dict(src_dict)
        api_server = d.pop("api_server", UNSET)

        def _parse_config(data: object) -> Union["K8SClusterConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = K8SClusterConfigType0.from_dict(data)

                return config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["K8SClusterConfigType0", None, Unset], data)

        config = _parse_config(d.pop("config", UNSET))

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

        def _parse_kubeconfig_content(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        kubeconfig_content = _parse_kubeconfig_content(d.pop("kubeconfig_content", UNSET))

        def _parse_kubeconfig_path(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        kubeconfig_path = _parse_kubeconfig_path(d.pop("kubeconfig_path", UNSET))

        name = d.pop("name", UNSET)

        namespace = d.pop("namespace", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ClusterStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ClusterStatus(_status)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        k8s_cluster = cls(
            api_server=api_server,
            config=config,
            created_at=created_at,
            description=description,
            id=id,
            kubeconfig_content=kubeconfig_content,
            kubeconfig_path=kubeconfig_path,
            name=name,
            namespace=namespace,
            status=status,
            updated_at=updated_at,
        )

        k8s_cluster.additional_properties = d
        return k8s_cluster

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
