from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.dashboard_layout import DashboardLayout
  from ..models.widget import Widget





T = TypeVar("T", bound="Dashboard")



@_attrs_define
class Dashboard:
    """ 
        Attributes:
            dashboard_id (Union[Unset, UUID]):
            name (Union[Unset, str]):
            description (Union[Unset, str]):
            layout (Union[Unset, DashboardLayout]):
            widgets (Union[Unset, list['Widget']]):
            is_default (Union[Unset, bool]):
            created_at (Union[Unset, datetime.datetime]):
            updated_at (Union[Unset, datetime.datetime]):
     """

    dashboard_id: Union[Unset, UUID] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    layout: Union[Unset, 'DashboardLayout'] = UNSET
    widgets: Union[Unset, list['Widget']] = UNSET
    is_default: Union[Unset, bool] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dashboard_layout import DashboardLayout
        from ..models.widget import Widget
        dashboard_id: Union[Unset, str] = UNSET
        if not isinstance(self.dashboard_id, Unset):
            dashboard_id = str(self.dashboard_id)

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

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if dashboard_id is not UNSET:
            field_dict["dashboard_id"] = dashboard_id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if layout is not UNSET:
            field_dict["layout"] = layout
        if widgets is not UNSET:
            field_dict["widgets"] = widgets
        if is_default is not UNSET:
            field_dict["is_default"] = is_default
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dashboard_layout import DashboardLayout
        from ..models.widget import Widget
        d = dict(src_dict)
        _dashboard_id = d.pop("dashboard_id", UNSET)
        dashboard_id: Union[Unset, UUID]
        if isinstance(_dashboard_id,  Unset):
            dashboard_id = UNSET
        else:
            dashboard_id = UUID(_dashboard_id)




        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        _layout = d.pop("layout", UNSET)
        layout: Union[Unset, DashboardLayout]
        if isinstance(_layout,  Unset):
            layout = UNSET
        else:
            layout = DashboardLayout.from_dict(_layout)




        widgets = []
        _widgets = d.pop("widgets", UNSET)
        for widgets_item_data in (_widgets or []):
            widgets_item = Widget.from_dict(widgets_item_data)



            widgets.append(widgets_item)


        is_default = d.pop("is_default", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at,  Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)




        dashboard = cls(
            dashboard_id=dashboard_id,
            name=name,
            description=description,
            layout=layout,
            widgets=widgets,
            is_default=is_default,
            created_at=created_at,
            updated_at=updated_at,
        )


        dashboard.additional_properties = d
        return dashboard

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
