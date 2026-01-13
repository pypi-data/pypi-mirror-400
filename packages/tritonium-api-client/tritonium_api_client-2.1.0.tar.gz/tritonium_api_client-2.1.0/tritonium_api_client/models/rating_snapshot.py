from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime






T = TypeVar("T", bound="RatingSnapshot")



@_attrs_define
class RatingSnapshot:
    """ 
        Attributes:
            recorded_at (Union[Unset, datetime.datetime]):
            platform (Union[Unset, str]):
            rating (Union[Unset, float]):
            rating_count (Union[Unset, int]):
     """

    recorded_at: Union[Unset, datetime.datetime] = UNSET
    platform: Union[Unset, str] = UNSET
    rating: Union[Unset, float] = UNSET
    rating_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        recorded_at: Union[Unset, str] = UNSET
        if not isinstance(self.recorded_at, Unset):
            recorded_at = self.recorded_at.isoformat()

        platform = self.platform

        rating = self.rating

        rating_count = self.rating_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if recorded_at is not UNSET:
            field_dict["recorded_at"] = recorded_at
        if platform is not UNSET:
            field_dict["platform"] = platform
        if rating is not UNSET:
            field_dict["rating"] = rating
        if rating_count is not UNSET:
            field_dict["rating_count"] = rating_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _recorded_at = d.pop("recorded_at", UNSET)
        recorded_at: Union[Unset, datetime.datetime]
        if isinstance(_recorded_at,  Unset):
            recorded_at = UNSET
        else:
            recorded_at = isoparse(_recorded_at)




        platform = d.pop("platform", UNSET)

        rating = d.pop("rating", UNSET)

        rating_count = d.pop("rating_count", UNSET)

        rating_snapshot = cls(
            recorded_at=recorded_at,
            platform=platform,
            rating=rating,
            rating_count=rating_count,
        )


        rating_snapshot.additional_properties = d
        return rating_snapshot

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
