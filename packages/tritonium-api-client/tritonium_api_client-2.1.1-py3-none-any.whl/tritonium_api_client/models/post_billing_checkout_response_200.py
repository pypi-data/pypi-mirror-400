from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="PostBillingCheckoutResponse200")



@_attrs_define
class PostBillingCheckoutResponse200:
    """ 
        Attributes:
            session_id (Union[Unset, str]):
            url (Union[Unset, str]):
     """

    session_id: Union[Unset, str] = UNSET
    url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        session_id = self.session_id

        url = self.url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        session_id = d.pop("session_id", UNSET)

        url = d.pop("url", UNSET)

        post_billing_checkout_response_200 = cls(
            session_id=session_id,
            url=url,
        )


        post_billing_checkout_response_200.additional_properties = d
        return post_billing_checkout_response_200

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
