from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.get_pricing_response_200_pricing import GetPricingResponse200Pricing





T = TypeVar("T", bound="GetPricingResponse200")



@_attrs_define
class GetPricingResponse200:
    """ 
        Attributes:
            pricing (Union[Unset, GetPricingResponse200Pricing]):
     """

    pricing: Union[Unset, 'GetPricingResponse200Pricing'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_pricing_response_200_pricing import GetPricingResponse200Pricing
        pricing: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.pricing, Unset):
            pricing = self.pricing.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if pricing is not UNSET:
            field_dict["pricing"] = pricing

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_pricing_response_200_pricing import GetPricingResponse200Pricing
        d = dict(src_dict)
        _pricing = d.pop("pricing", UNSET)
        pricing: Union[Unset, GetPricingResponse200Pricing]
        if isinstance(_pricing,  Unset):
            pricing = UNSET
        else:
            pricing = GetPricingResponse200Pricing.from_dict(_pricing)




        get_pricing_response_200 = cls(
            pricing=pricing,
        )


        get_pricing_response_200.additional_properties = d
        return get_pricing_response_200

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
