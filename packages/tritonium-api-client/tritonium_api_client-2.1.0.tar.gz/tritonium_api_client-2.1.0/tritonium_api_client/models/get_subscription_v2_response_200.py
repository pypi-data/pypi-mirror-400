from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.get_subscription_v2_response_200_subscription import GetSubscriptionV2Response200Subscription





T = TypeVar("T", bound="GetSubscriptionV2Response200")



@_attrs_define
class GetSubscriptionV2Response200:
    """ 
        Attributes:
            subscription (Union[Unset, GetSubscriptionV2Response200Subscription]):
     """

    subscription: Union[Unset, 'GetSubscriptionV2Response200Subscription'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_subscription_v2_response_200_subscription import GetSubscriptionV2Response200Subscription
        subscription: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.subscription, Unset):
            subscription = self.subscription.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if subscription is not UNSET:
            field_dict["subscription"] = subscription

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_subscription_v2_response_200_subscription import GetSubscriptionV2Response200Subscription
        d = dict(src_dict)
        _subscription = d.pop("subscription", UNSET)
        subscription: Union[Unset, GetSubscriptionV2Response200Subscription]
        if isinstance(_subscription,  Unset):
            subscription = UNSET
        else:
            subscription = GetSubscriptionV2Response200Subscription.from_dict(_subscription)




        get_subscription_v2_response_200 = cls(
            subscription=subscription,
        )


        get_subscription_v2_response_200.additional_properties = d
        return get_subscription_v2_response_200

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
