from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.generate_report_request_output_format import GenerateReportRequestOutputFormat
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.generate_report_request_filters import GenerateReportRequestFilters





T = TypeVar("T", bound="GenerateReportRequest")



@_attrs_define
class GenerateReportRequest:
    """ 
        Attributes:
            template_id (str):
            output_format (GenerateReportRequestOutputFormat):
            filters (Union[Unset, GenerateReportRequestFilters]):
     """

    template_id: str
    output_format: GenerateReportRequestOutputFormat
    filters: Union[Unset, 'GenerateReportRequestFilters'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.generate_report_request_filters import GenerateReportRequestFilters
        template_id = self.template_id

        output_format = self.output_format.value

        filters: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "template_id": template_id,
            "output_format": output_format,
        })
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.generate_report_request_filters import GenerateReportRequestFilters
        d = dict(src_dict)
        template_id = d.pop("template_id")

        output_format = GenerateReportRequestOutputFormat(d.pop("output_format"))




        _filters = d.pop("filters", UNSET)
        filters: Union[Unset, GenerateReportRequestFilters]
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = GenerateReportRequestFilters.from_dict(_filters)




        generate_report_request = cls(
            template_id=template_id,
            output_format=output_format,
            filters=filters,
        )


        generate_report_request.additional_properties = d
        return generate_report_request

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
