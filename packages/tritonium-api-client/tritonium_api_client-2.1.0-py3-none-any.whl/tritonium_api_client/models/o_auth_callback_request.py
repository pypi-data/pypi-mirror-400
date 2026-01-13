from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="OAuthCallbackRequest")



@_attrs_define
class OAuthCallbackRequest:
    """ 
        Attributes:
            code (str):
            state (str):
            redirect_uri (Union[Unset, str]):
     """

    code: str
    state: str
    redirect_uri: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        code = self.code

        state = self.state

        redirect_uri = self.redirect_uri


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "code": code,
            "state": state,
        })
        if redirect_uri is not UNSET:
            field_dict["redirect_uri"] = redirect_uri

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        state = d.pop("state")

        redirect_uri = d.pop("redirect_uri", UNSET)

        o_auth_callback_request = cls(
            code=code,
            state=state,
            redirect_uri=redirect_uri,
        )


        o_auth_callback_request.additional_properties = d
        return o_auth_callback_request

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
