from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.widget_type_default_size import WidgetTypeDefaultSize





T = TypeVar("T", bound="WidgetType")



@_attrs_define
class WidgetType:
    """ 
        Attributes:
            type_ (Union[Unset, str]):
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            icon (Union[Unset, str]):
            category (Union[Unset, str]):
            default_size (Union[Unset, WidgetTypeDefaultSize]):
            min_width (Union[Unset, int]):
            min_height (Union[Unset, int]):
            max_width (Union[Unset, int]):
            max_height (Union[Unset, int]):
            configurable_fields (Union[Unset, list[str]]):
     """

    type_: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    icon: Union[Unset, str] = UNSET
    category: Union[Unset, str] = UNSET
    default_size: Union[Unset, 'WidgetTypeDefaultSize'] = UNSET
    min_width: Union[Unset, int] = UNSET
    min_height: Union[Unset, int] = UNSET
    max_width: Union[Unset, int] = UNSET
    max_height: Union[Unset, int] = UNSET
    configurable_fields: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.widget_type_default_size import WidgetTypeDefaultSize
        type_ = self.type_

        name = self.name

        description = self.description

        icon = self.icon

        category = self.category

        default_size: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.default_size, Unset):
            default_size = self.default_size.to_dict()

        min_width = self.min_width

        min_height = self.min_height

        max_width = self.max_width

        max_height = self.max_height

        configurable_fields: Union[Unset, list[str]] = UNSET
        if not isinstance(self.configurable_fields, Unset):
            configurable_fields = self.configurable_fields




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if type_ is not UNSET:
            field_dict["type"] = type_
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if icon is not UNSET:
            field_dict["icon"] = icon
        if category is not UNSET:
            field_dict["category"] = category
        if default_size is not UNSET:
            field_dict["default_size"] = default_size
        if min_width is not UNSET:
            field_dict["min_width"] = min_width
        if min_height is not UNSET:
            field_dict["min_height"] = min_height
        if max_width is not UNSET:
            field_dict["max_width"] = max_width
        if max_height is not UNSET:
            field_dict["max_height"] = max_height
        if configurable_fields is not UNSET:
            field_dict["configurable_fields"] = configurable_fields

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_type_default_size import WidgetTypeDefaultSize
        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        icon = d.pop("icon", UNSET)

        category = d.pop("category", UNSET)

        _default_size = d.pop("default_size", UNSET)
        default_size: Union[Unset, WidgetTypeDefaultSize]
        if isinstance(_default_size,  Unset):
            default_size = UNSET
        else:
            default_size = WidgetTypeDefaultSize.from_dict(_default_size)




        min_width = d.pop("min_width", UNSET)

        min_height = d.pop("min_height", UNSET)

        max_width = d.pop("max_width", UNSET)

        max_height = d.pop("max_height", UNSET)

        configurable_fields = cast(list[str], d.pop("configurable_fields", UNSET))


        widget_type = cls(
            type_=type_,
            name=name,
            description=description,
            icon=icon,
            category=category,
            default_size=default_size,
            min_width=min_width,
            min_height=min_height,
            max_width=max_width,
            max_height=max_height,
            configurable_fields=configurable_fields,
        )


        widget_type.additional_properties = d
        return widget_type

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
