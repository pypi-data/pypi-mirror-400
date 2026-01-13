from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.update_api_key_request_status import UpdateApiKeyRequestStatus
from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="UpdateApiKeyRequest")



@_attrs_define
class UpdateApiKeyRequest:
    """ 
        Attributes:
            name (Union[Unset, str]):
            scopes (Union[Unset, list[str]]):
            status (Union[Unset, UpdateApiKeyRequestStatus]):
     """

    name: Union[Unset, str] = UNSET
    scopes: Union[Unset, list[str]] = UNSET
    status: Union[Unset, UpdateApiKeyRequestStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        scopes = cast(list[str], d.pop("scopes", UNSET))


        _status = d.pop("status", UNSET)
        status: Union[Unset, UpdateApiKeyRequestStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = UpdateApiKeyRequestStatus(_status)




        update_api_key_request = cls(
            name=name,
            scopes=scopes,
            status=status,
        )


        update_api_key_request.additional_properties = d
        return update_api_key_request

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
