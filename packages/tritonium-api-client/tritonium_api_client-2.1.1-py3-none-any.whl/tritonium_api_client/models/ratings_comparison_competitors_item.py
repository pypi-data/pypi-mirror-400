from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.competitor import Competitor
  from ..models.rating_summary import RatingSummary





T = TypeVar("T", bound="RatingsComparisonCompetitorsItem")



@_attrs_define
class RatingsComparisonCompetitorsItem:
    """ 
        Attributes:
            competitor (Union[Unset, Competitor]):
            rating (Union[Unset, RatingSummary]):
     """

    competitor: Union[Unset, 'Competitor'] = UNSET
    rating: Union[Unset, 'RatingSummary'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.competitor import Competitor
        from ..models.rating_summary import RatingSummary
        competitor: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.competitor, Unset):
            competitor = self.competitor.to_dict()

        rating: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.rating, Unset):
            rating = self.rating.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if competitor is not UNSET:
            field_dict["competitor"] = competitor
        if rating is not UNSET:
            field_dict["rating"] = rating

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.competitor import Competitor
        from ..models.rating_summary import RatingSummary
        d = dict(src_dict)
        _competitor = d.pop("competitor", UNSET)
        competitor: Union[Unset, Competitor]
        if isinstance(_competitor,  Unset):
            competitor = UNSET
        else:
            competitor = Competitor.from_dict(_competitor)




        _rating = d.pop("rating", UNSET)
        rating: Union[Unset, RatingSummary]
        if isinstance(_rating,  Unset):
            rating = UNSET
        else:
            rating = RatingSummary.from_dict(_rating)




        ratings_comparison_competitors_item = cls(
            competitor=competitor,
            rating=rating,
        )


        ratings_comparison_competitors_item.additional_properties = d
        return ratings_comparison_competitors_item

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
