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
  from ..models.update_auto_tag_rule_request_conditions_item import UpdateAutoTagRuleRequestConditionsItem





T = TypeVar("T", bound="UpdateAutoTagRuleRequest")



@_attrs_define
class UpdateAutoTagRuleRequest:
    """ 
        Attributes:
            name (Union[Unset, str]):
            tag_id (Union[Unset, UUID]):
            conditions (Union[Unset, list['UpdateAutoTagRuleRequestConditionsItem']]):
            enabled (Union[Unset, bool]):
     """

    name: Union[Unset, str] = UNSET
    tag_id: Union[Unset, UUID] = UNSET
    conditions: Union[Unset, list['UpdateAutoTagRuleRequestConditionsItem']] = UNSET
    enabled: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.update_auto_tag_rule_request_conditions_item import UpdateAutoTagRuleRequestConditionsItem
        name = self.name

        tag_id: Union[Unset, str] = UNSET
        if not isinstance(self.tag_id, Unset):
            tag_id = str(self.tag_id)

        conditions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.conditions, Unset):
            conditions = []
            for conditions_item_data in self.conditions:
                conditions_item = conditions_item_data.to_dict()
                conditions.append(conditions_item)



        enabled = self.enabled


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if tag_id is not UNSET:
            field_dict["tag_id"] = tag_id
        if conditions is not UNSET:
            field_dict["conditions"] = conditions
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_auto_tag_rule_request_conditions_item import UpdateAutoTagRuleRequestConditionsItem
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        _tag_id = d.pop("tag_id", UNSET)
        tag_id: Union[Unset, UUID]
        if isinstance(_tag_id,  Unset):
            tag_id = UNSET
        else:
            tag_id = UUID(_tag_id)




        conditions = []
        _conditions = d.pop("conditions", UNSET)
        for conditions_item_data in (_conditions or []):
            conditions_item = UpdateAutoTagRuleRequestConditionsItem.from_dict(conditions_item_data)



            conditions.append(conditions_item)


        enabled = d.pop("enabled", UNSET)

        update_auto_tag_rule_request = cls(
            name=name,
            tag_id=tag_id,
            conditions=conditions,
            enabled=enabled,
        )


        update_auto_tag_rule_request.additional_properties = d
        return update_auto_tag_rule_request

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
