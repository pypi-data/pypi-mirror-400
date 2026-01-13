from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="ReviewReplyDraft")



@_attrs_define
class ReviewReplyDraft:
    """ 
        Attributes:
            reply_text (Union[Unset, str]):
            tone (Union[Unset, str]):
            suggested_actions (Union[Unset, list[str]]):
     """

    reply_text: Union[Unset, str] = UNSET
    tone: Union[Unset, str] = UNSET
    suggested_actions: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        reply_text = self.reply_text

        tone = self.tone

        suggested_actions: Union[Unset, list[str]] = UNSET
        if not isinstance(self.suggested_actions, Unset):
            suggested_actions = self.suggested_actions




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if reply_text is not UNSET:
            field_dict["reply_text"] = reply_text
        if tone is not UNSET:
            field_dict["tone"] = tone
        if suggested_actions is not UNSET:
            field_dict["suggested_actions"] = suggested_actions

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reply_text = d.pop("reply_text", UNSET)

        tone = d.pop("tone", UNSET)

        suggested_actions = cast(list[str], d.pop("suggested_actions", UNSET))


        review_reply_draft = cls(
            reply_text=reply_text,
            tone=tone,
            suggested_actions=suggested_actions,
        )


        review_reply_draft.additional_properties = d
        return review_reply_draft

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
