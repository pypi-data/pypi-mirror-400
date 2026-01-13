from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime

if TYPE_CHECKING:
  from ..models.report_template_branding import ReportTemplateBranding





T = TypeVar("T", bound="ReportTemplate")



@_attrs_define
class ReportTemplate:
    """ 
        Attributes:
            template_id (Union[Unset, str]):
            name (Union[Unset, str]):
            template_type (Union[Unset, str]):
            sections (Union[Unset, list[str]]):
            branding (Union[Unset, ReportTemplateBranding]):
            output_formats (Union[Unset, list[str]]):
            created_at (Union[Unset, datetime.datetime]):
            updated_at (Union[Unset, datetime.datetime]):
     """

    template_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    template_type: Union[Unset, str] = UNSET
    sections: Union[Unset, list[str]] = UNSET
    branding: Union[Unset, 'ReportTemplateBranding'] = UNSET
    output_formats: Union[Unset, list[str]] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.report_template_branding import ReportTemplateBranding
        template_id = self.template_id

        name = self.name

        template_type = self.template_type

        sections: Union[Unset, list[str]] = UNSET
        if not isinstance(self.sections, Unset):
            sections = self.sections



        branding: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.branding, Unset):
            branding = self.branding.to_dict()

        output_formats: Union[Unset, list[str]] = UNSET
        if not isinstance(self.output_formats, Unset):
            output_formats = self.output_formats



        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if template_id is not UNSET:
            field_dict["template_id"] = template_id
        if name is not UNSET:
            field_dict["name"] = name
        if template_type is not UNSET:
            field_dict["template_type"] = template_type
        if sections is not UNSET:
            field_dict["sections"] = sections
        if branding is not UNSET:
            field_dict["branding"] = branding
        if output_formats is not UNSET:
            field_dict["output_formats"] = output_formats
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report_template_branding import ReportTemplateBranding
        d = dict(src_dict)
        template_id = d.pop("template_id", UNSET)

        name = d.pop("name", UNSET)

        template_type = d.pop("template_type", UNSET)

        sections = cast(list[str], d.pop("sections", UNSET))


        _branding = d.pop("branding", UNSET)
        branding: Union[Unset, ReportTemplateBranding]
        if isinstance(_branding,  Unset):
            branding = UNSET
        else:
            branding = ReportTemplateBranding.from_dict(_branding)




        output_formats = cast(list[str], d.pop("output_formats", UNSET))


        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at,  Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)




        report_template = cls(
            template_id=template_id,
            name=name,
            template_type=template_type,
            sections=sections,
            branding=branding,
            output_formats=output_formats,
            created_at=created_at,
            updated_at=updated_at,
        )


        report_template.additional_properties = d
        return report_template

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
