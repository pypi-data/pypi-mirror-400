from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union
from uuid import UUID

if TYPE_CHECKING:
  from ..models.widget_config import WidgetConfig
  from ..models.widget_position import WidgetPosition





T = TypeVar("T", bound="Widget")



@_attrs_define
class Widget:
    """ 
        Attributes:
            widget_id (Union[Unset, UUID]):
            widget_type (Union[Unset, str]):
            position (Union[Unset, WidgetPosition]):
            config (Union[Unset, WidgetConfig]):
     """

    widget_id: Union[Unset, UUID] = UNSET
    widget_type: Union[Unset, str] = UNSET
    position: Union[Unset, 'WidgetPosition'] = UNSET
    config: Union[Unset, 'WidgetConfig'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.widget_config import WidgetConfig
        from ..models.widget_position import WidgetPosition
        widget_id: Union[Unset, str] = UNSET
        if not isinstance(self.widget_id, Unset):
            widget_id = str(self.widget_id)

        widget_type = self.widget_type

        position: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.position, Unset):
            position = self.position.to_dict()

        config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if widget_id is not UNSET:
            field_dict["widget_id"] = widget_id
        if widget_type is not UNSET:
            field_dict["widget_type"] = widget_type
        if position is not UNSET:
            field_dict["position"] = position
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_config import WidgetConfig
        from ..models.widget_position import WidgetPosition
        d = dict(src_dict)
        _widget_id = d.pop("widget_id", UNSET)
        widget_id: Union[Unset, UUID]
        if isinstance(_widget_id,  Unset):
            widget_id = UNSET
        else:
            widget_id = UUID(_widget_id)




        widget_type = d.pop("widget_type", UNSET)

        _position = d.pop("position", UNSET)
        position: Union[Unset, WidgetPosition]
        if isinstance(_position,  Unset):
            position = UNSET
        else:
            position = WidgetPosition.from_dict(_position)




        _config = d.pop("config", UNSET)
        config: Union[Unset, WidgetConfig]
        if isinstance(_config,  Unset):
            config = UNSET
        else:
            config = WidgetConfig.from_dict(_config)




        widget = cls(
            widget_id=widget_id,
            widget_type=widget_type,
            position=position,
            config=config,
        )


        widget.additional_properties = d
        return widget

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
