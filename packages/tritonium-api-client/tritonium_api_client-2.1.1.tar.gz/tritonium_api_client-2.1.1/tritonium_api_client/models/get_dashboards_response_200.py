from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.dashboard import Dashboard





T = TypeVar("T", bound="GetDashboardsResponse200")



@_attrs_define
class GetDashboardsResponse200:
    """ 
        Attributes:
            dashboards (Union[Unset, list['Dashboard']]):
     """

    dashboards: Union[Unset, list['Dashboard']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dashboard import Dashboard
        dashboards: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.dashboards, Unset):
            dashboards = []
            for dashboards_item_data in self.dashboards:
                dashboards_item = dashboards_item_data.to_dict()
                dashboards.append(dashboards_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if dashboards is not UNSET:
            field_dict["dashboards"] = dashboards

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dashboard import Dashboard
        d = dict(src_dict)
        dashboards = []
        _dashboards = d.pop("dashboards", UNSET)
        for dashboards_item_data in (_dashboards or []):
            dashboards_item = Dashboard.from_dict(dashboards_item_data)



            dashboards.append(dashboards_item)


        get_dashboards_response_200 = cls(
            dashboards=dashboards,
        )


        get_dashboards_response_200.additional_properties = d
        return get_dashboards_response_200

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
