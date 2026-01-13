from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.post_create_subscription_v2_body_billing_cycle import PostCreateSubscriptionV2BodyBillingCycle
from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="PostCreateSubscriptionV2Body")



@_attrs_define
class PostCreateSubscriptionV2Body:
    """ 
        Attributes:
            payment_method_id (Union[Unset, str]):
            integration_ids (Union[Unset, list[str]]):
            integration_count (Union[Unset, int]):
            member_count (Union[Unset, int]):
            billing_cycle (Union[Unset, PostCreateSubscriptionV2BodyBillingCycle]):
     """

    payment_method_id: Union[Unset, str] = UNSET
    integration_ids: Union[Unset, list[str]] = UNSET
    integration_count: Union[Unset, int] = UNSET
    member_count: Union[Unset, int] = UNSET
    billing_cycle: Union[Unset, PostCreateSubscriptionV2BodyBillingCycle] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        payment_method_id = self.payment_method_id

        integration_ids: Union[Unset, list[str]] = UNSET
        if not isinstance(self.integration_ids, Unset):
            integration_ids = self.integration_ids



        integration_count = self.integration_count

        member_count = self.member_count

        billing_cycle: Union[Unset, str] = UNSET
        if not isinstance(self.billing_cycle, Unset):
            billing_cycle = self.billing_cycle.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if payment_method_id is not UNSET:
            field_dict["payment_method_id"] = payment_method_id
        if integration_ids is not UNSET:
            field_dict["integration_ids"] = integration_ids
        if integration_count is not UNSET:
            field_dict["integration_count"] = integration_count
        if member_count is not UNSET:
            field_dict["member_count"] = member_count
        if billing_cycle is not UNSET:
            field_dict["billing_cycle"] = billing_cycle

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        payment_method_id = d.pop("payment_method_id", UNSET)

        integration_ids = cast(list[str], d.pop("integration_ids", UNSET))


        integration_count = d.pop("integration_count", UNSET)

        member_count = d.pop("member_count", UNSET)

        _billing_cycle = d.pop("billing_cycle", UNSET)
        billing_cycle: Union[Unset, PostCreateSubscriptionV2BodyBillingCycle]
        if isinstance(_billing_cycle,  Unset):
            billing_cycle = UNSET
        else:
            billing_cycle = PostCreateSubscriptionV2BodyBillingCycle(_billing_cycle)




        post_create_subscription_v2_body = cls(
            payment_method_id=payment_method_id,
            integration_ids=integration_ids,
            integration_count=integration_count,
            member_count=member_count,
            billing_cycle=billing_cycle,
        )


        post_create_subscription_v2_body.additional_properties = d
        return post_create_subscription_v2_body

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
