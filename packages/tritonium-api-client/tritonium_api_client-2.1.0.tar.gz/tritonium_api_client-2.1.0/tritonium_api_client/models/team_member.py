from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="TeamMember")



@_attrs_define
class TeamMember:
    """ 
        Attributes:
            user_id (Union[Unset, str]): Unique identifier for the team member.
            name (Union[Unset, str]): Display name of the team member.
            email (Union[Unset, str]): Email address of the team member.
            avatar_url (Union[Unset, str]): URL to the team member's avatar image.
     """

    user_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    avatar_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        name = self.name

        email = self.email

        avatar_url = self.avatar_url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email
        if avatar_url is not UNSET:
            field_dict["avatar_url"] = avatar_url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id", UNSET)

        name = d.pop("name", UNSET)

        email = d.pop("email", UNSET)

        avatar_url = d.pop("avatar_url", UNSET)

        team_member = cls(
            user_id=user_id,
            name=name,
            email=email,
            avatar_url=avatar_url,
        )


        team_member.additional_properties = d
        return team_member

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
