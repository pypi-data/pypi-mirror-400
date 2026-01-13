from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.metric import Metric





T = TypeVar("T", bound="ListReportMetricsOutput")



@_attrs_define
class ListReportMetricsOutput:
    """ 
        Attributes:
            report_metrics (list[Metric] | Unset):
            next_page_token (str | Unset):
     """

    report_metrics: list[Metric] | Unset = UNSET
    next_page_token: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.metric import Metric
        report_metrics: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.report_metrics, Unset):
            report_metrics = []
            for report_metrics_item_data in self.report_metrics:
                report_metrics_item = report_metrics_item_data.to_dict()
                report_metrics.append(report_metrics_item)



        next_page_token = self.next_page_token


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if report_metrics is not UNSET:
            field_dict["reportMetrics"] = report_metrics
        if next_page_token is not UNSET:
            field_dict["nextPageToken"] = next_page_token

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metric import Metric
        d = dict(src_dict)
        report_metrics = []
        _report_metrics = d.pop("reportMetrics", UNSET)
        for report_metrics_item_data in (_report_metrics or []):
            report_metrics_item = Metric.from_dict(report_metrics_item_data)



            report_metrics.append(report_metrics_item)


        next_page_token = d.pop("nextPageToken", UNSET)

        list_report_metrics_output = cls(
            report_metrics=report_metrics,
            next_page_token=next_page_token,
        )


        list_report_metrics_output.additional_properties = d
        return list_report_metrics_output

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
