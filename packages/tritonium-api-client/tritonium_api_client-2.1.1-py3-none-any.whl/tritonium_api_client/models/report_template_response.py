from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.report_template import ReportTemplate





T = TypeVar("T", bound="ReportTemplateResponse")



@_attrs_define
class ReportTemplateResponse:
    """ 
        Attributes:
            template (Union[Unset, ReportTemplate]):
     """

    template: Union[Unset, 'ReportTemplate'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.report_template import ReportTemplate
        template: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.template, Unset):
            template = self.template.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if template is not UNSET:
            field_dict["template"] = template

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report_template import ReportTemplate
        d = dict(src_dict)
        _template = d.pop("template", UNSET)
        template: Union[Unset, ReportTemplate]
        if isinstance(_template,  Unset):
            template = UNSET
        else:
            template = ReportTemplate.from_dict(_template)




        report_template_response = cls(
            template=template,
        )


        report_template_response.additional_properties = d
        return report_template_response

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
