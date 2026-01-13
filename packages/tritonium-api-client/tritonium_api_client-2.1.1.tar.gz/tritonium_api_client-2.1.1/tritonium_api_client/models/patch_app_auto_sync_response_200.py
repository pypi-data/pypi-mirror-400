from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.patch_app_auto_sync_response_200_frequency import PatchAppAutoSyncResponse200Frequency
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="PatchAppAutoSyncResponse200")



@_attrs_define
class PatchAppAutoSyncResponse200:
    """ 
        Attributes:
            app_uuid (Union[Unset, str]):
            auto_sync_enabled (Union[Unset, bool]):
            frequency (Union[Unset, PatchAppAutoSyncResponse200Frequency]):
     """

    app_uuid: Union[Unset, str] = UNSET
    auto_sync_enabled: Union[Unset, bool] = UNSET
    frequency: Union[Unset, PatchAppAutoSyncResponse200Frequency] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        app_uuid = self.app_uuid

        auto_sync_enabled = self.auto_sync_enabled

        frequency: Union[Unset, str] = UNSET
        if not isinstance(self.frequency, Unset):
            frequency = self.frequency.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if app_uuid is not UNSET:
            field_dict["app_uuid"] = app_uuid
        if auto_sync_enabled is not UNSET:
            field_dict["auto_sync_enabled"] = auto_sync_enabled
        if frequency is not UNSET:
            field_dict["frequency"] = frequency

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        app_uuid = d.pop("app_uuid", UNSET)

        auto_sync_enabled = d.pop("auto_sync_enabled", UNSET)

        _frequency = d.pop("frequency", UNSET)
        frequency: Union[Unset, PatchAppAutoSyncResponse200Frequency]
        if isinstance(_frequency,  Unset):
            frequency = UNSET
        else:
            frequency = PatchAppAutoSyncResponse200Frequency(_frequency)




        patch_app_auto_sync_response_200 = cls(
            app_uuid=app_uuid,
            auto_sync_enabled=auto_sync_enabled,
            frequency=frequency,
        )


        patch_app_auto_sync_response_200.additional_properties = d
        return patch_app_auto_sync_response_200

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
