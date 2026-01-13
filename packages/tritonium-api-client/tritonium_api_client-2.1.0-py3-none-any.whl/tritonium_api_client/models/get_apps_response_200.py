from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.app_summary import AppSummary





T = TypeVar("T", bound="GetAppsResponse200")



@_attrs_define
class GetAppsResponse200:
    """ 
        Attributes:
            apps (Union[Unset, list['AppSummary']]):
            count (Union[Unset, int]):
     """

    apps: Union[Unset, list['AppSummary']] = UNSET
    count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.app_summary import AppSummary
        apps: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.apps, Unset):
            apps = []
            for apps_item_data in self.apps:
                apps_item = apps_item_data.to_dict()
                apps.append(apps_item)



        count = self.count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if apps is not UNSET:
            field_dict["apps"] = apps
        if count is not UNSET:
            field_dict["count"] = count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.app_summary import AppSummary
        d = dict(src_dict)
        apps = []
        _apps = d.pop("apps", UNSET)
        for apps_item_data in (_apps or []):
            apps_item = AppSummary.from_dict(apps_item_data)



            apps.append(apps_item)


        count = d.pop("count", UNSET)

        get_apps_response_200 = cls(
            apps=apps,
            count=count,
        )


        get_apps_response_200.additional_properties = d
        return get_apps_response_200

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
