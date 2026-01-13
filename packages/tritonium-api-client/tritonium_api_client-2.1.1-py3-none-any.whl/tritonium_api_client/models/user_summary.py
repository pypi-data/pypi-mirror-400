from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="UserSummary")



@_attrs_define
class UserSummary:
    """ 
        Attributes:
            user_id (Union[Unset, str]):
            email (Union[Unset, str]):
            name (Union[Unset, str]):
            tenant_id (Union[Unset, str]):
            company_name (Union[Unset, str]):
            role (Union[Unset, str]):
            email_verified (Union[Unset, bool]):
     """

    user_id: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    tenant_id: Union[Unset, str] = UNSET
    company_name: Union[Unset, str] = UNSET
    role: Union[Unset, str] = UNSET
    email_verified: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        email = self.email

        name = self.name

        tenant_id = self.tenant_id

        company_name = self.company_name

        role = self.role

        email_verified = self.email_verified


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if email is not UNSET:
            field_dict["email"] = email
        if name is not UNSET:
            field_dict["name"] = name
        if tenant_id is not UNSET:
            field_dict["tenant_id"] = tenant_id
        if company_name is not UNSET:
            field_dict["company_name"] = company_name
        if role is not UNSET:
            field_dict["role"] = role
        if email_verified is not UNSET:
            field_dict["email_verified"] = email_verified

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id", UNSET)

        email = d.pop("email", UNSET)

        name = d.pop("name", UNSET)

        tenant_id = d.pop("tenant_id", UNSET)

        company_name = d.pop("company_name", UNSET)

        role = d.pop("role", UNSET)

        email_verified = d.pop("email_verified", UNSET)

        user_summary = cls(
            user_id=user_id,
            email=email,
            name=name,
            tenant_id=tenant_id,
            company_name=company_name,
            role=role,
            email_verified=email_verified,
        )


        user_summary.additional_properties = d
        return user_summary

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
