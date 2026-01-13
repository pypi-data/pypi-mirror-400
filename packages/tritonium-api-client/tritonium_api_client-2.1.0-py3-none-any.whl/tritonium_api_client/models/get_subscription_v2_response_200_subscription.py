from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.get_subscription_v2_response_200_subscription_billing_cycle import GetSubscriptionV2Response200SubscriptionBillingCycle
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.get_subscription_v2_response_200_subscription_active_integrations_item import GetSubscriptionV2Response200SubscriptionActiveIntegrationsItem





T = TypeVar("T", bound="GetSubscriptionV2Response200Subscription")



@_attrs_define
class GetSubscriptionV2Response200Subscription:
    """ 
        Attributes:
            subscription_id (Union[Unset, str]):
            tenant_id (Union[Unset, str]):
            status (Union[Unset, str]):
            pricing_model (Union[Unset, str]):
            billing_cycle (Union[Unset, GetSubscriptionV2Response200SubscriptionBillingCycle]):
            integration_count (Union[Unset, int]):
            member_count (Union[Unset, int]):
            integration_subtotal (Union[Unset, float]):
            member_subtotal (Union[Unset, float]):
            monthly_cost (Union[Unset, float]):
            annual_discount_applied (Union[None, Unset, float]):
            effective_monthly_rate (Union[Unset, float]):
            active_integrations (Union[Unset, list['GetSubscriptionV2Response200SubscriptionActiveIntegrationsItem']]):
            stripe_customer_id (Union[Unset, str]):
            stripe_subscription_id (Union[Unset, str]):
     """

    subscription_id: Union[Unset, str] = UNSET
    tenant_id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    pricing_model: Union[Unset, str] = UNSET
    billing_cycle: Union[Unset, GetSubscriptionV2Response200SubscriptionBillingCycle] = UNSET
    integration_count: Union[Unset, int] = UNSET
    member_count: Union[Unset, int] = UNSET
    integration_subtotal: Union[Unset, float] = UNSET
    member_subtotal: Union[Unset, float] = UNSET
    monthly_cost: Union[Unset, float] = UNSET
    annual_discount_applied: Union[None, Unset, float] = UNSET
    effective_monthly_rate: Union[Unset, float] = UNSET
    active_integrations: Union[Unset, list['GetSubscriptionV2Response200SubscriptionActiveIntegrationsItem']] = UNSET
    stripe_customer_id: Union[Unset, str] = UNSET
    stripe_subscription_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_subscription_v2_response_200_subscription_active_integrations_item import GetSubscriptionV2Response200SubscriptionActiveIntegrationsItem
        subscription_id = self.subscription_id

        tenant_id = self.tenant_id

        status = self.status

        pricing_model = self.pricing_model

        billing_cycle: Union[Unset, str] = UNSET
        if not isinstance(self.billing_cycle, Unset):
            billing_cycle = self.billing_cycle.value


        integration_count = self.integration_count

        member_count = self.member_count

        integration_subtotal = self.integration_subtotal

        member_subtotal = self.member_subtotal

        monthly_cost = self.monthly_cost

        annual_discount_applied: Union[None, Unset, float]
        if isinstance(self.annual_discount_applied, Unset):
            annual_discount_applied = UNSET
        else:
            annual_discount_applied = self.annual_discount_applied

        effective_monthly_rate = self.effective_monthly_rate

        active_integrations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.active_integrations, Unset):
            active_integrations = []
            for active_integrations_item_data in self.active_integrations:
                active_integrations_item = active_integrations_item_data.to_dict()
                active_integrations.append(active_integrations_item)



        stripe_customer_id = self.stripe_customer_id

        stripe_subscription_id = self.stripe_subscription_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if subscription_id is not UNSET:
            field_dict["subscription_id"] = subscription_id
        if tenant_id is not UNSET:
            field_dict["tenant_id"] = tenant_id
        if status is not UNSET:
            field_dict["status"] = status
        if pricing_model is not UNSET:
            field_dict["pricing_model"] = pricing_model
        if billing_cycle is not UNSET:
            field_dict["billing_cycle"] = billing_cycle
        if integration_count is not UNSET:
            field_dict["integration_count"] = integration_count
        if member_count is not UNSET:
            field_dict["member_count"] = member_count
        if integration_subtotal is not UNSET:
            field_dict["integration_subtotal"] = integration_subtotal
        if member_subtotal is not UNSET:
            field_dict["member_subtotal"] = member_subtotal
        if monthly_cost is not UNSET:
            field_dict["monthly_cost"] = monthly_cost
        if annual_discount_applied is not UNSET:
            field_dict["annual_discount_applied"] = annual_discount_applied
        if effective_monthly_rate is not UNSET:
            field_dict["effective_monthly_rate"] = effective_monthly_rate
        if active_integrations is not UNSET:
            field_dict["active_integrations"] = active_integrations
        if stripe_customer_id is not UNSET:
            field_dict["stripe_customer_id"] = stripe_customer_id
        if stripe_subscription_id is not UNSET:
            field_dict["stripe_subscription_id"] = stripe_subscription_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_subscription_v2_response_200_subscription_active_integrations_item import GetSubscriptionV2Response200SubscriptionActiveIntegrationsItem
        d = dict(src_dict)
        subscription_id = d.pop("subscription_id", UNSET)

        tenant_id = d.pop("tenant_id", UNSET)

        status = d.pop("status", UNSET)

        pricing_model = d.pop("pricing_model", UNSET)

        _billing_cycle = d.pop("billing_cycle", UNSET)
        billing_cycle: Union[Unset, GetSubscriptionV2Response200SubscriptionBillingCycle]
        if isinstance(_billing_cycle,  Unset):
            billing_cycle = UNSET
        else:
            billing_cycle = GetSubscriptionV2Response200SubscriptionBillingCycle(_billing_cycle)




        integration_count = d.pop("integration_count", UNSET)

        member_count = d.pop("member_count", UNSET)

        integration_subtotal = d.pop("integration_subtotal", UNSET)

        member_subtotal = d.pop("member_subtotal", UNSET)

        monthly_cost = d.pop("monthly_cost", UNSET)

        def _parse_annual_discount_applied(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        annual_discount_applied = _parse_annual_discount_applied(d.pop("annual_discount_applied", UNSET))


        effective_monthly_rate = d.pop("effective_monthly_rate", UNSET)

        active_integrations = []
        _active_integrations = d.pop("active_integrations", UNSET)
        for active_integrations_item_data in (_active_integrations or []):
            active_integrations_item = GetSubscriptionV2Response200SubscriptionActiveIntegrationsItem.from_dict(active_integrations_item_data)



            active_integrations.append(active_integrations_item)


        stripe_customer_id = d.pop("stripe_customer_id", UNSET)

        stripe_subscription_id = d.pop("stripe_subscription_id", UNSET)

        get_subscription_v2_response_200_subscription = cls(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            status=status,
            pricing_model=pricing_model,
            billing_cycle=billing_cycle,
            integration_count=integration_count,
            member_count=member_count,
            integration_subtotal=integration_subtotal,
            member_subtotal=member_subtotal,
            monthly_cost=monthly_cost,
            annual_discount_applied=annual_discount_applied,
            effective_monthly_rate=effective_monthly_rate,
            active_integrations=active_integrations,
            stripe_customer_id=stripe_customer_id,
            stripe_subscription_id=stripe_subscription_id,
        )


        get_subscription_v2_response_200_subscription.additional_properties = d
        return get_subscription_v2_response_200_subscription

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
