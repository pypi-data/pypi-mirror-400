from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="GetPricingResponse200Pricing")



@_attrs_define
class GetPricingResponse200Pricing:
    """ 
        Attributes:
            model (Union[Unset, str]):  Example: per_app.
            app_price (Union[Unset, float]):  Example: 19.99.
            additional_member_price (Union[Unset, float]):  Example: 9.99.
            included_members_per_app (Union[Unset, int]):  Example: 1.
            included_ai_analyses_per_app (Union[Unset, int]):  Example: 5000.
            ai_overage_rate (Union[Unset, float]):  Example: 0.005.
            annual_discount (Union[Unset, float]):  Example: 0.1.
            trial_days (Union[Unset, int]):  Example: 7.
     """

    model: Union[Unset, str] = UNSET
    app_price: Union[Unset, float] = UNSET
    additional_member_price: Union[Unset, float] = UNSET
    included_members_per_app: Union[Unset, int] = UNSET
    included_ai_analyses_per_app: Union[Unset, int] = UNSET
    ai_overage_rate: Union[Unset, float] = UNSET
    annual_discount: Union[Unset, float] = UNSET
    trial_days: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        model = self.model

        app_price = self.app_price

        additional_member_price = self.additional_member_price

        included_members_per_app = self.included_members_per_app

        included_ai_analyses_per_app = self.included_ai_analyses_per_app

        ai_overage_rate = self.ai_overage_rate

        annual_discount = self.annual_discount

        trial_days = self.trial_days


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if model is not UNSET:
            field_dict["model"] = model
        if app_price is not UNSET:
            field_dict["app_price"] = app_price
        if additional_member_price is not UNSET:
            field_dict["additional_member_price"] = additional_member_price
        if included_members_per_app is not UNSET:
            field_dict["included_members_per_app"] = included_members_per_app
        if included_ai_analyses_per_app is not UNSET:
            field_dict["included_ai_analyses_per_app"] = included_ai_analyses_per_app
        if ai_overage_rate is not UNSET:
            field_dict["ai_overage_rate"] = ai_overage_rate
        if annual_discount is not UNSET:
            field_dict["annual_discount"] = annual_discount
        if trial_days is not UNSET:
            field_dict["trial_days"] = trial_days

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        model = d.pop("model", UNSET)

        app_price = d.pop("app_price", UNSET)

        additional_member_price = d.pop("additional_member_price", UNSET)

        included_members_per_app = d.pop("included_members_per_app", UNSET)

        included_ai_analyses_per_app = d.pop("included_ai_analyses_per_app", UNSET)

        ai_overage_rate = d.pop("ai_overage_rate", UNSET)

        annual_discount = d.pop("annual_discount", UNSET)

        trial_days = d.pop("trial_days", UNSET)

        get_pricing_response_200_pricing = cls(
            model=model,
            app_price=app_price,
            additional_member_price=additional_member_price,
            included_members_per_app=included_members_per_app,
            included_ai_analyses_per_app=included_ai_analyses_per_app,
            ai_overage_rate=ai_overage_rate,
            annual_discount=annual_discount,
            trial_days=trial_days,
        )


        get_pricing_response_200_pricing.additional_properties = d
        return get_pricing_response_200_pricing

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
