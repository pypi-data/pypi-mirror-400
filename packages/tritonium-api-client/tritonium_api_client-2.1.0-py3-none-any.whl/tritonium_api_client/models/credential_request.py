from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.credential_request_metadata import CredentialRequestMetadata





T = TypeVar("T", bound="CredentialRequest")



@_attrs_define
class CredentialRequest:
    """ 
        Attributes:
            provider (str):
            secret (str):
            description (Union[Unset, str]):
            metadata (Union[Unset, CredentialRequestMetadata]):
     """

    provider: str
    secret: str
    description: Union[Unset, str] = UNSET
    metadata: Union[Unset, 'CredentialRequestMetadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.credential_request_metadata import CredentialRequestMetadata
        provider = self.provider

        secret = self.secret

        description = self.description

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "provider": provider,
            "secret": secret,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.credential_request_metadata import CredentialRequestMetadata
        d = dict(src_dict)
        provider = d.pop("provider")

        secret = d.pop("secret")

        description = d.pop("description", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CredentialRequestMetadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = CredentialRequestMetadata.from_dict(_metadata)




        credential_request = cls(
            provider=provider,
            secret=secret,
            description=description,
            metadata=metadata,
        )


        credential_request.additional_properties = d
        return credential_request

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
