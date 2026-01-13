from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.post_migrate_subscription_body_billing_cycle import PostMigrateSubscriptionBodyBillingCycle
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="PostMigrateSubscriptionBody")



@_attrs_define
class PostMigrateSubscriptionBody:
    """ 
        Attributes:
            billing_cycle (Union[Unset, PostMigrateSubscriptionBodyBillingCycle]):
            member_count (Union[Unset, int]):
     """

    billing_cycle: Union[Unset, PostMigrateSubscriptionBodyBillingCycle] = UNSET
    member_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        billing_cycle: Union[Unset, str] = UNSET
        if not isinstance(self.billing_cycle, Unset):
            billing_cycle = self.billing_cycle.value


        member_count = self.member_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if billing_cycle is not UNSET:
            field_dict["billing_cycle"] = billing_cycle
        if member_count is not UNSET:
            field_dict["member_count"] = member_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _billing_cycle = d.pop("billing_cycle", UNSET)
        billing_cycle: Union[Unset, PostMigrateSubscriptionBodyBillingCycle]
        if isinstance(_billing_cycle,  Unset):
            billing_cycle = UNSET
        else:
            billing_cycle = PostMigrateSubscriptionBodyBillingCycle(_billing_cycle)




        member_count = d.pop("member_count", UNSET)

        post_migrate_subscription_body = cls(
            billing_cycle=billing_cycle,
            member_count=member_count,
        )


        post_migrate_subscription_body.additional_properties = d
        return post_migrate_subscription_body

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
