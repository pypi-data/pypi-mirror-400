from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="ExperienceFilterInput")



@_attrs_define
class ExperienceFilterInput:
    """ 
        Attributes:
            name (str | Unset): Filter experiences by name
            text (str | Unset): Filter experiences by a text string on name and description
            search (str | Unset): A search query. Supports searching by tag_id Example: tag_id IN
                ("71b96a67-9990-426b-993e-0f3d9c6bbe48").
     """

    name: str | Unset = UNSET
    text: str | Unset = UNSET
    search: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        text = self.text

        search = self.search


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if text is not UNSET:
            field_dict["text"] = text
        if search is not UNSET:
            field_dict["search"] = search

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        text = d.pop("text", UNSET)

        search = d.pop("search", UNSET)

        experience_filter_input = cls(
            name=name,
            text=text,
            search=search,
        )


        experience_filter_input.additional_properties = d
        return experience_filter_input

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
