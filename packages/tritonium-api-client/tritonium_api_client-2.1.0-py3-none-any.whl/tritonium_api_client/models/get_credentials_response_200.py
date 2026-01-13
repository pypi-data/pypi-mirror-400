from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.credential import Credential





T = TypeVar("T", bound="GetCredentialsResponse200")



@_attrs_define
class GetCredentialsResponse200:
    """ 
        Attributes:
            credentials (Union[Unset, list['Credential']]):
     """

    credentials: Union[Unset, list['Credential']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.credential import Credential
        credentials: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.credentials, Unset):
            credentials = []
            for credentials_item_data in self.credentials:
                credentials_item = credentials_item_data.to_dict()
                credentials.append(credentials_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if credentials is not UNSET:
            field_dict["credentials"] = credentials

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.credential import Credential
        d = dict(src_dict)
        credentials = []
        _credentials = d.pop("credentials", UNSET)
        for credentials_item_data in (_credentials or []):
            credentials_item = Credential.from_dict(credentials_item_data)



            credentials.append(credentials_item)


        get_credentials_response_200 = cls(
            credentials=credentials,
        )


        get_credentials_response_200.additional_properties = d
        return get_credentials_response_200

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
