from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.slack_channel import SlackChannel





T = TypeVar("T", bound="GetSlackChannelsResponse200")



@_attrs_define
class GetSlackChannelsResponse200:
    """ 
        Attributes:
            channels (Union[Unset, list['SlackChannel']]):
     """

    channels: Union[Unset, list['SlackChannel']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.slack_channel import SlackChannel
        channels: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.channels, Unset):
            channels = []
            for channels_item_data in self.channels:
                channels_item = channels_item_data.to_dict()
                channels.append(channels_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if channels is not UNSET:
            field_dict["channels"] = channels

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.slack_channel import SlackChannel
        d = dict(src_dict)
        channels = []
        _channels = d.pop("channels", UNSET)
        for channels_item_data in (_channels or []):
            channels_item = SlackChannel.from_dict(channels_item_data)



            channels.append(channels_item)


        get_slack_channels_response_200 = cls(
            channels=channels,
        )


        get_slack_channels_response_200.additional_properties = d
        return get_slack_channels_response_200

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
