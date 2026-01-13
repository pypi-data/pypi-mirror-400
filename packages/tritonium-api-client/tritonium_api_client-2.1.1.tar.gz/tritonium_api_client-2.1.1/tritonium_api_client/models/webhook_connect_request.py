from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.webhook_connect_request_metadata import WebhookConnectRequestMetadata





T = TypeVar("T", bound="WebhookConnectRequest")



@_attrs_define
class WebhookConnectRequest:
    """ 
        Attributes:
            url (str):
            secret (Union[Unset, str]):
            metadata (Union[Unset, WebhookConnectRequestMetadata]):
     """

    url: str
    secret: Union[Unset, str] = UNSET
    metadata: Union[Unset, 'WebhookConnectRequestMetadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.webhook_connect_request_metadata import WebhookConnectRequestMetadata
        url = self.url

        secret = self.secret

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "url": url,
        })
        if secret is not UNSET:
            field_dict["secret"] = secret
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.webhook_connect_request_metadata import WebhookConnectRequestMetadata
        d = dict(src_dict)
        url = d.pop("url")

        secret = d.pop("secret", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, WebhookConnectRequestMetadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = WebhookConnectRequestMetadata.from_dict(_metadata)




        webhook_connect_request = cls(
            url=url,
            secret=secret,
            metadata=metadata,
        )


        webhook_connect_request.additional_properties = d
        return webhook_connect_request

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
