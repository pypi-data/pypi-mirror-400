from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.team_member import TeamMember





T = TypeVar("T", bound="GetTeamMembersResponse200")



@_attrs_define
class GetTeamMembersResponse200:
    """ 
        Attributes:
            members (Union[Unset, list['TeamMember']]):
     """

    members: Union[Unset, list['TeamMember']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.team_member import TeamMember
        members: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.members, Unset):
            members = []
            for members_item_data in self.members:
                members_item = members_item_data.to_dict()
                members.append(members_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if members is not UNSET:
            field_dict["members"] = members

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.team_member import TeamMember
        d = dict(src_dict)
        members = []
        _members = d.pop("members", UNSET)
        for members_item_data in (_members or []):
            members_item = TeamMember.from_dict(members_item_data)



            members.append(members_item)


        get_team_members_response_200 = cls(
            members=members,
        )


        get_team_members_response_200.additional_properties = d
        return get_team_members_response_200

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
