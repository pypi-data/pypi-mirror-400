from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.post_calculate_pricing_response_200_calculation import PostCalculatePricingResponse200Calculation
  from ..models.post_calculate_pricing_response_200_breakdown import PostCalculatePricingResponse200Breakdown





T = TypeVar("T", bound="PostCalculatePricingResponse200")



@_attrs_define
class PostCalculatePricingResponse200:
    """ 
        Attributes:
            calculation (Union[Unset, PostCalculatePricingResponse200Calculation]):
            breakdown (Union[Unset, PostCalculatePricingResponse200Breakdown]):
     """

    calculation: Union[Unset, 'PostCalculatePricingResponse200Calculation'] = UNSET
    breakdown: Union[Unset, 'PostCalculatePricingResponse200Breakdown'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.post_calculate_pricing_response_200_calculation import PostCalculatePricingResponse200Calculation
        from ..models.post_calculate_pricing_response_200_breakdown import PostCalculatePricingResponse200Breakdown
        calculation: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.calculation, Unset):
            calculation = self.calculation.to_dict()

        breakdown: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.breakdown, Unset):
            breakdown = self.breakdown.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if calculation is not UNSET:
            field_dict["calculation"] = calculation
        if breakdown is not UNSET:
            field_dict["breakdown"] = breakdown

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_calculate_pricing_response_200_calculation import PostCalculatePricingResponse200Calculation
        from ..models.post_calculate_pricing_response_200_breakdown import PostCalculatePricingResponse200Breakdown
        d = dict(src_dict)
        _calculation = d.pop("calculation", UNSET)
        calculation: Union[Unset, PostCalculatePricingResponse200Calculation]
        if isinstance(_calculation,  Unset):
            calculation = UNSET
        else:
            calculation = PostCalculatePricingResponse200Calculation.from_dict(_calculation)




        _breakdown = d.pop("breakdown", UNSET)
        breakdown: Union[Unset, PostCalculatePricingResponse200Breakdown]
        if isinstance(_breakdown,  Unset):
            breakdown = UNSET
        else:
            breakdown = PostCalculatePricingResponse200Breakdown.from_dict(_breakdown)




        post_calculate_pricing_response_200 = cls(
            calculation=calculation,
            breakdown=breakdown,
        )


        post_calculate_pricing_response_200.additional_properties = d
        return post_calculate_pricing_response_200

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
