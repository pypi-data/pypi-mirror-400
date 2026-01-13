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





T = TypeVar("T", bound="ListScheduledReportsResponse200")



@_attrs_define
class ListScheduledReportsResponse200:
    """ 
        Attributes:
            schedules (Union[Unset, list['ScheduledReport']]):
     """

    schedules: Union[Unset, list['ScheduledReport']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.scheduled_report import ScheduledReport
        schedules: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.schedules, Unset):
            schedules = []
            for schedules_item_data in self.schedules:
                schedules_item = schedules_item_data.to_dict()
                schedules.append(schedules_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if schedules is not UNSET:
            field_dict["schedules"] = schedules

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scheduled_report import ScheduledReport
        d = dict(src_dict)
        schedules = []
        _schedules = d.pop("schedules", UNSET)
        for schedules_item_data in (_schedules or []):
            schedules_item = ScheduledReport.from_dict(schedules_item_data)



            schedules.append(schedules_item)


        list_scheduled_reports_response_200 = cls(
            schedules=schedules,
        )


        list_scheduled_reports_response_200.additional_properties = d
        return list_scheduled_reports_response_200

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
