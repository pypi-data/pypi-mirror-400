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





T = TypeVar("T", bound="GetReviewTagResponse200")



@_attrs_define
class GetReviewTagResponse200:
    """ 
        Attributes:
            tag (Union[Unset, ReviewTag]):
     """

    tag: Union[Unset, 'ReviewTag'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.review_tag import ReviewTag
        tag: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tag, Unset):
            tag = self.tag.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if tag is not UNSET:
            field_dict["tag"] = tag

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.review_tag import ReviewTag
        d = dict(src_dict)
        _tag = d.pop("tag", UNSET)
        tag: Union[Unset, ReviewTag]
        if isinstance(_tag,  Unset):
            tag = UNSET
        else:
            tag = ReviewTag.from_dict(_tag)




        get_review_tag_response_200 = cls(
            tag=tag,
        )


        get_review_tag_response_200.additional_properties = d
        return get_review_tag_response_200

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
