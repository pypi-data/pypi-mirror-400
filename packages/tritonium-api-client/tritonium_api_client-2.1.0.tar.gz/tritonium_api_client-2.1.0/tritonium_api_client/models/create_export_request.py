from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.create_export_request_export_type import CreateExportRequestExportType
from ..models.create_export_request_format import CreateExportRequestFormat
from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.create_export_request_filters import CreateExportRequestFilters





T = TypeVar("T", bound="CreateExportRequest")



@_attrs_define
class CreateExportRequest:
    """ 
        Attributes:
            export_type (CreateExportRequestExportType):
            format_ (CreateExportRequestFormat):
            filters (Union[Unset, CreateExportRequestFilters]):
     """

    export_type: CreateExportRequestExportType
    format_: CreateExportRequestFormat
    filters: Union[Unset, 'CreateExportRequestFilters'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.create_export_request_filters import CreateExportRequestFilters
        export_type = self.export_type.value

        format_ = self.format_.value

        filters: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "export_type": export_type,
            "format": format_,
        })
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.create_export_request_filters import CreateExportRequestFilters
        d = dict(src_dict)
        export_type = CreateExportRequestExportType(d.pop("export_type"))




        format_ = CreateExportRequestFormat(d.pop("format"))




        _filters = d.pop("filters", UNSET)
        filters: Union[Unset, CreateExportRequestFilters]
        if isinstance(_filters,  Unset):
            filters = UNSET
        else:
            filters = CreateExportRequestFilters.from_dict(_filters)




        create_export_request = cls(
            export_type=export_type,
            format_=format_,
            filters=filters,
        )


        create_export_request.additional_properties = d
        return create_export_request

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
