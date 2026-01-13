from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.post_slack_message_body_blocks_item import PostSlackMessageBodyBlocksItem





T = TypeVar("T", bound="PostSlackMessageBody")



@_attrs_define
class PostSlackMessageBody:
    """ 
        Attributes:
            text (str):
            channel (Union[Unset, str]):
            blocks (Union[Unset, list['PostSlackMessageBodyBlocksItem']]):
     """

    text: str
    channel: Union[Unset, str] = UNSET
    blocks: Union[Unset, list['PostSlackMessageBodyBlocksItem']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.post_slack_message_body_blocks_item import PostSlackMessageBodyBlocksItem
        text = self.text

        channel = self.channel

        blocks: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.blocks, Unset):
            blocks = []
            for blocks_item_data in self.blocks:
                blocks_item = blocks_item_data.to_dict()
                blocks.append(blocks_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "text": text,
        })
        if channel is not UNSET:
            field_dict["channel"] = channel
        if blocks is not UNSET:
            field_dict["blocks"] = blocks

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_slack_message_body_blocks_item import PostSlackMessageBodyBlocksItem
        d = dict(src_dict)
        text = d.pop("text")

        channel = d.pop("channel", UNSET)

        blocks = []
        _blocks = d.pop("blocks", UNSET)
        for blocks_item_data in (_blocks or []):
            blocks_item = PostSlackMessageBodyBlocksItem.from_dict(blocks_item_data)



            blocks.append(blocks_item)


        post_slack_message_body = cls(
            text=text,
            channel=channel,
            blocks=blocks,
        )


        post_slack_message_body.additional_properties = d
        return post_slack_message_body

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
