from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.auto_tag_rule import AutoTagRule





T = TypeVar("T", bound="GetAutoTagRulesResponse200")



@_attrs_define
class GetAutoTagRulesResponse200:
    """ 
        Attributes:
            rules (Union[Unset, list['AutoTagRule']]):
     """

    rules: Union[Unset, list['AutoTagRule']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.auto_tag_rule import AutoTagRule
        rules: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.rules, Unset):
            rules = []
            for rules_item_data in self.rules:
                rules_item = rules_item_data.to_dict()
                rules.append(rules_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if rules is not UNSET:
            field_dict["rules"] = rules

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.auto_tag_rule import AutoTagRule
        d = dict(src_dict)
        rules = []
        _rules = d.pop("rules", UNSET)
        for rules_item_data in (_rules or []):
            rules_item = AutoTagRule.from_dict(rules_item_data)



            rules.append(rules_item)


        get_auto_tag_rules_response_200 = cls(
            rules=rules,
        )


        get_auto_tag_rules_response_200.additional_properties = d
        return get_auto_tag_rules_response_200

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
