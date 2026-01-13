from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.insight import Insight





T = TypeVar("T", bound="GetTenantInsightsResponse200")



@_attrs_define
class GetTenantInsightsResponse200:
    """ 
        Attributes:
            items (Union[Unset, list['Insight']]):
            next_cursor (Union[Unset, str]):
     """

    items: Union[Unset, list['Insight']] = UNSET
    next_cursor: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.insight import Insight
        items: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)



        next_cursor = self.next_cursor


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if items is not UNSET:
            field_dict["items"] = items
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.insight import Insight
        d = dict(src_dict)
        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in (_items or []):
            items_item = Insight.from_dict(items_item_data)



            items.append(items_item)


        next_cursor = d.pop("next_cursor", UNSET)

        get_tenant_insights_response_200 = cls(
            items=items,
            next_cursor=next_cursor,
        )


        get_tenant_insights_response_200.additional_properties = d
        return get_tenant_insights_response_200

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
