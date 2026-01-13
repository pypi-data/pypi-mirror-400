from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.widget_type import WidgetType





T = TypeVar("T", bound="GetWidgetTypesResponse200")



@_attrs_define
class GetWidgetTypesResponse200:
    """ 
        Attributes:
            widget_types (Union[Unset, list['WidgetType']]):
     """

    widget_types: Union[Unset, list['WidgetType']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.widget_type import WidgetType
        widget_types: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.widget_types, Unset):
            widget_types = []
            for widget_types_item_data in self.widget_types:
                widget_types_item = widget_types_item_data.to_dict()
                widget_types.append(widget_types_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if widget_types is not UNSET:
            field_dict["widget_types"] = widget_types

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_type import WidgetType
        d = dict(src_dict)
        widget_types = []
        _widget_types = d.pop("widget_types", UNSET)
        for widget_types_item_data in (_widget_types or []):
            widget_types_item = WidgetType.from_dict(widget_types_item_data)



            widget_types.append(widget_types_item)


        get_widget_types_response_200 = cls(
            widget_types=widget_types,
        )


        get_widget_types_response_200.additional_properties = d
        return get_widget_types_response_200

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
