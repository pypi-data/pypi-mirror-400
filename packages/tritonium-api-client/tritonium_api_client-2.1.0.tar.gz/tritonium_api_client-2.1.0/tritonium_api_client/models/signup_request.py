from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="SignupRequest")



@_attrs_define
class SignupRequest:
    """ 
        Attributes:
            email (str): Email address for waitlist signup. Example: user@company.com.
            company (str): Company or organization name. Example: Acme Inc.
            app (Union[Unset, str]): Name of the app they want to track.
            app_name (Union[Unset, str]): Alias for app field.
            name (Union[Unset, str]): Contact person's name.
     """

    email: str
    company: str
    app: Union[Unset, str] = UNSET
    app_name: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        email = self.email

        company = self.company

        app = self.app

        app_name = self.app_name

        name = self.name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "email": email,
            "company": company,
        })
        if app is not UNSET:
            field_dict["app"] = app
        if app_name is not UNSET:
            field_dict["app_name"] = app_name
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        company = d.pop("company")

        app = d.pop("app", UNSET)

        app_name = d.pop("app_name", UNSET)

        name = d.pop("name", UNSET)

        signup_request = cls(
            email=email,
            company=company,
            app=app,
            app_name=app_name,
            name=name,
        )


        signup_request.additional_properties = d
        return signup_request

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
