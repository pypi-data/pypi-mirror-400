from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.triggered_via import TriggeredVia
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.experience_filter_input import ExperienceFilterInput
  from ..models.batch_parameters import BatchParameters





T = TypeVar("T", bound="BatchInput")



@_attrs_define
class BatchInput:
    """ 
        Attributes:
            excluded_experience_i_ds (list[str] | None | Unset):
            filters (ExperienceFilterInput | Unset):
            experience_i_ds (list[str] | None | Unset):
            experience_tag_i_ds (list[str] | None | Unset):
            experience_names (list[str] | None | Unset):
            experience_tag_names (list[str] | None | Unset):
            build_id (str | Unset):
            metrics_build_id (str | Unset):
            metrics_set_name (None | str | Unset):
            parameters (BatchParameters | Unset):
            associated_account (str | Unset):
            triggered_via (TriggeredVia | Unset):
            pool_labels (list[str] | Unset):
            batch_name (str | Unset):
            allowable_failure_percent (int | None | Unset):
     """

    excluded_experience_i_ds: list[str] | None | Unset = UNSET
    filters: ExperienceFilterInput | Unset = UNSET
    experience_i_ds: list[str] | None | Unset = UNSET
    experience_tag_i_ds: list[str] | None | Unset = UNSET
    experience_names: list[str] | None | Unset = UNSET
    experience_tag_names: list[str] | None | Unset = UNSET
    build_id: str | Unset = UNSET
    metrics_build_id: str | Unset = UNSET
    metrics_set_name: None | str | Unset = UNSET
    parameters: BatchParameters | Unset = UNSET
    associated_account: str | Unset = UNSET
    triggered_via: TriggeredVia | Unset = UNSET
    pool_labels: list[str] | Unset = UNSET
    batch_name: str | Unset = UNSET
    allowable_failure_percent: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.experience_filter_input import ExperienceFilterInput
        from ..models.batch_parameters import BatchParameters
        excluded_experience_i_ds: list[str] | None | Unset
        if isinstance(self.excluded_experience_i_ds, Unset):
            excluded_experience_i_ds = UNSET
        elif isinstance(self.excluded_experience_i_ds, list):
            excluded_experience_i_ds = self.excluded_experience_i_ds


        else:
            excluded_experience_i_ds = self.excluded_experience_i_ds

        filters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        experience_i_ds: list[str] | None | Unset
        if isinstance(self.experience_i_ds, Unset):
            experience_i_ds = UNSET
        elif isinstance(self.experience_i_ds, list):
            experience_i_ds = self.experience_i_ds


        else:
            experience_i_ds = self.experience_i_ds

        experience_tag_i_ds: list[str] | None | Unset
        if isinstance(self.experience_tag_i_ds, Unset):
            experience_tag_i_ds = UNSET
        elif isinstance(self.experience_tag_i_ds, list):
            experience_tag_i_ds = self.experience_tag_i_ds


        else:
            experience_tag_i_ds = self.experience_tag_i_ds

        experience_names: list[str] | None | Unset
        if isinstance(self.experience_names, Unset):
            experience_names = UNSET
        elif isinstance(self.experience_names, list):
            experience_names = self.experience_names


        else:
            experience_names = self.experience_names

        experience_tag_names: list[str] | None | Unset
        if isinstance(self.experience_tag_names, Unset):
            experience_tag_names = UNSET
        elif isinstance(self.experience_tag_names, list):
            experience_tag_names = self.experience_tag_names


        else:
            experience_tag_names = self.experience_tag_names

        build_id = self.build_id

        metrics_build_id = self.metrics_build_id

        metrics_set_name: None | str | Unset
        if isinstance(self.metrics_set_name, Unset):
            metrics_set_name = UNSET
        else:
            metrics_set_name = self.metrics_set_name

        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        associated_account = self.associated_account

        triggered_via: str | Unset = UNSET
        if not isinstance(self.triggered_via, Unset):
            triggered_via = self.triggered_via.value


        pool_labels: list[str] | Unset = UNSET
        if not isinstance(self.pool_labels, Unset):
            pool_labels = self.pool_labels



        batch_name = self.batch_name

        allowable_failure_percent: int | None | Unset
        if isinstance(self.allowable_failure_percent, Unset):
            allowable_failure_percent = UNSET
        else:
            allowable_failure_percent = self.allowable_failure_percent


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if excluded_experience_i_ds is not UNSET:
            field_dict["excludedExperienceIDs"] = excluded_experience_i_ds
        if filters is not UNSET:
            field_dict["filters"] = filters
        if experience_i_ds is not UNSET:
            field_dict["experienceIDs"] = experience_i_ds
        if experience_tag_i_ds is not UNSET:
            field_dict["experienceTagIDs"] = experience_tag_i_ds
        if experience_names is not UNSET:
            field_dict["experienceNames"] = experience_names
        if experience_tag_names is not UNSET:
            field_dict["experienceTagNames"] = experience_tag_names
        if build_id is not UNSET:
            field_dict["buildID"] = build_id
        if metrics_build_id is not UNSET:
            field_dict["metricsBuildID"] = metrics_build_id
        if metrics_set_name is not UNSET:
            field_dict["metricsSetName"] = metrics_set_name
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if associated_account is not UNSET:
            field_dict["associatedAccount"] = associated_account
        if triggered_via is not UNSET:
            field_dict["triggeredVia"] = triggered_via
        if pool_labels is not UNSET:
            field_dict["poolLabels"] = pool_labels
        if batch_name is not UNSET:
            field_dict["batchName"] = batch_name
        if allowable_failure_percent is not UNSET:
            field_dict["allowableFailurePercent"] = allowable_failure_percent

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.experience_filter_input import ExperienceFilterInput
        from ..models.batch_parameters import BatchParameters
        d = dict(src_dict)
        def _parse_excluded_experience_i_ds(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                excluded_experience_i_ds_type_0 = cast(list[str], data)

                return excluded_experience_i_ds_type_0
            except: # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        excluded_experience_i_ds = _parse_excluded_experience_i_ds(d.pop("excludedExperienceIDs", UNSET))


        _filters = d.pop("filters", UNSET)
        filters: ExperienceFilterInput | Unset
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = ExperienceFilterInput.from_dict(_filters)




        def _parse_experience_i_ds(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                experience_i_ds_type_0 = cast(list[str], data)

                return experience_i_ds_type_0
            except: # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        experience_i_ds = _parse_experience_i_ds(d.pop("experienceIDs", UNSET))


        def _parse_experience_tag_i_ds(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                experience_tag_i_ds_type_0 = cast(list[str], data)

                return experience_tag_i_ds_type_0
            except: # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        experience_tag_i_ds = _parse_experience_tag_i_ds(d.pop("experienceTagIDs", UNSET))


        def _parse_experience_names(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                experience_names_type_0 = cast(list[str], data)

                return experience_names_type_0
            except: # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        experience_names = _parse_experience_names(d.pop("experienceNames", UNSET))


        def _parse_experience_tag_names(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                experience_tag_names_type_0 = cast(list[str], data)

                return experience_tag_names_type_0
            except: # noqa: E722
                pass
            return cast(list[str] | None | Unset, data)

        experience_tag_names = _parse_experience_tag_names(d.pop("experienceTagNames", UNSET))


        build_id = d.pop("buildID", UNSET)

        metrics_build_id = d.pop("metricsBuildID", UNSET)

        def _parse_metrics_set_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        metrics_set_name = _parse_metrics_set_name(d.pop("metricsSetName", UNSET))


        _parameters = d.pop("parameters", UNSET)
        parameters: BatchParameters | Unset
        if isinstance(_parameters,  Unset):
            parameters = UNSET
        else:
            parameters = BatchParameters.from_dict(_parameters)




        associated_account = d.pop("associatedAccount", UNSET)

        _triggered_via = d.pop("triggeredVia", UNSET)
        triggered_via: TriggeredVia | Unset
        if isinstance(_triggered_via,  Unset):
            triggered_via = UNSET
        else:
            triggered_via = TriggeredVia(_triggered_via)




        pool_labels = cast(list[str], d.pop("poolLabels", UNSET))


        batch_name = d.pop("batchName", UNSET)

        def _parse_allowable_failure_percent(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        allowable_failure_percent = _parse_allowable_failure_percent(d.pop("allowableFailurePercent", UNSET))


        batch_input = cls(
            excluded_experience_i_ds=excluded_experience_i_ds,
            filters=filters,
            experience_i_ds=experience_i_ds,
            experience_tag_i_ds=experience_tag_i_ds,
            experience_names=experience_names,
            experience_tag_names=experience_tag_names,
            build_id=build_id,
            metrics_build_id=metrics_build_id,
            metrics_set_name=metrics_set_name,
            parameters=parameters,
            associated_account=associated_account,
            triggered_via=triggered_via,
            pool_labels=pool_labels,
            batch_name=batch_name,
            allowable_failure_percent=allowable_failure_percent,
        )


        batch_input.additional_properties = d
        return batch_input

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
