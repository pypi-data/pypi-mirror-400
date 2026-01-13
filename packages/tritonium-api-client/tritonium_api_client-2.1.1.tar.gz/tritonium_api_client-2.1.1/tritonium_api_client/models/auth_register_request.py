from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="AuthRegisterRequest")



@_attrs_define
class AuthRegisterRequest:
    """ 
        Attributes:
            email (str):
            password (str):
            company_name (str):
            name (Union[Unset, str]):
            marketing_opt_in (Union[Unset, bool]):
     """

    email: str
    password: str
    company_name: str
    name: Union[Unset, str] = UNSET
    marketing_opt_in: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        email = self.email

        password = self.password

        company_name = self.company_name

        name = self.name

        marketing_opt_in = self.marketing_opt_in


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "email": email,
            "password": password,
            "company_name": company_name,
        })
        if name is not UNSET:
            field_dict["name"] = name
        if marketing_opt_in is not UNSET:
            field_dict["marketing_opt_in"] = marketing_opt_in

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        password = d.pop("password")

        company_name = d.pop("company_name")

        name = d.pop("name", UNSET)

        marketing_opt_in = d.pop("marketing_opt_in", UNSET)

        auth_register_request = cls(
            email=email,
            password=password,
            company_name=company_name,
            name=name,
            marketing_opt_in=marketing_opt_in,
        )


        auth_register_request.additional_properties = d
        return auth_register_request

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
