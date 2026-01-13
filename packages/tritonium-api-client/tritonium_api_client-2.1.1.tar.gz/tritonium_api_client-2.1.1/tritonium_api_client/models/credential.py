from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime

if TYPE_CHECKING:
  from ..models.credential_metadata import CredentialMetadata





T = TypeVar("T", bound="Credential")



@_attrs_define
class Credential:
    """ 
        Attributes:
            credential_id (Union[Unset, str]):
            provider (Union[Unset, str]):
            created_at (Union[Unset, datetime.datetime]):
            last_verified_at (Union[Unset, datetime.datetime]):
            metadata (Union[Unset, CredentialMetadata]):
     """

    credential_id: Union[Unset, str] = UNSET
    provider: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    last_verified_at: Union[Unset, datetime.datetime] = UNSET
    metadata: Union[Unset, 'CredentialMetadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.credential_metadata import CredentialMetadata
        credential_id = self.credential_id

        provider = self.provider

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        last_verified_at: Union[Unset, str] = UNSET
        if not isinstance(self.last_verified_at, Unset):
            last_verified_at = self.last_verified_at.isoformat()

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if credential_id is not UNSET:
            field_dict["credential_id"] = credential_id
        if provider is not UNSET:
            field_dict["provider"] = provider
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if last_verified_at is not UNSET:
            field_dict["last_verified_at"] = last_verified_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.credential_metadata import CredentialMetadata
        d = dict(src_dict)
        credential_id = d.pop("credential_id", UNSET)

        provider = d.pop("provider", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _last_verified_at = d.pop("last_verified_at", UNSET)
        last_verified_at: Union[Unset, datetime.datetime]
        if isinstance(_last_verified_at,  Unset):
            last_verified_at = UNSET
        else:
            last_verified_at = isoparse(_last_verified_at)




        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CredentialMetadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = CredentialMetadata.from_dict(_metadata)




        credential = cls(
            credential_id=credential_id,
            provider=provider,
            created_at=created_at,
            last_verified_at=last_verified_at,
            metadata=metadata,
        )


        credential.additional_properties = d
        return credential

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
