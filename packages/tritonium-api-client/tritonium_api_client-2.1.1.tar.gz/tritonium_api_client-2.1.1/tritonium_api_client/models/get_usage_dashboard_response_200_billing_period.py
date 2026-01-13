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






T = TypeVar("T", bound="GetUsageDashboardResponse200BillingPeriod")



@_attrs_define
class GetUsageDashboardResponse200BillingPeriod:
    """ 
        Attributes:
            start (Union[Unset, datetime.date]):
            end (Union[Unset, datetime.date]):
            days_remaining (Union[Unset, int]):
     """

    start: Union[Unset, datetime.date] = UNSET
    end: Union[Unset, datetime.date] = UNSET
    days_remaining: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        start: Union[Unset, str] = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.isoformat()

        end: Union[Unset, str] = UNSET
        if not isinstance(self.end, Unset):
            end = self.end.isoformat()

        days_remaining = self.days_remaining


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end
        if days_remaining is not UNSET:
            field_dict["days_remaining"] = days_remaining

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _start = d.pop("start", UNSET)
        start: Union[Unset, datetime.date]
        if isinstance(_start,  Unset):
            start = UNSET
        else:
            start = isoparse(_start).date()




        _end = d.pop("end", UNSET)
        end: Union[Unset, datetime.date]
        if isinstance(_end,  Unset):
            end = UNSET
        else:
            end = isoparse(_end).date()




        days_remaining = d.pop("days_remaining", UNSET)

        get_usage_dashboard_response_200_billing_period = cls(
            start=start,
            end=end,
            days_remaining=days_remaining,
        )


        get_usage_dashboard_response_200_billing_period.additional_properties = d
        return get_usage_dashboard_response_200_billing_period

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
