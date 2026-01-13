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
  from ..models.auto_tag_rule_conditions_item import AutoTagRuleConditionsItem





T = TypeVar("T", bound="AutoTagRule")



@_attrs_define
class AutoTagRule:
    """ 
        Attributes:
            rule_id (Union[Unset, UUID]):
            name (Union[Unset, str]):
            tag_id (Union[Unset, UUID]):
            tag_name (Union[Unset, str]):
            tag_color (Union[Unset, str]):
            conditions (Union[Unset, list['AutoTagRuleConditionsItem']]):
            enabled (Union[Unset, bool]):
            matches_count (Union[Unset, int]):
            created_at (Union[Unset, datetime.datetime]):
            updated_at (Union[Unset, datetime.datetime]):
     """

    rule_id: Union[Unset, UUID] = UNSET
    name: Union[Unset, str] = UNSET
    tag_id: Union[Unset, UUID] = UNSET
    tag_name: Union[Unset, str] = UNSET
    tag_color: Union[Unset, str] = UNSET
    conditions: Union[Unset, list['AutoTagRuleConditionsItem']] = UNSET
    enabled: Union[Unset, bool] = UNSET
    matches_count: Union[Unset, int] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.auto_tag_rule_conditions_item import AutoTagRuleConditionsItem
        rule_id: Union[Unset, str] = UNSET
        if not isinstance(self.rule_id, Unset):
            rule_id = str(self.rule_id)

        name = self.name

        tag_id: Union[Unset, str] = UNSET
        if not isinstance(self.tag_id, Unset):
            tag_id = str(self.tag_id)

        tag_name = self.tag_name

        tag_color = self.tag_color

        conditions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.conditions, Unset):
            conditions = []
            for conditions_item_data in self.conditions:
                conditions_item = conditions_item_data.to_dict()
                conditions.append(conditions_item)



        enabled = self.enabled

        matches_count = self.matches_count

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
        if rule_id is not UNSET:
            field_dict["rule_id"] = rule_id
        if name is not UNSET:
            field_dict["name"] = name
        if tag_id is not UNSET:
            field_dict["tag_id"] = tag_id
        if tag_name is not UNSET:
            field_dict["tag_name"] = tag_name
        if tag_color is not UNSET:
            field_dict["tag_color"] = tag_color
        if conditions is not UNSET:
            field_dict["conditions"] = conditions
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if matches_count is not UNSET:
            field_dict["matches_count"] = matches_count
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.auto_tag_rule_conditions_item import AutoTagRuleConditionsItem
        d = dict(src_dict)
        _rule_id = d.pop("rule_id", UNSET)
        rule_id: Union[Unset, UUID]
        if isinstance(_rule_id,  Unset):
            rule_id = UNSET
        else:
            rule_id = UUID(_rule_id)




        name = d.pop("name", UNSET)

        _tag_id = d.pop("tag_id", UNSET)
        tag_id: Union[Unset, UUID]
        if isinstance(_tag_id,  Unset):
            tag_id = UNSET
        else:
            tag_id = UUID(_tag_id)




        tag_name = d.pop("tag_name", UNSET)

        tag_color = d.pop("tag_color", UNSET)

        conditions = []
        _conditions = d.pop("conditions", UNSET)
        for conditions_item_data in (_conditions or []):
            conditions_item = AutoTagRuleConditionsItem.from_dict(conditions_item_data)



            conditions.append(conditions_item)


        enabled = d.pop("enabled", UNSET)

        matches_count = d.pop("matches_count", UNSET)

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




        auto_tag_rule = cls(
            rule_id=rule_id,
            name=name,
            tag_id=tag_id,
            tag_name=tag_name,
            tag_color=tag_color,
            conditions=conditions,
            enabled=enabled,
            matches_count=matches_count,
            created_at=created_at,
            updated_at=updated_at,
        )


        auto_tag_rule.additional_properties = d
        return auto_tag_rule

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
