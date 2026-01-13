from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.api_key_with_secret import ApiKeyWithSecret





T = TypeVar("T", bound="CreateApiKeyResponse201")



@_attrs_define
class CreateApiKeyResponse201:
    """ 
        Attributes:
            api_key (Union[Unset, ApiKeyWithSecret]):
            message (Union[Unset, str]):
     """

    api_key: Union[Unset, 'ApiKeyWithSecret'] = UNSET
    message: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.api_key_with_secret import ApiKeyWithSecret
        api_key: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.api_key, Unset):
            api_key = self.api_key.to_dict()

        message = self.message


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if api_key is not UNSET:
            field_dict["api_key"] = api_key
        if message is not UNSET:
            field_dict["message"] = message

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_with_secret import ApiKeyWithSecret
        d = dict(src_dict)
        _api_key = d.pop("api_key", UNSET)
        api_key: Union[Unset, ApiKeyWithSecret]
        if isinstance(_api_key,  Unset):
            api_key = UNSET
        else:
            api_key = ApiKeyWithSecret.from_dict(_api_key)




        message = d.pop("message", UNSET)

        create_api_key_response_201 = cls(
            api_key=api_key,
            message=message,
        )


        create_api_key_response_201.additional_properties = d
        return create_api_key_response_201

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
