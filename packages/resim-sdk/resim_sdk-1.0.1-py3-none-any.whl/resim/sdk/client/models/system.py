from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.architecture import Architecture
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="System")



@_attrs_define
class System:
    """ 
        Attributes:
            system_id (str):
            project_id (str):
            name (str):
            description (str):
            build_vcpus (int):
            build_memory_mib (int):
            build_gpus (int):
            build_shared_memory_mb (int):
            architecture (Architecture):
            metrics_build_vcpus (int):
            metrics_build_memory_mib (int):
            metrics_build_gpus (int):
            metrics_build_shared_memory_mb (int):
            num_builds (int):
            num_test_suites (int):
            num_experiences (int):
            num_metrics_builds (int):
            num_batches (int):
            creation_timestamp (datetime.datetime):
            user_id (str):
            org_id (str):
            archived (bool):
     """

    system_id: str
    project_id: str
    name: str
    description: str
    build_vcpus: int
    build_memory_mib: int
    build_gpus: int
    build_shared_memory_mb: int
    architecture: Architecture
    metrics_build_vcpus: int
    metrics_build_memory_mib: int
    metrics_build_gpus: int
    metrics_build_shared_memory_mb: int
    num_builds: int
    num_test_suites: int
    num_experiences: int
    num_metrics_builds: int
    num_batches: int
    creation_timestamp: datetime.datetime
    user_id: str
    org_id: str
    archived: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        system_id = self.system_id

        project_id = self.project_id

        name = self.name

        description = self.description

        build_vcpus = self.build_vcpus

        build_memory_mib = self.build_memory_mib

        build_gpus = self.build_gpus

        build_shared_memory_mb = self.build_shared_memory_mb

        architecture = self.architecture.value

        metrics_build_vcpus = self.metrics_build_vcpus

        metrics_build_memory_mib = self.metrics_build_memory_mib

        metrics_build_gpus = self.metrics_build_gpus

        metrics_build_shared_memory_mb = self.metrics_build_shared_memory_mb

        num_builds = self.num_builds

        num_test_suites = self.num_test_suites

        num_experiences = self.num_experiences

        num_metrics_builds = self.num_metrics_builds

        num_batches = self.num_batches

        creation_timestamp = self.creation_timestamp.isoformat()

        user_id = self.user_id

        org_id = self.org_id

        archived = self.archived


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "systemID": system_id,
            "projectID": project_id,
            "name": name,
            "description": description,
            "build_vcpus": build_vcpus,
            "build_memory_mib": build_memory_mib,
            "build_gpus": build_gpus,
            "build_shared_memory_mb": build_shared_memory_mb,
            "architecture": architecture,
            "metrics_build_vcpus": metrics_build_vcpus,
            "metrics_build_memory_mib": metrics_build_memory_mib,
            "metrics_build_gpus": metrics_build_gpus,
            "metrics_build_shared_memory_mb": metrics_build_shared_memory_mb,
            "numBuilds": num_builds,
            "numTestSuites": num_test_suites,
            "numExperiences": num_experiences,
            "numMetricsBuilds": num_metrics_builds,
            "numBatches": num_batches,
            "creationTimestamp": creation_timestamp,
            "userID": user_id,
            "orgID": org_id,
            "archived": archived,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        system_id = d.pop("systemID")

        project_id = d.pop("projectID")

        name = d.pop("name")

        description = d.pop("description")

        build_vcpus = d.pop("build_vcpus")

        build_memory_mib = d.pop("build_memory_mib")

        build_gpus = d.pop("build_gpus")

        build_shared_memory_mb = d.pop("build_shared_memory_mb")

        architecture = Architecture(d.pop("architecture"))




        metrics_build_vcpus = d.pop("metrics_build_vcpus")

        metrics_build_memory_mib = d.pop("metrics_build_memory_mib")

        metrics_build_gpus = d.pop("metrics_build_gpus")

        metrics_build_shared_memory_mb = d.pop("metrics_build_shared_memory_mb")

        num_builds = d.pop("numBuilds")

        num_test_suites = d.pop("numTestSuites")

        num_experiences = d.pop("numExperiences")

        num_metrics_builds = d.pop("numMetricsBuilds")

        num_batches = d.pop("numBatches")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        user_id = d.pop("userID")

        org_id = d.pop("orgID")

        archived = d.pop("archived")

        system = cls(
            system_id=system_id,
            project_id=project_id,
            name=name,
            description=description,
            build_vcpus=build_vcpus,
            build_memory_mib=build_memory_mib,
            build_gpus=build_gpus,
            build_shared_memory_mb=build_shared_memory_mb,
            architecture=architecture,
            metrics_build_vcpus=metrics_build_vcpus,
            metrics_build_memory_mib=metrics_build_memory_mib,
            metrics_build_gpus=metrics_build_gpus,
            metrics_build_shared_memory_mb=metrics_build_shared_memory_mb,
            num_builds=num_builds,
            num_test_suites=num_test_suites,
            num_experiences=num_experiences,
            num_metrics_builds=num_metrics_builds,
            num_batches=num_batches,
            creation_timestamp=creation_timestamp,
            user_id=user_id,
            org_id=org_id,
            archived=archived,
        )


        system.additional_properties = d
        return system

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
