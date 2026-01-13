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
  from ..models.create_auto_tag_rule_request_conditions_item import CreateAutoTagRuleRequestConditionsItem





T = TypeVar("T", bound="CreateAutoTagRuleRequest")



@_attrs_define
class CreateAutoTagRuleRequest:
    """ 
        Attributes:
            name (str):
            tag_id (UUID):
            conditions (list['CreateAutoTagRuleRequestConditionsItem']):
            enabled (Union[Unset, bool]):  Default: True.
     """

    name: str
    tag_id: UUID
    conditions: list['CreateAutoTagRuleRequestConditionsItem']
    enabled: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.create_auto_tag_rule_request_conditions_item import CreateAutoTagRuleRequestConditionsItem
        name = self.name

        tag_id = str(self.tag_id)

        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)



        enabled = self.enabled


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "tag_id": tag_id,
            "conditions": conditions,
        })
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_auto_tag_rule_request_conditions_item import CreateAutoTagRuleRequestConditionsItem
        d = dict(src_dict)
        name = d.pop("name")

        tag_id = UUID(d.pop("tag_id"))




        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in (_conditions):
            conditions_item = CreateAutoTagRuleRequestConditionsItem.from_dict(conditions_item_data)



            conditions.append(conditions_item)


        enabled = d.pop("enabled", UNSET)

        create_auto_tag_rule_request = cls(
            name=name,
            tag_id=tag_id,
            conditions=conditions,
            enabled=enabled,
        )


        create_auto_tag_rule_request.additional_properties = d
        return create_auto_tag_rule_request

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
