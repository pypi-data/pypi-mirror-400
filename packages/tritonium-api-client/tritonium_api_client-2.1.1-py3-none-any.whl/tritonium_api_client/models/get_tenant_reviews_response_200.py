from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.review_summary import ReviewSummary





T = TypeVar("T", bound="GetTenantReviewsResponse200")



@_attrs_define
class GetTenantReviewsResponse200:
    """ 
        Attributes:
            reviews (Union[Unset, list['ReviewSummary']]):
            next_cursor (Union[Unset, str]):
     """

    reviews: Union[Unset, list['ReviewSummary']] = UNSET
    next_cursor: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.review_summary import ReviewSummary
        reviews: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.reviews, Unset):
            reviews = []
            for reviews_item_data in self.reviews:
                reviews_item = reviews_item_data.to_dict()
                reviews.append(reviews_item)



        next_cursor = self.next_cursor


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if reviews is not UNSET:
            field_dict["reviews"] = reviews
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.review_summary import ReviewSummary
        d = dict(src_dict)
        reviews = []
        _reviews = d.pop("reviews", UNSET)
        for reviews_item_data in (_reviews or []):
            reviews_item = ReviewSummary.from_dict(reviews_item_data)



            reviews.append(reviews_item)


        next_cursor = d.pop("next_cursor", UNSET)

        get_tenant_reviews_response_200 = cls(
            reviews=reviews,
            next_cursor=next_cursor,
        )


        get_tenant_reviews_response_200.additional_properties = d
        return get_tenant_reviews_response_200

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
