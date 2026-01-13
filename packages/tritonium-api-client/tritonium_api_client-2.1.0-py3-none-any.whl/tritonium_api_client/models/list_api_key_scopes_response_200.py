from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.list_api_key_scopes_response_200_scope_groups import ListApiKeyScopesResponse200ScopeGroups





T = TypeVar("T", bound="ListApiKeyScopesResponse200")



@_attrs_define
class ListApiKeyScopesResponse200:
    """ 
        Attributes:
            scopes (Union[Unset, list[str]]):  Example: ['apps:read', 'apps:write', 'reviews:read', 'reviews:write'].
            scope_groups (Union[Unset, ListApiKeyScopesResponse200ScopeGroups]):
     """

    scopes: Union[Unset, list[str]] = UNSET
    scope_groups: Union[Unset, 'ListApiKeyScopesResponse200ScopeGroups'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.list_api_key_scopes_response_200_scope_groups import ListApiKeyScopesResponse200ScopeGroups
        scopes: Union[Unset, list[str]] = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes



        scope_groups: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.scope_groups, Unset):
            scope_groups = self.scope_groups.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if scope_groups is not UNSET:
            field_dict["scope_groups"] = scope_groups

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_api_key_scopes_response_200_scope_groups import ListApiKeyScopesResponse200ScopeGroups
        d = dict(src_dict)
        scopes = cast(list[str], d.pop("scopes", UNSET))


        _scope_groups = d.pop("scope_groups", UNSET)
        scope_groups: Union[Unset, ListApiKeyScopesResponse200ScopeGroups]
        if isinstance(_scope_groups,  Unset):
            scope_groups = UNSET
        else:
            scope_groups = ListApiKeyScopesResponse200ScopeGroups.from_dict(_scope_groups)




        list_api_key_scopes_response_200 = cls(
            scopes=scopes,
            scope_groups=scope_groups,
        )


        list_api_key_scopes_response_200.additional_properties = d
        return list_api_key_scopes_response_200

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
