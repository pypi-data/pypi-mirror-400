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





T = TypeVar("T", bound="GetAutoTagRuleResponse200")



@_attrs_define
class GetAutoTagRuleResponse200:
    """ 
        Attributes:
            rule (Union[Unset, AutoTagRule]):
     """

    rule: Union[Unset, 'AutoTagRule'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.auto_tag_rule import AutoTagRule
        rule: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.rule, Unset):
            rule = self.rule.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if rule is not UNSET:
            field_dict["rule"] = rule

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.auto_tag_rule import AutoTagRule
        d = dict(src_dict)
        _rule = d.pop("rule", UNSET)
        rule: Union[Unset, AutoTagRule]
        if isinstance(_rule,  Unset):
            rule = UNSET
        else:
            rule = AutoTagRule.from_dict(_rule)




        get_auto_tag_rule_response_200 = cls(
            rule=rule,
        )


        get_auto_tag_rule_response_200.additional_properties = d
        return get_auto_tag_rule_response_200

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
