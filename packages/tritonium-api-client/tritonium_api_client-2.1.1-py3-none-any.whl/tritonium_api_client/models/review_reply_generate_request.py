from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="ReviewReplyGenerateRequest")



@_attrs_define
class ReviewReplyGenerateRequest:
    """ 
        Attributes:
            issue_type (Union[Unset, str]):
            known_issues (Union[Unset, list[str]]):
            fix_eta (Union[Unset, str]):
            similar_review_count (Union[Unset, int]):
            user_segment (Union[Unset, str]):
     """

    issue_type: Union[Unset, str] = UNSET
    known_issues: Union[Unset, list[str]] = UNSET
    fix_eta: Union[Unset, str] = UNSET
    similar_review_count: Union[Unset, int] = UNSET
    user_segment: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        issue_type = self.issue_type

        known_issues: Union[Unset, list[str]] = UNSET
        if not isinstance(self.known_issues, Unset):
            known_issues = self.known_issues



        fix_eta = self.fix_eta

        similar_review_count = self.similar_review_count

        user_segment = self.user_segment


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if issue_type is not UNSET:
            field_dict["issue_type"] = issue_type
        if known_issues is not UNSET:
            field_dict["known_issues"] = known_issues
        if fix_eta is not UNSET:
            field_dict["fix_eta"] = fix_eta
        if similar_review_count is not UNSET:
            field_dict["similar_review_count"] = similar_review_count
        if user_segment is not UNSET:
            field_dict["user_segment"] = user_segment

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        issue_type = d.pop("issue_type", UNSET)

        known_issues = cast(list[str], d.pop("known_issues", UNSET))


        fix_eta = d.pop("fix_eta", UNSET)

        similar_review_count = d.pop("similar_review_count", UNSET)

        user_segment = d.pop("user_segment", UNSET)

        review_reply_generate_request = cls(
            issue_type=issue_type,
            known_issues=known_issues,
            fix_eta=fix_eta,
            similar_review_count=similar_review_count,
            user_segment=user_segment,
        )


        review_reply_generate_request.additional_properties = d
        return review_reply_generate_request

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
