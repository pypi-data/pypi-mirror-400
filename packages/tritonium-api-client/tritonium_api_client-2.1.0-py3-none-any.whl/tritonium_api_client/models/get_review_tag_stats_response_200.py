from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.get_review_tag_stats_response_200_stats_item import GetReviewTagStatsResponse200StatsItem





T = TypeVar("T", bound="GetReviewTagStatsResponse200")



@_attrs_define
class GetReviewTagStatsResponse200:
    """ 
        Attributes:
            stats (Union[Unset, list['GetReviewTagStatsResponse200StatsItem']]):
     """

    stats: Union[Unset, list['GetReviewTagStatsResponse200StatsItem']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_review_tag_stats_response_200_stats_item import GetReviewTagStatsResponse200StatsItem
        stats: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.stats, Unset):
            stats = []
            for stats_item_data in self.stats:
                stats_item = stats_item_data.to_dict()
                stats.append(stats_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if stats is not UNSET:
            field_dict["stats"] = stats

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_review_tag_stats_response_200_stats_item import GetReviewTagStatsResponse200StatsItem
        d = dict(src_dict)
        stats = []
        _stats = d.pop("stats", UNSET)
        for stats_item_data in (_stats or []):
            stats_item = GetReviewTagStatsResponse200StatsItem.from_dict(stats_item_data)



            stats.append(stats_item)


        get_review_tag_stats_response_200 = cls(
            stats=stats,
        )


        get_review_tag_stats_response_200.additional_properties = d
        return get_review_tag_stats_response_200

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
