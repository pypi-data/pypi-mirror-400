from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.ratings_comparison_competitors_item import RatingsComparisonCompetitorsItem
  from ..models.rating_summary import RatingSummary





T = TypeVar("T", bound="RatingsComparison")



@_attrs_define
class RatingsComparison:
    """ 
        Attributes:
            app (Union[Unset, RatingSummary]):
            competitors (Union[Unset, list['RatingsComparisonCompetitorsItem']]):
     """

    app: Union[Unset, 'RatingSummary'] = UNSET
    competitors: Union[Unset, list['RatingsComparisonCompetitorsItem']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.ratings_comparison_competitors_item import RatingsComparisonCompetitorsItem
        from ..models.rating_summary import RatingSummary
        app: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.app, Unset):
            app = self.app.to_dict()

        competitors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.competitors, Unset):
            competitors = []
            for competitors_item_data in self.competitors:
                competitors_item = competitors_item_data.to_dict()
                competitors.append(competitors_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if app is not UNSET:
            field_dict["app"] = app
        if competitors is not UNSET:
            field_dict["competitors"] = competitors

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ratings_comparison_competitors_item import RatingsComparisonCompetitorsItem
        from ..models.rating_summary import RatingSummary
        d = dict(src_dict)
        _app = d.pop("app", UNSET)
        app: Union[Unset, RatingSummary]
        if isinstance(_app,  Unset):
            app = UNSET
        else:
            app = RatingSummary.from_dict(_app)




        competitors = []
        _competitors = d.pop("competitors", UNSET)
        for competitors_item_data in (_competitors or []):
            competitors_item = RatingsComparisonCompetitorsItem.from_dict(competitors_item_data)



            competitors.append(competitors_item)


        ratings_comparison = cls(
            app=app,
            competitors=competitors,
        )


        ratings_comparison.additional_properties = d
        return ratings_comparison

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
