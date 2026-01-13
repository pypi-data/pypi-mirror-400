from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.environment_variable import EnvironmentVariable





T = TypeVar("T", bound="ExperienceSyncExperience")



@_attrs_define
class ExperienceSyncExperience:
    """ 
        Attributes:
            name (str):
            description (str):
            locations (list[str]):
            tags (list[str]):
            systems (list[str]):
            archived (bool):
            experience_id (str | Unset):
            container_timeout_seconds (int | Unset):
            profile (str | Unset):
            environment_variables (list[EnvironmentVariable] | Unset):
            cache_exempt (bool | Unset):
     """

    name: str
    description: str
    locations: list[str]
    tags: list[str]
    systems: list[str]
    archived: bool
    experience_id: str | Unset = UNSET
    container_timeout_seconds: int | Unset = UNSET
    profile: str | Unset = UNSET
    environment_variables: list[EnvironmentVariable] | Unset = UNSET
    cache_exempt: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.environment_variable import EnvironmentVariable
        name = self.name

        description = self.description

        locations = self.locations



        tags = self.tags



        systems = self.systems



        archived = self.archived

        experience_id = self.experience_id

        container_timeout_seconds = self.container_timeout_seconds

        profile = self.profile

        environment_variables: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.environment_variables, Unset):
            environment_variables = []
            for environment_variables_item_data in self.environment_variables:
                environment_variables_item = environment_variables_item_data.to_dict()
                environment_variables.append(environment_variables_item)



        cache_exempt = self.cache_exempt


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "description": description,
            "locations": locations,
            "tags": tags,
            "systems": systems,
            "archived": archived,
        })
        if experience_id is not UNSET:
            field_dict["experienceID"] = experience_id
        if container_timeout_seconds is not UNSET:
            field_dict["containerTimeoutSeconds"] = container_timeout_seconds
        if profile is not UNSET:
            field_dict["profile"] = profile
        if environment_variables is not UNSET:
            field_dict["environmentVariables"] = environment_variables
        if cache_exempt is not UNSET:
            field_dict["cacheExempt"] = cache_exempt

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.environment_variable import EnvironmentVariable
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        locations = cast(list[str], d.pop("locations"))


        tags = cast(list[str], d.pop("tags"))


        systems = cast(list[str], d.pop("systems"))


        archived = d.pop("archived")

        experience_id = d.pop("experienceID", UNSET)

        container_timeout_seconds = d.pop("containerTimeoutSeconds", UNSET)

        profile = d.pop("profile", UNSET)

        environment_variables = []
        _environment_variables = d.pop("environmentVariables", UNSET)
        for environment_variables_item_data in (_environment_variables or []):
            environment_variables_item = EnvironmentVariable.from_dict(environment_variables_item_data)



            environment_variables.append(environment_variables_item)


        cache_exempt = d.pop("cacheExempt", UNSET)

        experience_sync_experience = cls(
            name=name,
            description=description,
            locations=locations,
            tags=tags,
            systems=systems,
            archived=archived,
            experience_id=experience_id,
            container_timeout_seconds=container_timeout_seconds,
            profile=profile,
            environment_variables=environment_variables,
            cache_exempt=cache_exempt,
        )


        experience_sync_experience.additional_properties = d
        return experience_sync_experience

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
