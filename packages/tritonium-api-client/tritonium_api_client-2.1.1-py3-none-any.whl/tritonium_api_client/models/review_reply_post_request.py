from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="ReviewReplyPostRequest")



@_attrs_define
class ReviewReplyPostRequest:
    """ 
        Attributes:
            reply_text (str):
            notify_customer (Union[Unset, bool]):
     """

    reply_text: str
    notify_customer: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        reply_text = self.reply_text

        notify_customer = self.notify_customer


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "reply_text": reply_text,
        })
        if notify_customer is not UNSET:
            field_dict["notify_customer"] = notify_customer

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reply_text = d.pop("reply_text")

        notify_customer = d.pop("notify_customer", UNSET)

        review_reply_post_request = cls(
            reply_text=reply_text,
            notify_customer=notify_customer,
        )


        review_reply_post_request.additional_properties = d
        return review_reply_post_request

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
