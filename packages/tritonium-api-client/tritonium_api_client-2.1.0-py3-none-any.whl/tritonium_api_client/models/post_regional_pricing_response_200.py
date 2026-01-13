from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.regional_pricing_response import RegionalPricingResponse





T = TypeVar("T", bound="PostRegionalPricingResponse200")



@_attrs_define
class PostRegionalPricingResponse200:
    """ 
        Attributes:
            regional_pricing (Union[Unset, RegionalPricingResponse]):
     """

    regional_pricing: Union[Unset, 'RegionalPricingResponse'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.regional_pricing_response import RegionalPricingResponse
        regional_pricing: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.regional_pricing, Unset):
            regional_pricing = self.regional_pricing.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if regional_pricing is not UNSET:
            field_dict["regional_pricing"] = regional_pricing

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.regional_pricing_response import RegionalPricingResponse
        d = dict(src_dict)
        _regional_pricing = d.pop("regional_pricing", UNSET)
        regional_pricing: Union[Unset, RegionalPricingResponse]
        if isinstance(_regional_pricing,  Unset):
            regional_pricing = UNSET
        else:
            regional_pricing = RegionalPricingResponse.from_dict(_regional_pricing)




        post_regional_pricing_response_200 = cls(
            regional_pricing=regional_pricing,
        )


        post_regional_pricing_response_200.additional_properties = d
        return post_regional_pricing_response_200

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
