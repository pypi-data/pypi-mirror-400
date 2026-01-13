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






T = TypeVar("T", bound="GenerateReportRequestFilters")



@_attrs_define
class GenerateReportRequestFilters:
    """ 
        Attributes:
            start_date (Union[Unset, datetime.date]):
            end_date (Union[Unset, datetime.date]):
            app_uuids (Union[Unset, list[str]]):
     """

    start_date: Union[Unset, datetime.date] = UNSET
    end_date: Union[Unset, datetime.date] = UNSET
    app_uuids: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        start_date: Union[Unset, str] = UNSET
        if not isinstance(self.start_date, Unset):
            start_date = self.start_date.isoformat()

        end_date: Union[Unset, str] = UNSET
        if not isinstance(self.end_date, Unset):
            end_date = self.end_date.isoformat()

        app_uuids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.app_uuids, Unset):
            app_uuids = self.app_uuids




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if start_date is not UNSET:
            field_dict["start_date"] = start_date
        if end_date is not UNSET:
            field_dict["end_date"] = end_date
        if app_uuids is not UNSET:
            field_dict["app_uuids"] = app_uuids

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _start_date = d.pop("start_date", UNSET)
        start_date: Union[Unset, datetime.date]
        if isinstance(_start_date,  Unset):
            start_date = UNSET
        else:
            start_date = isoparse(_start_date).date()




        _end_date = d.pop("end_date", UNSET)
        end_date: Union[Unset, datetime.date]
        if isinstance(_end_date,  Unset):
            end_date = UNSET
        else:
            end_date = isoparse(_end_date).date()




        app_uuids = cast(list[str], d.pop("app_uuids", UNSET))


        generate_report_request_filters = cls(
            start_date=start_date,
            end_date=end_date,
            app_uuids=app_uuids,
        )


        generate_report_request_filters.additional_properties = d
        return generate_report_request_filters

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
