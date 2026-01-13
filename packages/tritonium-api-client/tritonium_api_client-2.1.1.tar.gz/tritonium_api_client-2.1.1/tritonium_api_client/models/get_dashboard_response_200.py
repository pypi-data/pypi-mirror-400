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





T = TypeVar("T", bound="GetDashboardResponse200")



@_attrs_define
class GetDashboardResponse200:
    """ 
        Attributes:
            dashboard (Union[Unset, Dashboard]):
     """

    dashboard: Union[Unset, 'Dashboard'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.dashboard import Dashboard
        dashboard: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.dashboard, Unset):
            dashboard = self.dashboard.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if dashboard is not UNSET:
            field_dict["dashboard"] = dashboard

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dashboard import Dashboard
        d = dict(src_dict)
        _dashboard = d.pop("dashboard", UNSET)
        dashboard: Union[Unset, Dashboard]
        if isinstance(_dashboard,  Unset):
            dashboard = UNSET
        else:
            dashboard = Dashboard.from_dict(_dashboard)




        get_dashboard_response_200 = cls(
            dashboard=dashboard,
        )


        get_dashboard_response_200.additional_properties = d
        return get_dashboard_response_200

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
