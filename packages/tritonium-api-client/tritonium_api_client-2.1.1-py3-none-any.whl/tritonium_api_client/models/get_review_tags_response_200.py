from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.review_tag import ReviewTag





T = TypeVar("T", bound="GetReviewTagsResponse200")



@_attrs_define
class GetReviewTagsResponse200:
    """ 
        Attributes:
            tags (Union[Unset, list['ReviewTag']]):
     """

    tags: Union[Unset, list['ReviewTag']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.review_tag import ReviewTag
        tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.review_tag import ReviewTag
        d = dict(src_dict)
        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in (_tags or []):
            tags_item = ReviewTag.from_dict(tags_item_data)



            tags.append(tags_item)


        get_review_tags_response_200 = cls(
            tags=tags,
        )


        get_review_tags_response_200.additional_properties = d
        return get_review_tags_response_200

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
