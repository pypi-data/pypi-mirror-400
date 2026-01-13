from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.list_report_sections_response_200_sections_item import ListReportSectionsResponse200SectionsItem





T = TypeVar("T", bound="ListReportSectionsResponse200")



@_attrs_define
class ListReportSectionsResponse200:
    """ 
        Attributes:
            sections (Union[Unset, list['ListReportSectionsResponse200SectionsItem']]):
     """

    sections: Union[Unset, list['ListReportSectionsResponse200SectionsItem']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.list_report_sections_response_200_sections_item import ListReportSectionsResponse200SectionsItem
        sections: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.sections, Unset):
            sections = []
            for sections_item_data in self.sections:
                sections_item = sections_item_data.to_dict()
                sections.append(sections_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if sections is not UNSET:
            field_dict["sections"] = sections

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_report_sections_response_200_sections_item import ListReportSectionsResponse200SectionsItem
        d = dict(src_dict)
        sections = []
        _sections = d.pop("sections", UNSET)
        for sections_item_data in (_sections or []):
            sections_item = ListReportSectionsResponse200SectionsItem.from_dict(sections_item_data)



            sections.append(sections_item)


        list_report_sections_response_200 = cls(
            sections=sections,
        )


        list_report_sections_response_200.additional_properties = d
        return list_report_sections_response_200

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
