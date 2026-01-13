from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.get_detect_country_response_200_pricing_info import GetDetectCountryResponse200PricingInfo





T = TypeVar("T", bound="GetDetectCountryResponse200")



@_attrs_define
class GetDetectCountryResponse200:
    """ 
        Attributes:
            detected_country (Union[Unset, str]): ISO 3166-1 alpha-2 country code Example: US.
            pricing_info (Union[Unset, GetDetectCountryResponse200PricingInfo]):
            note (Union[Unset, str]):  Example: Final price will be determined by your payment card country.
     """

    detected_country: Union[Unset, str] = UNSET
    pricing_info: Union[Unset, 'GetDetectCountryResponse200PricingInfo'] = UNSET
    note: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_detect_country_response_200_pricing_info import GetDetectCountryResponse200PricingInfo
        detected_country = self.detected_country

        pricing_info: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.pricing_info, Unset):
            pricing_info = self.pricing_info.to_dict()

        note = self.note


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if detected_country is not UNSET:
            field_dict["detected_country"] = detected_country
        if pricing_info is not UNSET:
            field_dict["pricing_info"] = pricing_info
        if note is not UNSET:
            field_dict["note"] = note

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_detect_country_response_200_pricing_info import GetDetectCountryResponse200PricingInfo
        d = dict(src_dict)
        detected_country = d.pop("detected_country", UNSET)

        _pricing_info = d.pop("pricing_info", UNSET)
        pricing_info: Union[Unset, GetDetectCountryResponse200PricingInfo]
        if isinstance(_pricing_info,  Unset):
            pricing_info = UNSET
        else:
            pricing_info = GetDetectCountryResponse200PricingInfo.from_dict(_pricing_info)




        note = d.pop("note", UNSET)

        get_detect_country_response_200 = cls(
            detected_country=detected_country,
            pricing_info=pricing_info,
            note=note,
        )


        get_detect_country_response_200.additional_properties = d
        return get_detect_country_response_200

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
