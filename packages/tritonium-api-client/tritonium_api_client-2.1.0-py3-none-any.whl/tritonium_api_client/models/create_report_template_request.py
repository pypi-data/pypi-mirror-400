from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.create_report_template_request_output_formats_item import CreateReportTemplateRequestOutputFormatsItem
from ..models.create_report_template_request_sections_item import CreateReportTemplateRequestSectionsItem
from ..models.create_report_template_request_template_type import CreateReportTemplateRequestTemplateType
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.create_report_template_request_branding import CreateReportTemplateRequestBranding





T = TypeVar("T", bound="CreateReportTemplateRequest")



@_attrs_define
class CreateReportTemplateRequest:
    """ 
        Attributes:
            name (str):
            template_type (CreateReportTemplateRequestTemplateType):
            sections (list[CreateReportTemplateRequestSectionsItem]):
            output_formats (list[CreateReportTemplateRequestOutputFormatsItem]):
            branding (Union[Unset, CreateReportTemplateRequestBranding]):
     """

    name: str
    template_type: CreateReportTemplateRequestTemplateType
    sections: list[CreateReportTemplateRequestSectionsItem]
    output_formats: list[CreateReportTemplateRequestOutputFormatsItem]
    branding: Union[Unset, 'CreateReportTemplateRequestBranding'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.create_report_template_request_branding import CreateReportTemplateRequestBranding
        name = self.name

        template_type = self.template_type.value

        sections = []
        for sections_item_data in self.sections:
            sections_item = sections_item_data.value
            sections.append(sections_item)



        output_formats = []
        for output_formats_item_data in self.output_formats:
            output_formats_item = output_formats_item_data.value
            output_formats.append(output_formats_item)



        branding: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.branding, Unset):
            branding = self.branding.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "name": name,
            "template_type": template_type,
            "sections": sections,
            "output_formats": output_formats,
        })
        if branding is not UNSET:
            field_dict["branding"] = branding

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_report_template_request_branding import CreateReportTemplateRequestBranding
        d = dict(src_dict)
        name = d.pop("name")

        template_type = CreateReportTemplateRequestTemplateType(d.pop("template_type"))




        sections = []
        _sections = d.pop("sections")
        for sections_item_data in (_sections):
            sections_item = CreateReportTemplateRequestSectionsItem(sections_item_data)



            sections.append(sections_item)


        output_formats = []
        _output_formats = d.pop("output_formats")
        for output_formats_item_data in (_output_formats):
            output_formats_item = CreateReportTemplateRequestOutputFormatsItem(output_formats_item_data)



            output_formats.append(output_formats_item)


        _branding = d.pop("branding", UNSET)
        branding: Union[Unset, CreateReportTemplateRequestBranding]
        if isinstance(_branding,  Unset):
            branding = UNSET
        else:
            branding = CreateReportTemplateRequestBranding.from_dict(_branding)




        create_report_template_request = cls(
            name=name,
            template_type=template_type,
            sections=sections,
            output_formats=output_formats,
            branding=branding,
        )


        create_report_template_request.additional_properties = d
        return create_report_template_request

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
