from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.create_dashboard_request_widgets_item import CreateDashboardRequestWidgetsItem
  from ..models.create_dashboard_request_layout import CreateDashboardRequestLayout





T = TypeVar("T", bound="CreateDashboardRequest")



@_attrs_define
class CreateDashboardRequest:
    """ 
        Attributes:
            name (str):
            description (Union[Unset, str]):
            layout (Union[Unset, CreateDashboardRequestLayout]):
            widgets (Union[Unset, list['CreateDashboardRequestWidgetsItem']]):
            is_default (Union[Unset, bool]):
     """

    name: str
    description: Union[Unset, str] = UNSET
    layout: Union[Unset, 'CreateDashboardRequestLayout'] = UNSET
    widgets: Union[Unset, list['CreateDashboardRequestWidgetsItem']] = UNSET
    is_default: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.create_dashboard_request_widgets_item import CreateDashboardRequestWidgetsItem
        from ..models.create_dashboard_request_layout import CreateDashboardRequestLayout
        name = self.name

        description = self.description

        layout: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.layout, Unset):
            layout = self.layout.to_dict()

        widgets: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.widgets, Unset):
            widgets = []
            for widgets_item_data in self.widgets:
                widgets_item = widgets_item_data.to_dict()
                widgets.append(widgets_item)



        is_default = self.is_default


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
        })
        if description is not UNSET:
            field_dict["description"] = description
        if layout is not UNSET:
            field_dict["layout"] = layout
        if widgets is not UNSET:
            field_dict["widgets"] = widgets
        if is_default is not UNSET:
            field_dict["is_default"] = is_default

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_dashboard_request_widgets_item import CreateDashboardRequestWidgetsItem
        from ..models.create_dashboard_request_layout import CreateDashboardRequestLayout
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description", UNSET)

        _layout = d.pop("layout", UNSET)
        layout: Union[Unset, CreateDashboardRequestLayout]
        if isinstance(_layout,  Unset):
            layout = UNSET
        else:
            layout = CreateDashboardRequestLayout.from_dict(_layout)




        widgets = []
        _widgets = d.pop("widgets", UNSET)
        for widgets_item_data in (_widgets or []):
            widgets_item = CreateDashboardRequestWidgetsItem.from_dict(widgets_item_data)



            widgets.append(widgets_item)


        is_default = d.pop("is_default", UNSET)

        create_dashboard_request = cls(
            name=name,
            description=description,
            layout=layout,
            widgets=widgets,
            is_default=is_default,
        )


        create_dashboard_request.additional_properties = d
        return create_dashboard_request

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
