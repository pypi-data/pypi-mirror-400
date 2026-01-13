from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.event_timestamp_type import EventTimestampType
from ..models.metric_status import MetricStatus
from dateutil.parser import isoparse
from typing import cast
import datetime






T = TypeVar("T", bound="Event")



@_attrs_define
class Event:
    """ 
        Attributes:
            event_id (str):
            name (str):
            description (str):
            creation_timestamp (datetime.datetime):
            timestamp_type (EventTimestampType):
            timestamp (datetime.datetime):
            tags (list[str]):  Example: ['tag1', 'tag2'].
            status (MetricStatus):
            metrics_i_ds (list[str]):
     """

    event_id: str
    name: str
    description: str
    creation_timestamp: datetime.datetime
    timestamp_type: EventTimestampType
    timestamp: datetime.datetime
    tags: list[str]
    status: MetricStatus
    metrics_i_ds: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        event_id = self.event_id

        name = self.name

        description = self.description

        creation_timestamp = self.creation_timestamp.isoformat()

        timestamp_type = self.timestamp_type.value

        timestamp = self.timestamp.isoformat()

        tags = self.tags



        status = self.status.value

        metrics_i_ds = self.metrics_i_ds




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "eventID": event_id,
            "name": name,
            "description": description,
            "creationTimestamp": creation_timestamp,
            "timestampType": timestamp_type,
            "timestamp": timestamp,
            "tags": tags,
            "status": status,
            "metricsIDs": metrics_i_ds,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        event_id = d.pop("eventID")

        name = d.pop("name")

        description = d.pop("description")

        creation_timestamp = isoparse(d.pop("creationTimestamp"))




        timestamp_type = EventTimestampType(d.pop("timestampType"))




        timestamp = isoparse(d.pop("timestamp"))




        tags = cast(list[str], d.pop("tags"))


        status = MetricStatus(d.pop("status"))




        metrics_i_ds = cast(list[str], d.pop("metricsIDs"))


        event = cls(
            event_id=event_id,
            name=name,
            description=description,
            creation_timestamp=creation_timestamp,
            timestamp_type=timestamp_type,
            timestamp=timestamp,
            tags=tags,
            status=status,
            metrics_i_ds=metrics_i_ds,
        )


        event.additional_properties = d
        return event

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
