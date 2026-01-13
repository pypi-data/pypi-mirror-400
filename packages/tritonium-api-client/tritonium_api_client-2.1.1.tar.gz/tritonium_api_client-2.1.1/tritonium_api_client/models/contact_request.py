from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="ContactRequest")



@_attrs_define
class ContactRequest:
    """ 
        Attributes:
            name (str): Contact's full name. Example: Jane Doe.
            email (str): Contact's email address. Example: jane@company.com.
            company (str): Company or organization name. Example: Acme Inc.
            message (str): The contact message or inquiry.
            title (Union[Unset, str]): Contact's job title.
            role (Union[Unset, str]): Contact's role in the organization.
            company_size (Union[Unset, str]): Size of the company.
            utm_source (Union[Unset, str]): UTM source tracking parameter.
            utm_medium (Union[Unset, str]): UTM medium tracking parameter.
            utm_campaign (Union[Unset, str]): UTM campaign tracking parameter.
     """

    name: str
    email: str
    company: str
    message: str
    title: Union[Unset, str] = UNSET
    role: Union[Unset, str] = UNSET
    company_size: Union[Unset, str] = UNSET
    utm_source: Union[Unset, str] = UNSET
    utm_medium: Union[Unset, str] = UNSET
    utm_campaign: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        email = self.email

        company = self.company

        message = self.message

        title = self.title

        role = self.role

        company_size = self.company_size

        utm_source = self.utm_source

        utm_medium = self.utm_medium

        utm_campaign = self.utm_campaign


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "email": email,
            "company": company,
            "message": message,
        })
        if title is not UNSET:
            field_dict["title"] = title
        if role is not UNSET:
            field_dict["role"] = role
        if company_size is not UNSET:
            field_dict["company_size"] = company_size
        if utm_source is not UNSET:
            field_dict["utm_source"] = utm_source
        if utm_medium is not UNSET:
            field_dict["utm_medium"] = utm_medium
        if utm_campaign is not UNSET:
            field_dict["utm_campaign"] = utm_campaign

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        email = d.pop("email")

        company = d.pop("company")

        message = d.pop("message")

        title = d.pop("title", UNSET)

        role = d.pop("role", UNSET)

        company_size = d.pop("company_size", UNSET)

        utm_source = d.pop("utm_source", UNSET)

        utm_medium = d.pop("utm_medium", UNSET)

        utm_campaign = d.pop("utm_campaign", UNSET)

        contact_request = cls(
            name=name,
            email=email,
            company=company,
            message=message,
            title=title,
            role=role,
            company_size=company_size,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
        )


        contact_request.additional_properties = d
        return contact_request

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
