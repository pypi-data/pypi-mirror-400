from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="SendScheduledReportNowResponse200")



@_attrs_define
class SendScheduledReportNowResponse200:
    """ 
        Attributes:
            message (Union[Unset, str]):
            job_id (Union[Unset, str]):
     """

    message: Union[Unset, str] = UNSET
    job_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        message = self.message

        job_id = self.job_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if message is not UNSET:
            field_dict["message"] = message
        if job_id is not UNSET:
            field_dict["job_id"] = job_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message", UNSET)

        job_id = d.pop("job_id", UNSET)

        send_scheduled_report_now_response_200 = cls(
            message=message,
            job_id=job_id,
        )


        send_scheduled_report_now_response_200.additional_properties = d
        return send_scheduled_report_now_response_200

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
