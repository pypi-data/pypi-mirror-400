from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="DebugExperienceOutput")



@_attrs_define
class DebugExperienceOutput:
    """ 
        Attributes:
            batch_id (str | Unset):
            namespace (str | Unset):
            cluster_endpoint (str | Unset):
            cluster_token (str | Unset):
            cluster_ca_data (str | Unset):
     """

    batch_id: str | Unset = UNSET
    namespace: str | Unset = UNSET
    cluster_endpoint: str | Unset = UNSET
    cluster_token: str | Unset = UNSET
    cluster_ca_data: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        batch_id = self.batch_id

        namespace = self.namespace

        cluster_endpoint = self.cluster_endpoint

        cluster_token = self.cluster_token

        cluster_ca_data = self.cluster_ca_data


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if batch_id is not UNSET:
            field_dict["batchID"] = batch_id
        if namespace is not UNSET:
            field_dict["namespace"] = namespace
        if cluster_endpoint is not UNSET:
            field_dict["clusterEndpoint"] = cluster_endpoint
        if cluster_token is not UNSET:
            field_dict["clusterToken"] = cluster_token
        if cluster_ca_data is not UNSET:
            field_dict["clusterCAData"] = cluster_ca_data

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        batch_id = d.pop("batchID", UNSET)

        namespace = d.pop("namespace", UNSET)

        cluster_endpoint = d.pop("clusterEndpoint", UNSET)

        cluster_token = d.pop("clusterToken", UNSET)

        cluster_ca_data = d.pop("clusterCAData", UNSET)

        debug_experience_output = cls(
            batch_id=batch_id,
            namespace=namespace,
            cluster_endpoint=cluster_endpoint,
            cluster_token=cluster_token,
            cluster_ca_data=cluster_ca_data,
        )


        debug_experience_output.additional_properties = d
        return debug_experience_output

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
