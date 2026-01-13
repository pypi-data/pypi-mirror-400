from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.sms_connect_request_metadata import SmsConnectRequestMetadata





T = TypeVar("T", bound="SmsConnectRequest")



@_attrs_define
class SmsConnectRequest:
    """ 
        Attributes:
            phone_number (str):
            provider (Union[Unset, str]):
            metadata (Union[Unset, SmsConnectRequestMetadata]):
     """

    phone_number: str
    provider: Union[Unset, str] = UNSET
    metadata: Union[Unset, 'SmsConnectRequestMetadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.sms_connect_request_metadata import SmsConnectRequestMetadata
        phone_number = self.phone_number

        provider = self.provider

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "phone_number": phone_number,
        })
        if provider is not UNSET:
            field_dict["provider"] = provider
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sms_connect_request_metadata import SmsConnectRequestMetadata
        d = dict(src_dict)
        phone_number = d.pop("phone_number")

        provider = d.pop("provider", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, SmsConnectRequestMetadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = SmsConnectRequestMetadata.from_dict(_metadata)




        sms_connect_request = cls(
            phone_number=phone_number,
            provider=provider,
            metadata=metadata,
        )


        sms_connect_request.additional_properties = d
        return sms_connect_request

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
