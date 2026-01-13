from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.scheduled_report import ScheduledReport





T = TypeVar("T", bound="ScheduledReportResponse")



@_attrs_define
class ScheduledReportResponse:
    """ 
        Attributes:
            schedule (Union[Unset, ScheduledReport]):
     """

    schedule: Union[Unset, 'ScheduledReport'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.scheduled_report import ScheduledReport
        schedule: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.schedule, Unset):
            schedule = self.schedule.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if schedule is not UNSET:
            field_dict["schedule"] = schedule

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scheduled_report import ScheduledReport
        d = dict(src_dict)
        _schedule = d.pop("schedule", UNSET)
        schedule: Union[Unset, ScheduledReport]
        if isinstance(_schedule,  Unset):
            schedule = UNSET
        else:
            schedule = ScheduledReport.from_dict(_schedule)




        scheduled_report_response = cls(
            schedule=schedule,
        )


        scheduled_report_response.additional_properties = d
        return scheduled_report_response

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
