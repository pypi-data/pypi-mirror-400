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






T = TypeVar("T", bound="AppSummary")



@_attrs_define
class AppSummary:
    """ 
        Attributes:
            app_uuid (Union[Unset, str]):
            app_name (Union[Unset, str]):
            platform (Union[Unset, str]):
            review_count (Union[Unset, int]):
            auto_sync_enabled (Union[Unset, bool]):
            auto_sync_frequency (Union[Unset, str]):
            last_synced_at (Union[Unset, datetime.datetime]):
     """

    app_uuid: Union[Unset, str] = UNSET
    app_name: Union[Unset, str] = UNSET
    platform: Union[Unset, str] = UNSET
    review_count: Union[Unset, int] = UNSET
    auto_sync_enabled: Union[Unset, bool] = UNSET
    auto_sync_frequency: Union[Unset, str] = UNSET
    last_synced_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        app_uuid = self.app_uuid

        app_name = self.app_name

        platform = self.platform

        review_count = self.review_count

        auto_sync_enabled = self.auto_sync_enabled

        auto_sync_frequency = self.auto_sync_frequency

        last_synced_at: Union[Unset, str] = UNSET
        if not isinstance(self.last_synced_at, Unset):
            last_synced_at = self.last_synced_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if app_uuid is not UNSET:
            field_dict["app_uuid"] = app_uuid
        if app_name is not UNSET:
            field_dict["app_name"] = app_name
        if platform is not UNSET:
            field_dict["platform"] = platform
        if review_count is not UNSET:
            field_dict["review_count"] = review_count
        if auto_sync_enabled is not UNSET:
            field_dict["auto_sync_enabled"] = auto_sync_enabled
        if auto_sync_frequency is not UNSET:
            field_dict["auto_sync_frequency"] = auto_sync_frequency
        if last_synced_at is not UNSET:
            field_dict["last_synced_at"] = last_synced_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        app_uuid = d.pop("app_uuid", UNSET)

        app_name = d.pop("app_name", UNSET)

        platform = d.pop("platform", UNSET)

        review_count = d.pop("review_count", UNSET)

        auto_sync_enabled = d.pop("auto_sync_enabled", UNSET)

        auto_sync_frequency = d.pop("auto_sync_frequency", UNSET)

        _last_synced_at = d.pop("last_synced_at", UNSET)
        last_synced_at: Union[Unset, datetime.datetime]
        if isinstance(_last_synced_at,  Unset):
            last_synced_at = UNSET
        else:
            last_synced_at = isoparse(_last_synced_at)




        app_summary = cls(
            app_uuid=app_uuid,
            app_name=app_name,
            platform=platform,
            review_count=review_count,
            auto_sync_enabled=auto_sync_enabled,
            auto_sync_frequency=auto_sync_frequency,
            last_synced_at=last_synced_at,
        )


        app_summary.additional_properties = d
        return app_summary

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
