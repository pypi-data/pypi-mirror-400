from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.regional_pricing_response_tier import RegionalPricingResponseTier
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="RegionalPricingResponse")



@_attrs_define
class RegionalPricingResponse:
    """ 
        Attributes:
            country_code (Union[Unset, str]):  Example: BR.
            tier (Union[Unset, RegionalPricingResponseTier]): Pricing tier based on purchasing power parity.
            discount_rate (Union[Unset, float]): Discount rate applied (0.0 to 0.6). Example: 0.4.
            discount_percentage (Union[Unset, int]): Discount as percentage (0 to 60). Example: 40.
            currency (Union[Unset, str]): Preferred currency for this region. Example: BRL.
            base_price (Union[Unset, float]): Original price before discount.
            discounted_price (Union[Unset, float]): Final price after regional discount.
            total_price (Union[Unset, float]): Total calculated price.
            annual_discount_rate (Union[Unset, float]): Additional discount for annual billing.
            annual_discount_amount (Union[Unset, float]): Amount saved with annual billing.
     """

    country_code: Union[Unset, str] = UNSET
    tier: Union[Unset, RegionalPricingResponseTier] = UNSET
    discount_rate: Union[Unset, float] = UNSET
    discount_percentage: Union[Unset, int] = UNSET
    currency: Union[Unset, str] = UNSET
    base_price: Union[Unset, float] = UNSET
    discounted_price: Union[Unset, float] = UNSET
    total_price: Union[Unset, float] = UNSET
    annual_discount_rate: Union[Unset, float] = UNSET
    annual_discount_amount: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        country_code = self.country_code

        tier: Union[Unset, str] = UNSET
        if not isinstance(self.tier, Unset):
            tier = self.tier.value


        discount_rate = self.discount_rate

        discount_percentage = self.discount_percentage

        currency = self.currency

        base_price = self.base_price

        discounted_price = self.discounted_price

        total_price = self.total_price

        annual_discount_rate = self.annual_discount_rate

        annual_discount_amount = self.annual_discount_amount


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if country_code is not UNSET:
            field_dict["country_code"] = country_code
        if tier is not UNSET:
            field_dict["tier"] = tier
        if discount_rate is not UNSET:
            field_dict["discount_rate"] = discount_rate
        if discount_percentage is not UNSET:
            field_dict["discount_percentage"] = discount_percentage
        if currency is not UNSET:
            field_dict["currency"] = currency
        if base_price is not UNSET:
            field_dict["base_price"] = base_price
        if discounted_price is not UNSET:
            field_dict["discounted_price"] = discounted_price
        if total_price is not UNSET:
            field_dict["total_price"] = total_price
        if annual_discount_rate is not UNSET:
            field_dict["annual_discount_rate"] = annual_discount_rate
        if annual_discount_amount is not UNSET:
            field_dict["annual_discount_amount"] = annual_discount_amount

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        country_code = d.pop("country_code", UNSET)

        _tier = d.pop("tier", UNSET)
        tier: Union[Unset, RegionalPricingResponseTier]
        if isinstance(_tier,  Unset):
            tier = UNSET
        else:
            tier = RegionalPricingResponseTier(_tier)




        discount_rate = d.pop("discount_rate", UNSET)

        discount_percentage = d.pop("discount_percentage", UNSET)

        currency = d.pop("currency", UNSET)

        base_price = d.pop("base_price", UNSET)

        discounted_price = d.pop("discounted_price", UNSET)

        total_price = d.pop("total_price", UNSET)

        annual_discount_rate = d.pop("annual_discount_rate", UNSET)

        annual_discount_amount = d.pop("annual_discount_amount", UNSET)

        regional_pricing_response = cls(
            country_code=country_code,
            tier=tier,
            discount_rate=discount_rate,
            discount_percentage=discount_percentage,
            currency=currency,
            base_price=base_price,
            discounted_price=discounted_price,
            total_price=total_price,
            annual_discount_rate=annual_discount_rate,
            annual_discount_amount=annual_discount_amount,
        )


        regional_pricing_response.additional_properties = d
        return regional_pricing_response

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
