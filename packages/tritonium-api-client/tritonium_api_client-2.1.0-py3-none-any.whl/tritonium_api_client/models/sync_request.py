from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="SyncRequest")



@_attrs_define
class SyncRequest:
    """ 
        Attributes:
            app_uuid (str):
            force_full_sync (Union[Unset, bool]):
     """

    app_uuid: str
    force_full_sync: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        app_uuid = self.app_uuid

        force_full_sync = self.force_full_sync


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "app_uuid": app_uuid,
        })
        if force_full_sync is not UNSET:
            field_dict["force_full_sync"] = force_full_sync

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        app_uuid = d.pop("app_uuid")

        force_full_sync = d.pop("force_full_sync", UNSET)

        sync_request = cls(
            app_uuid=app_uuid,
            force_full_sync=force_full_sync,
        )


        sync_request.additional_properties = d
        return sync_request

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
