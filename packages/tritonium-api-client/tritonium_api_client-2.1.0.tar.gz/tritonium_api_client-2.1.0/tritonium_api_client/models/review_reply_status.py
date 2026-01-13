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






T = TypeVar("T", bound="ReviewReplyStatus")



@_attrs_define
class ReviewReplyStatus:
    """ 
        Attributes:
            review_id (Union[Unset, str]):
            status (Union[Unset, str]):
            posted_at (Union[Unset, datetime.datetime]):
            source_reference (Union[Unset, str]):
     """

    review_id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    posted_at: Union[Unset, datetime.datetime] = UNSET
    source_reference: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        review_id = self.review_id

        status = self.status

        posted_at: Union[Unset, str] = UNSET
        if not isinstance(self.posted_at, Unset):
            posted_at = self.posted_at.isoformat()

        source_reference = self.source_reference


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if review_id is not UNSET:
            field_dict["review_id"] = review_id
        if status is not UNSET:
            field_dict["status"] = status
        if posted_at is not UNSET:
            field_dict["posted_at"] = posted_at
        if source_reference is not UNSET:
            field_dict["source_reference"] = source_reference

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        review_id = d.pop("review_id", UNSET)

        status = d.pop("status", UNSET)

        _posted_at = d.pop("posted_at", UNSET)
        posted_at: Union[Unset, datetime.datetime]
        if isinstance(_posted_at,  Unset):
            posted_at = UNSET
        else:
            posted_at = isoparse(_posted_at)




        source_reference = d.pop("source_reference", UNSET)

        review_reply_status = cls(
            review_id=review_id,
            status=status,
            posted_at=posted_at,
            source_reference=source_reference,
        )


        review_reply_status.additional_properties = d
        return review_reply_status

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
