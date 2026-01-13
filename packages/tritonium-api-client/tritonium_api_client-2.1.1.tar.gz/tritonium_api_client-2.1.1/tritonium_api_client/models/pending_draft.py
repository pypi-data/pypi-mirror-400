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

if TYPE_CHECKING:
  from ..models.pending_draft_review_snapshot import PendingDraftReviewSnapshot





T = TypeVar("T", bound="PendingDraft")



@_attrs_define
class PendingDraft:
    """ 
        Attributes:
            draft_id (Union[Unset, str]): Unique identifier for the draft.
            review_id (Union[Unset, str]): ID of the review this draft is replying to.
            app_name (Union[Unset, str]): Name of the app the review belongs to.
            reply_text (Union[Unset, str]): AI-generated reply text.
            review_snapshot (Union[Unset, PendingDraftReviewSnapshot]): Snapshot of the original review.
            created_at (Union[Unset, datetime.datetime]): When the draft was created.
     """

    draft_id: Union[Unset, str] = UNSET
    review_id: Union[Unset, str] = UNSET
    app_name: Union[Unset, str] = UNSET
    reply_text: Union[Unset, str] = UNSET
    review_snapshot: Union[Unset, 'PendingDraftReviewSnapshot'] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.pending_draft_review_snapshot import PendingDraftReviewSnapshot
        draft_id = self.draft_id

        review_id = self.review_id

        app_name = self.app_name

        reply_text = self.reply_text

        review_snapshot: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.review_snapshot, Unset):
            review_snapshot = self.review_snapshot.to_dict()

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if draft_id is not UNSET:
            field_dict["draft_id"] = draft_id
        if review_id is not UNSET:
            field_dict["review_id"] = review_id
        if app_name is not UNSET:
            field_dict["app_name"] = app_name
        if reply_text is not UNSET:
            field_dict["reply_text"] = reply_text
        if review_snapshot is not UNSET:
            field_dict["review_snapshot"] = review_snapshot
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pending_draft_review_snapshot import PendingDraftReviewSnapshot
        d = dict(src_dict)
        draft_id = d.pop("draft_id", UNSET)

        review_id = d.pop("review_id", UNSET)

        app_name = d.pop("app_name", UNSET)

        reply_text = d.pop("reply_text", UNSET)

        _review_snapshot = d.pop("review_snapshot", UNSET)
        review_snapshot: Union[Unset, PendingDraftReviewSnapshot]
        if isinstance(_review_snapshot,  Unset):
            review_snapshot = UNSET
        else:
            review_snapshot = PendingDraftReviewSnapshot.from_dict(_review_snapshot)




        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        pending_draft = cls(
            draft_id=draft_id,
            review_id=review_id,
            app_name=app_name,
            reply_text=reply_text,
            review_snapshot=review_snapshot,
            created_at=created_at,
        )


        pending_draft.additional_properties = d
        return pending_draft

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
