from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.integration_test_request_payload import IntegrationTestRequestPayload





T = TypeVar("T", bound="IntegrationTestRequest")



@_attrs_define
class IntegrationTestRequest:
    """ 
        Attributes:
            message (Union[Unset, str]):
            severity (Union[Unset, str]):
            payload (Union[Unset, IntegrationTestRequestPayload]):
     """

    message: Union[Unset, str] = UNSET
    severity: Union[Unset, str] = UNSET
    payload: Union[Unset, 'IntegrationTestRequestPayload'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.integration_test_request_payload import IntegrationTestRequestPayload
        message = self.message

        severity = self.severity

        payload: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.payload, Unset):
            payload = self.payload.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if message is not UNSET:
            field_dict["message"] = message
        if severity is not UNSET:
            field_dict["severity"] = severity
        if payload is not UNSET:
            field_dict["payload"] = payload

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.integration_test_request_payload import IntegrationTestRequestPayload
        d = dict(src_dict)
        message = d.pop("message", UNSET)

        severity = d.pop("severity", UNSET)

        _payload = d.pop("payload", UNSET)
        payload: Union[Unset, IntegrationTestRequestPayload]
        if isinstance(_payload,  Unset):
            payload = UNSET
        else:
            payload = IntegrationTestRequestPayload.from_dict(_payload)




        integration_test_request = cls(
            message=message,
            severity=severity,
            payload=payload,
        )


        integration_test_request.additional_properties = d
        return integration_test_request

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
