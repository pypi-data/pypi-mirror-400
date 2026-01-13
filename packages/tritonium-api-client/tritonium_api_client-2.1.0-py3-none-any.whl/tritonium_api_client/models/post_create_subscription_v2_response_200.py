from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="PostCreateSubscriptionV2Response200")



@_attrs_define
class PostCreateSubscriptionV2Response200:
    """ 
        Attributes:
            subscription_id (Union[Unset, str]):
            status (Union[Unset, str]):
     """

    subscription_id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        subscription_id = self.subscription_id

        status = self.status


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if subscription_id is not UNSET:
            field_dict["subscription_id"] = subscription_id
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        subscription_id = d.pop("subscription_id", UNSET)

        status = d.pop("status", UNSET)

        post_create_subscription_v2_response_200 = cls(
            subscription_id=subscription_id,
            status=status,
        )


        post_create_subscription_v2_response_200.additional_properties = d
        return post_create_subscription_v2_response_200

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
