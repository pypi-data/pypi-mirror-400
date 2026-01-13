from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cluster_status import ClusterStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_k8s_cluster_request_config_type_0 import UpdateK8SClusterRequestConfigType0


T = TypeVar("T", bound="UpdateK8SClusterRequest")


@_attrs_define
class UpdateK8SClusterRequest:
    """
    Attributes:
        api_server (Union[Unset, str]):  Example: https://k8s-api.example.com:6443.
        config (Union['UpdateK8SClusterRequestConfigType0', None, Unset]):  Example: {'retry': 3, 'timeout': 30}.
        description (Union[None, Unset, str]):  Example: Primary Kubernetes cluster.
        kubeconfig_content (Union[None, Unset, str]): Kubeconfig content (base64 encoded, optional) Example:
            base64encodedkubeconfigcontent.
        kubeconfig_path (Union[None, Unset, str]):  Example: /path/to/kubeconfig.
        name (Union[Unset, str]):  Example: k8s-cluster-01.
        namespace (Union[Unset, str]):  Example: default.
        status (Union[Unset, ClusterStatus]):  Example: active.
    """

    api_server: Union[Unset, str] = UNSET
    config: Union["UpdateK8SClusterRequestConfigType0", None, Unset] = UNSET
    description: Union[None, Unset, str] = UNSET
    kubeconfig_content: Union[None, Unset, str] = UNSET
    kubeconfig_path: Union[None, Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    namespace: Union[Unset, str] = UNSET
    status: Union[Unset, ClusterStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.update_k8s_cluster_request_config_type_0 import UpdateK8SClusterRequestConfigType0

        api_server = self.api_server

        config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, UpdateK8SClusterRequestConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if api_server is not UNSET:
            field_dict["api_server"] = api_server
        if config is not UNSET:
            field_dict["config"] = config
        if description is not UNSET:
            field_dict["description"] = description
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_k8s_cluster_request_config_type_0 import UpdateK8SClusterRequestConfigType0

        d = dict(src_dict)
        api_server = d.pop("api_server", UNSET)

        def _parse_config(data: object) -> Union["UpdateK8SClusterRequestConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = UpdateK8SClusterRequestConfigType0.from_dict(data)

                return config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UpdateK8SClusterRequestConfigType0", None, Unset], data)

        config = _parse_config(d.pop("config", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

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

        update_k8s_cluster_request = cls(
            api_server=api_server,
            config=config,
            description=description,
            kubeconfig_content=kubeconfig_content,
            kubeconfig_path=kubeconfig_path,
            name=name,
            namespace=namespace,
            status=status,
        )

        update_k8s_cluster_request.additional_properties = d
        return update_k8s_cluster_request

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
