from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.regional_pricing_request_billing_cycle import RegionalPricingRequestBillingCycle
from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="RegionalPricingRequest")



@_attrs_define
class RegionalPricingRequest:
    """ 
        Attributes:
            country_code (Union[Unset, str]): ISO 3166-1 alpha-2 country code. Default: 'US'. Example: BR.
            app_count (Union[Unset, int]): Number of apps to price. Default: 1.
            member_count (Union[Unset, int]): Number of team members. Default: 1.
            billing_cycle (Union[Unset, RegionalPricingRequestBillingCycle]): Billing frequency. Default:
                RegionalPricingRequestBillingCycle.MONTHLY.
     """

    country_code: Union[Unset, str] = 'US'
    app_count: Union[Unset, int] = 1
    member_count: Union[Unset, int] = 1
    billing_cycle: Union[Unset, RegionalPricingRequestBillingCycle] = RegionalPricingRequestBillingCycle.MONTHLY
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        country_code = self.country_code

        app_count = self.app_count

        member_count = self.member_count

        billing_cycle: Union[Unset, str] = UNSET
        if not isinstance(self.billing_cycle, Unset):
            billing_cycle = self.billing_cycle.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if country_code is not UNSET:
            field_dict["country_code"] = country_code
        if app_count is not UNSET:
            field_dict["app_count"] = app_count
        if member_count is not UNSET:
            field_dict["member_count"] = member_count
        if billing_cycle is not UNSET:
            field_dict["billing_cycle"] = billing_cycle

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        country_code = d.pop("country_code", UNSET)

        app_count = d.pop("app_count", UNSET)

        member_count = d.pop("member_count", UNSET)

        _billing_cycle = d.pop("billing_cycle", UNSET)
        billing_cycle: Union[Unset, RegionalPricingRequestBillingCycle]
        if isinstance(_billing_cycle,  Unset):
            billing_cycle = UNSET
        else:
            billing_cycle = RegionalPricingRequestBillingCycle(_billing_cycle)




        regional_pricing_request = cls(
            country_code=country_code,
            app_count=app_count,
            member_count=member_count,
            billing_cycle=billing_cycle,
        )


        regional_pricing_request.additional_properties = d
        return regional_pricing_request

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
