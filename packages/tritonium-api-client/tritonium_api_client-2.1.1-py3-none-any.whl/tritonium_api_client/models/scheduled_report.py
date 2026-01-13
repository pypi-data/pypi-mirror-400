from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime

if TYPE_CHECKING:
  from ..models.scheduled_report_filters import ScheduledReportFilters





T = TypeVar("T", bound="ScheduledReport")



@_attrs_define
class ScheduledReport:
    """ 
        Attributes:
            schedule_id (Union[Unset, str]):
            template_id (Union[Unset, str]):
            template_name (Union[Unset, str]):
            name (Union[Unset, str]):
            frequency (Union[Unset, str]):
            delivery_day (Union[Unset, int]):
            delivery_hour (Union[Unset, int]):
            recipients (Union[Unset, list[str]]):
            filters (Union[Unset, ScheduledReportFilters]):
            enabled (Union[Unset, bool]):
            last_sent_at (Union[Unset, datetime.datetime]):
            next_send_at (Union[Unset, datetime.datetime]):
            created_at (Union[Unset, datetime.datetime]):
     """

    schedule_id: Union[Unset, str] = UNSET
    template_id: Union[Unset, str] = UNSET
    template_name: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    frequency: Union[Unset, str] = UNSET
    delivery_day: Union[Unset, int] = UNSET
    delivery_hour: Union[Unset, int] = UNSET
    recipients: Union[Unset, list[str]] = UNSET
    filters: Union[Unset, 'ScheduledReportFilters'] = UNSET
    enabled: Union[Unset, bool] = UNSET
    last_sent_at: Union[Unset, datetime.datetime] = UNSET
    next_send_at: Union[Unset, datetime.datetime] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.scheduled_report_filters import ScheduledReportFilters
        schedule_id = self.schedule_id

        template_id = self.template_id

        template_name = self.template_name

        name = self.name

        frequency = self.frequency

        delivery_day = self.delivery_day

        delivery_hour = self.delivery_hour

        recipients: Union[Unset, list[str]] = UNSET
        if not isinstance(self.recipients, Unset):
            recipients = self.recipients



        filters: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        enabled = self.enabled

        last_sent_at: Union[Unset, str] = UNSET
        if not isinstance(self.last_sent_at, Unset):
            last_sent_at = self.last_sent_at.isoformat()

        next_send_at: Union[Unset, str] = UNSET
        if not isinstance(self.next_send_at, Unset):
            next_send_at = self.next_send_at.isoformat()

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if schedule_id is not UNSET:
            field_dict["schedule_id"] = schedule_id
        if template_id is not UNSET:
            field_dict["template_id"] = template_id
        if template_name is not UNSET:
            field_dict["template_name"] = template_name
        if name is not UNSET:
            field_dict["name"] = name
        if frequency is not UNSET:
            field_dict["frequency"] = frequency
        if delivery_day is not UNSET:
            field_dict["delivery_day"] = delivery_day
        if delivery_hour is not UNSET:
            field_dict["delivery_hour"] = delivery_hour
        if recipients is not UNSET:
            field_dict["recipients"] = recipients
        if filters is not UNSET:
            field_dict["filters"] = filters
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if last_sent_at is not UNSET:
            field_dict["last_sent_at"] = last_sent_at
        if next_send_at is not UNSET:
            field_dict["next_send_at"] = next_send_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scheduled_report_filters import ScheduledReportFilters
        d = dict(src_dict)
        schedule_id = d.pop("schedule_id", UNSET)

        template_id = d.pop("template_id", UNSET)

        template_name = d.pop("template_name", UNSET)

        name = d.pop("name", UNSET)

        frequency = d.pop("frequency", UNSET)

        delivery_day = d.pop("delivery_day", UNSET)

        delivery_hour = d.pop("delivery_hour", UNSET)

        recipients = cast(list[str], d.pop("recipients", UNSET))


        _filters = d.pop("filters", UNSET)
        filters: Union[Unset, ScheduledReportFilters]
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = ScheduledReportFilters.from_dict(_filters)




        enabled = d.pop("enabled", UNSET)

        _last_sent_at = d.pop("last_sent_at", UNSET)
        last_sent_at: Union[Unset, datetime.datetime]
        if isinstance(_last_sent_at,  Unset):
            last_sent_at = UNSET
        else:
            last_sent_at = isoparse(_last_sent_at)




        _next_send_at = d.pop("next_send_at", UNSET)
        next_send_at: Union[Unset, datetime.datetime]
        if isinstance(_next_send_at,  Unset):
            next_send_at = UNSET
        else:
            next_send_at = isoparse(_next_send_at)




        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        scheduled_report = cls(
            schedule_id=schedule_id,
            template_id=template_id,
            template_name=template_name,
            name=name,
            frequency=frequency,
            delivery_day=delivery_day,
            delivery_hour=delivery_hour,
            recipients=recipients,
            filters=filters,
            enabled=enabled,
            last_sent_at=last_sent_at,
            next_send_at=next_send_at,
            created_at=created_at,
        )


        scheduled_report.additional_properties = d
        return scheduled_report

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
