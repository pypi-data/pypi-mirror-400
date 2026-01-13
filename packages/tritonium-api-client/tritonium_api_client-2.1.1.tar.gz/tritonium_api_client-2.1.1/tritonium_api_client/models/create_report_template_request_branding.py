from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="CreateReportTemplateRequestBranding")



@_attrs_define
class CreateReportTemplateRequestBranding:
    """ 
        Attributes:
            logo_url (Union[Unset, str]):
            primary_color (Union[Unset, str]):
            secondary_color (Union[Unset, str]):
            company_name (Union[Unset, str]):
     """

    logo_url: Union[Unset, str] = UNSET
    primary_color: Union[Unset, str] = UNSET
    secondary_color: Union[Unset, str] = UNSET
    company_name: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        logo_url = self.logo_url

        primary_color = self.primary_color

        secondary_color = self.secondary_color

        company_name = self.company_name


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if logo_url is not UNSET:
            field_dict["logo_url"] = logo_url
        if primary_color is not UNSET:
            field_dict["primary_color"] = primary_color
        if secondary_color is not UNSET:
            field_dict["secondary_color"] = secondary_color
        if company_name is not UNSET:
            field_dict["company_name"] = company_name

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        logo_url = d.pop("logo_url", UNSET)

        primary_color = d.pop("primary_color", UNSET)

        secondary_color = d.pop("secondary_color", UNSET)

        company_name = d.pop("company_name", UNSET)

        create_report_template_request_branding = cls(
            logo_url=logo_url,
            primary_color=primary_color,
            secondary_color=secondary_color,
            company_name=company_name,
        )


        create_report_template_request_branding.additional_properties = d
        return create_report_template_request_branding

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
