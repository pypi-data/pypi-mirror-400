from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="RatingSummary")



@_attrs_define
class RatingSummary:
    """ 
        Attributes:
            current_rating (Union[Unset, float]):
            rating_count (Union[Unset, int]):
            change_1d (Union[Unset, float]):
            change_7d (Union[Unset, float]):
            change_30d (Union[Unset, float]):
     """

    current_rating: Union[Unset, float] = UNSET
    rating_count: Union[Unset, int] = UNSET
    change_1d: Union[Unset, float] = UNSET
    change_7d: Union[Unset, float] = UNSET
    change_30d: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        current_rating = self.current_rating

        rating_count = self.rating_count

        change_1d = self.change_1d

        change_7d = self.change_7d

        change_30d = self.change_30d


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if current_rating is not UNSET:
            field_dict["current_rating"] = current_rating
        if rating_count is not UNSET:
            field_dict["rating_count"] = rating_count
        if change_1d is not UNSET:
            field_dict["change_1d"] = change_1d
        if change_7d is not UNSET:
            field_dict["change_7d"] = change_7d
        if change_30d is not UNSET:
            field_dict["change_30d"] = change_30d

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_rating = d.pop("current_rating", UNSET)

        rating_count = d.pop("rating_count", UNSET)

        change_1d = d.pop("change_1d", UNSET)

        change_7d = d.pop("change_7d", UNSET)

        change_30d = d.pop("change_30d", UNSET)

        rating_summary = cls(
            current_rating=current_rating,
            rating_count=rating_count,
            change_1d=change_1d,
            change_7d=change_7d,
            change_30d=change_30d,
        )


        rating_summary.additional_properties = d
        return rating_summary

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
