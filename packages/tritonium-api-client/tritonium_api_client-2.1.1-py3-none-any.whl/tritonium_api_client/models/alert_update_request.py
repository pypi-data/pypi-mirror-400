from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.alert_update_request_status import AlertUpdateRequestStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime






T = TypeVar("T", bound="AlertUpdateRequest")



@_attrs_define
class AlertUpdateRequest:
    """ 
        Attributes:
            status (Union[Unset, AlertUpdateRequestStatus]):
            note (Union[Unset, str]):
            snooze_until (Union[Unset, datetime.datetime]):
     """

    status: Union[Unset, AlertUpdateRequestStatus] = UNSET
    note: Union[Unset, str] = UNSET
    snooze_until: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        note = self.note

        snooze_until: Union[Unset, str] = UNSET
        if not isinstance(self.snooze_until, Unset):
            snooze_until = self.snooze_until.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if status is not UNSET:
            field_dict["status"] = status
        if note is not UNSET:
            field_dict["note"] = note
        if snooze_until is not UNSET:
            field_dict["snooze_until"] = snooze_until

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _status = d.pop("status", UNSET)
        status: Union[Unset, AlertUpdateRequestStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = AlertUpdateRequestStatus(_status)




        note = d.pop("note", UNSET)

        _snooze_until = d.pop("snooze_until", UNSET)
        snooze_until: Union[Unset, datetime.datetime]
        if isinstance(_snooze_until,  Unset):
            snooze_until = UNSET
        else:
            snooze_until = isoparse(_snooze_until)




        alert_update_request = cls(
            status=status,
            note=note,
            snooze_until=snooze_until,
        )


        alert_update_request.additional_properties = d
        return alert_update_request

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
