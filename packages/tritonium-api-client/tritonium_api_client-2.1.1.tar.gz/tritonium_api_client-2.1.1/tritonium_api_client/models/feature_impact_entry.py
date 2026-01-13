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






T = TypeVar("T", bound="FeatureImpactEntry")



@_attrs_define
class FeatureImpactEntry:
    """ 
        Attributes:
            feature (Union[Unset, str]):
            impact_score (Union[Unset, float]):
            sentiment (Union[Unset, str]):
            notes (Union[Unset, str]):
            recorded_at (Union[Unset, datetime.datetime]):
     """

    feature: Union[Unset, str] = UNSET
    impact_score: Union[Unset, float] = UNSET
    sentiment: Union[Unset, str] = UNSET
    notes: Union[Unset, str] = UNSET
    recorded_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        feature = self.feature

        impact_score = self.impact_score

        sentiment = self.sentiment

        notes = self.notes

        recorded_at: Union[Unset, str] = UNSET
        if not isinstance(self.recorded_at, Unset):
            recorded_at = self.recorded_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if feature is not UNSET:
            field_dict["feature"] = feature
        if impact_score is not UNSET:
            field_dict["impact_score"] = impact_score
        if sentiment is not UNSET:
            field_dict["sentiment"] = sentiment
        if notes is not UNSET:
            field_dict["notes"] = notes
        if recorded_at is not UNSET:
            field_dict["recorded_at"] = recorded_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        feature = d.pop("feature", UNSET)

        impact_score = d.pop("impact_score", UNSET)

        sentiment = d.pop("sentiment", UNSET)

        notes = d.pop("notes", UNSET)

        _recorded_at = d.pop("recorded_at", UNSET)
        recorded_at: Union[Unset, datetime.datetime]
        if isinstance(_recorded_at,  Unset):
            recorded_at = UNSET
        else:
            recorded_at = isoparse(_recorded_at)




        feature_impact_entry = cls(
            feature=feature,
            impact_score=impact_score,
            sentiment=sentiment,
            notes=notes,
            recorded_at=recorded_at,
        )


        feature_impact_entry.additional_properties = d
        return feature_impact_entry

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
