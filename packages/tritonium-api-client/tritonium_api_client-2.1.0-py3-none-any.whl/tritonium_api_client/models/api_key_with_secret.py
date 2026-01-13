from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.api_key_status import ApiKeyStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime






T = TypeVar("T", bound="ApiKeyWithSecret")



@_attrs_define
class ApiKeyWithSecret:
    """ 
        Attributes:
            key_id (Union[Unset, str]): Unique identifier for the API key.
            key_prefix (Union[Unset, str]): Prefix of the key for identification. Example: trtn_live_abc123....
            name (Union[Unset, str]): Friendly name for the API key.
            scopes (Union[Unset, list[str]]): Permission scopes granted to this key.
            status (Union[Unset, ApiKeyStatus]): Current status of the API key.
            created_at (Union[Unset, datetime.datetime]):
            created_by (Union[Unset, str]): User ID who created the key.
            expires_at (Union[None, Unset, datetime.datetime]): Expiration timestamp (null for no expiration).
            last_used_at (Union[None, Unset, datetime.datetime]):
            usage_count (Union[Unset, int]): Total number of requests made with this key.
            key (Union[Unset, str]): The actual API key secret. Only shown on creation/rotation. Example:
                trtn_live_abc123def456ghi789jkl012mno345pqr678.
     """

    key_id: Union[Unset, str] = UNSET
    key_prefix: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    status: Union[Unset, ApiKeyStatus] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    created_by: Union[Unset, str] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    last_used_at: Union[None, Unset, datetime.datetime] = UNSET
    usage_count: Union[Unset, int] = UNSET
    key: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        key_id = self.key_id

        key_prefix = self.key_prefix

        name = self.name

        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        created_by = self.created_by

        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        last_used_at: Union[None, Unset, str]
        if isinstance(self.last_used_at, Unset):
            last_used_at = UNSET
        elif isinstance(self.last_used_at, datetime.datetime):
            last_used_at = self.last_used_at.isoformat()
        else:
            last_used_at = self.last_used_at

        usage_count = self.usage_count

        key = self.key


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if key_id is not UNSET:
            field_dict["key_id"] = key_id
        if key_prefix is not UNSET:
            field_dict["key_prefix"] = key_prefix
        if name is not UNSET:
            field_dict["name"] = name
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if status is not UNSET:
            field_dict["status"] = status
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if last_used_at is not UNSET:
            field_dict["last_used_at"] = last_used_at
        if usage_count is not UNSET:
            field_dict["usage_count"] = usage_count
        if key is not UNSET:
            field_dict["key"] = key

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        key_id = d.pop("key_id", UNSET)

        key_prefix = d.pop("key_prefix", UNSET)

        name = d.pop("name", UNSET)

        scopes = cast(list[str], d.pop("scopes", UNSET))


        _status = d.pop("status", UNSET)
        status: Union[Unset, ApiKeyStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = ApiKeyStatus(_status)




        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        created_by = d.pop("created_by", UNSET)

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)



                return expires_at_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))


        def _parse_last_used_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_used_at_type_0 = isoparse(data)



                return last_used_at_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_used_at = _parse_last_used_at(d.pop("last_used_at", UNSET))


        usage_count = d.pop("usage_count", UNSET)

        key = d.pop("key", UNSET)

        api_key_with_secret = cls(
            key_id=key_id,
            key_prefix=key_prefix,
            name=name,
            scopes=scopes,
            status=status,
            created_at=created_at,
            created_by=created_by,
            expires_at=expires_at,
            last_used_at=last_used_at,
            usage_count=usage_count,
            key=key,
        )


        api_key_with_secret.additional_properties = d
        return api_key_with_secret

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
