from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="PendingDraftReviewSnapshot")



@_attrs_define
class PendingDraftReviewSnapshot:
    """ Snapshot of the original review.

        Attributes:
            rating (Union[Unset, int]):
            content (Union[Unset, str]):
            author (Union[Unset, str]):
     """

    rating: Union[Unset, int] = UNSET
    content: Union[Unset, str] = UNSET
    author: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        rating = self.rating

        content = self.content

        author = self.author


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if rating is not UNSET:
            field_dict["rating"] = rating
        if content is not UNSET:
            field_dict["content"] = content
        if author is not UNSET:
            field_dict["author"] = author

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        rating = d.pop("rating", UNSET)

        content = d.pop("content", UNSET)

        author = d.pop("author", UNSET)

        pending_draft_review_snapshot = cls(
            rating=rating,
            content=content,
            author=author,
        )


        pending_draft_review_snapshot.additional_properties = d
        return pending_draft_review_snapshot

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
