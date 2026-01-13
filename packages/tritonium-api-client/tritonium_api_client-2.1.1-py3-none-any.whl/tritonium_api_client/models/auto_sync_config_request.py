from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.auto_sync_config_request_frequency import AutoSyncConfigRequestFrequency
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="AutoSyncConfigRequest")



@_attrs_define
class AutoSyncConfigRequest:
    """ 
        Attributes:
            auto_sync_enabled (bool):
            frequency (Union[Unset, AutoSyncConfigRequestFrequency]):
     """

    auto_sync_enabled: bool
    frequency: Union[Unset, AutoSyncConfigRequestFrequency] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        auto_sync_enabled = self.auto_sync_enabled

        frequency: Union[Unset, str] = UNSET
        if not isinstance(self.frequency, Unset):
            frequency = self.frequency.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "auto_sync_enabled": auto_sync_enabled,
        })
        if frequency is not UNSET:
            field_dict["frequency"] = frequency

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        auto_sync_enabled = d.pop("auto_sync_enabled")

        _frequency = d.pop("frequency", UNSET)
        frequency: Union[Unset, AutoSyncConfigRequestFrequency]
        if isinstance(_frequency,  Unset):
            frequency = UNSET
        else:
            frequency = AutoSyncConfigRequestFrequency(_frequency)




        auto_sync_config_request = cls(
            auto_sync_enabled=auto_sync_enabled,
            frequency=frequency,
        )


        auto_sync_config_request.additional_properties = d
        return auto_sync_config_request

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
