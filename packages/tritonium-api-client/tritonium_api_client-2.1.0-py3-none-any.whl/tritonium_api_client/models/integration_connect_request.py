from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.integration_connect_request_metadata import IntegrationConnectRequestMetadata





T = TypeVar("T", bound="IntegrationConnectRequest")



@_attrs_define
class IntegrationConnectRequest:
    """ 
        Attributes:
            redirect_uri (Union[Unset, str]):
            scopes (Union[Unset, list[str]]):
            metadata (Union[Unset, IntegrationConnectRequestMetadata]):
     """

    redirect_uri: Union[Unset, str] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    metadata: Union[Unset, 'IntegrationConnectRequestMetadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.integration_connect_request_metadata import IntegrationConnectRequestMetadata
        redirect_uri = self.redirect_uri

        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if redirect_uri is not UNSET:
            field_dict["redirect_uri"] = redirect_uri
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.integration_connect_request_metadata import IntegrationConnectRequestMetadata
        d = dict(src_dict)
        redirect_uri = d.pop("redirect_uri", UNSET)

        scopes = cast(list[str], d.pop("scopes", UNSET))


        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, IntegrationConnectRequestMetadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = IntegrationConnectRequestMetadata.from_dict(_metadata)




        integration_connect_request = cls(
            redirect_uri=redirect_uri,
            scopes=scopes,
            metadata=metadata,
        )


        integration_connect_request.additional_properties = d
        return integration_connect_request

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
