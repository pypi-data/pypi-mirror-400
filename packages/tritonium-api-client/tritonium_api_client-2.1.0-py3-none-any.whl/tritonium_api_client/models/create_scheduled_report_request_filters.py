from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="CreateScheduledReportRequestFilters")



@_attrs_define
class CreateScheduledReportRequestFilters:
    """ 
        Attributes:
            app_uuids (Union[Unset, list[str]]):
            date_range_days (Union[Unset, int]):
     """

    app_uuids: Union[Unset, list[str]] = UNSET
    date_range_days: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        app_uuids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.app_uuids, Unset):
            app_uuids = self.app_uuids



        date_range_days = self.date_range_days


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if app_uuids is not UNSET:
            field_dict["app_uuids"] = app_uuids
        if date_range_days is not UNSET:
            field_dict["date_range_days"] = date_range_days

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        app_uuids = cast(list[str], d.pop("app_uuids", UNSET))


        date_range_days = d.pop("date_range_days", UNSET)

        create_scheduled_report_request_filters = cls(
            app_uuids=app_uuids,
            date_range_days=date_range_days,
        )


        create_scheduled_report_request_filters.additional_properties = d
        return create_scheduled_report_request_filters

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
