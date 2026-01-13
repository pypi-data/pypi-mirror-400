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






T = TypeVar("T", bound="ReviewSummary")



@_attrs_define
class ReviewSummary:
    """ 
        Attributes:
            review_id (Union[Unset, str]):
            title (Union[Unset, str]):
            body (Union[Unset, str]):
            rating (Union[Unset, int]):
            sentiment (Union[Unset, str]):
            locale (Union[Unset, str]):
            storefront (Union[Unset, str]):
            created_at (Union[Unset, datetime.datetime]):
     """

    review_id: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    body: Union[Unset, str] = UNSET
    rating: Union[Unset, int] = UNSET
    sentiment: Union[Unset, str] = UNSET
    locale: Union[Unset, str] = UNSET
    storefront: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        review_id = self.review_id

        title = self.title

        body = self.body

        rating = self.rating

        sentiment = self.sentiment

        locale = self.locale

        storefront = self.storefront

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if review_id is not UNSET:
            field_dict["review_id"] = review_id
        if title is not UNSET:
            field_dict["title"] = title
        if body is not UNSET:
            field_dict["body"] = body
        if rating is not UNSET:
            field_dict["rating"] = rating
        if sentiment is not UNSET:
            field_dict["sentiment"] = sentiment
        if locale is not UNSET:
            field_dict["locale"] = locale
        if storefront is not UNSET:
            field_dict["storefront"] = storefront
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        review_id = d.pop("review_id", UNSET)

        title = d.pop("title", UNSET)

        body = d.pop("body", UNSET)

        rating = d.pop("rating", UNSET)

        sentiment = d.pop("sentiment", UNSET)

        locale = d.pop("locale", UNSET)

        storefront = d.pop("storefront", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        review_summary = cls(
            review_id=review_id,
            title=title,
            body=body,
            rating=rating,
            sentiment=sentiment,
            locale=locale,
            storefront=storefront,
            created_at=created_at,
        )


        review_summary.additional_properties = d
        return review_summary

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
