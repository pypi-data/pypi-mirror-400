from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast






T = TypeVar("T", bound="RerunBatchInput")



@_attrs_define
class RerunBatchInput:
    """ 
        Attributes:
            sync_batch (bool):  Default: False.
            job_i_ds (list[str] | Unset):
     """

    sync_batch: bool = False
    job_i_ds: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        sync_batch = self.sync_batch

        job_i_ds: list[str] | Unset = UNSET
        if not isinstance(self.job_i_ds, Unset):
            job_i_ds = self.job_i_ds




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "syncBatch": sync_batch,
        })
        if job_i_ds is not UNSET:
            field_dict["jobIDs"] = job_i_ds

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sync_batch = d.pop("syncBatch")

        job_i_ds = cast(list[str], d.pop("jobIDs", UNSET))


        rerun_batch_input = cls(
            sync_batch=sync_batch,
            job_i_ds=job_i_ds,
        )


        rerun_batch_input.additional_properties = d
        return rerun_batch_input

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
