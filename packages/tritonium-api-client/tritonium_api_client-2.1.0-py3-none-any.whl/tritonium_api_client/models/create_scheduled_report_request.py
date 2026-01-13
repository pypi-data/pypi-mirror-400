from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.create_scheduled_report_request_frequency import CreateScheduledReportRequestFrequency
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.create_scheduled_report_request_filters import CreateScheduledReportRequestFilters





T = TypeVar("T", bound="CreateScheduledReportRequest")



@_attrs_define
class CreateScheduledReportRequest:
    """ 
        Attributes:
            template_id (str):
            name (str):
            frequency (CreateScheduledReportRequestFrequency):
            delivery_hour (int):
            recipients (list[str]):
            delivery_day (Union[Unset, int]):
            filters (Union[Unset, CreateScheduledReportRequestFilters]):
            enabled (Union[Unset, bool]):  Default: True.
     """

    template_id: str
    name: str
    frequency: CreateScheduledReportRequestFrequency
    delivery_hour: int
    recipients: list[str]
    delivery_day: Union[Unset, int] = UNSET
    filters: Union[Unset, 'CreateScheduledReportRequestFilters'] = UNSET
    enabled: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.create_scheduled_report_request_filters import CreateScheduledReportRequestFilters
        template_id = self.template_id

        name = self.name

        frequency = self.frequency.value

        delivery_hour = self.delivery_hour

        recipients = self.recipients



        delivery_day = self.delivery_day

        filters: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        enabled = self.enabled


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "template_id": template_id,
            "name": name,
            "frequency": frequency,
            "delivery_hour": delivery_hour,
            "recipients": recipients,
        })
        if delivery_day is not UNSET:
            field_dict["delivery_day"] = delivery_day
        if filters is not UNSET:
            field_dict["filters"] = filters
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_scheduled_report_request_filters import CreateScheduledReportRequestFilters
        d = dict(src_dict)
        template_id = d.pop("template_id")

        name = d.pop("name")

        frequency = CreateScheduledReportRequestFrequency(d.pop("frequency"))




        delivery_hour = d.pop("delivery_hour")

        recipients = cast(list[str], d.pop("recipients"))


        delivery_day = d.pop("delivery_day", UNSET)

        _filters = d.pop("filters", UNSET)
        filters: Union[Unset, CreateScheduledReportRequestFilters]
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = CreateScheduledReportRequestFilters.from_dict(_filters)




        enabled = d.pop("enabled", UNSET)

        create_scheduled_report_request = cls(
            template_id=template_id,
            name=name,
            frequency=frequency,
            delivery_hour=delivery_hour,
            recipients=recipients,
            delivery_day=delivery_day,
            filters=filters,
            enabled=enabled,
        )


        create_scheduled_report_request.additional_properties = d
        return create_scheduled_report_request

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
