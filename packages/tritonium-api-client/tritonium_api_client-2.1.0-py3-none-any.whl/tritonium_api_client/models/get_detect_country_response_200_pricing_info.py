from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.get_detect_country_response_200_pricing_info_tier import GetDetectCountryResponse200PricingInfoTier
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="GetDetectCountryResponse200PricingInfo")



@_attrs_define
class GetDetectCountryResponse200PricingInfo:
    """ 
        Attributes:
            tier (Union[Unset, GetDetectCountryResponse200PricingInfoTier]): Pricing tier based on PPP
            discount_rate (Union[Unset, float]): Discount rate (0.0 to 0.6) Example: 0.4.
            currency (Union[Unset, str]): Preferred currency for this region Example: USD.
     """

    tier: Union[Unset, GetDetectCountryResponse200PricingInfoTier] = UNSET
    discount_rate: Union[Unset, float] = UNSET
    currency: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        tier: Union[Unset, str] = UNSET
        if not isinstance(self.tier, Unset):
            tier = self.tier.value


        discount_rate = self.discount_rate

        currency = self.currency


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if tier is not UNSET:
            field_dict["tier"] = tier
        if discount_rate is not UNSET:
            field_dict["discount_rate"] = discount_rate
        if currency is not UNSET:
            field_dict["currency"] = currency

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _tier = d.pop("tier", UNSET)
        tier: Union[Unset, GetDetectCountryResponse200PricingInfoTier]
        if isinstance(_tier,  Unset):
            tier = UNSET
        else:
            tier = GetDetectCountryResponse200PricingInfoTier(_tier)




        discount_rate = d.pop("discount_rate", UNSET)

        currency = d.pop("currency", UNSET)

        get_detect_country_response_200_pricing_info = cls(
            tier=tier,
            discount_rate=discount_rate,
            currency=currency,
        )


        get_detect_country_response_200_pricing_info.additional_properties = d
        return get_detect_country_response_200_pricing_info

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
