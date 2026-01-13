from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="DashboardLayout")



@_attrs_define
class DashboardLayout:
    """ 
        Attributes:
            columns (Union[Unset, int]):
            row_height (Union[Unset, int]):
            gap (Union[Unset, int]):
     """

    columns: Union[Unset, int] = UNSET
    row_height: Union[Unset, int] = UNSET
    gap: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        columns = self.columns

        row_height = self.row_height

        gap = self.gap


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if columns is not UNSET:
            field_dict["columns"] = columns
        if row_height is not UNSET:
            field_dict["row_height"] = row_height
        if gap is not UNSET:
            field_dict["gap"] = gap

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        columns = d.pop("columns", UNSET)

        row_height = d.pop("row_height", UNSET)

        gap = d.pop("gap", UNSET)

        dashboard_layout = cls(
            columns=columns,
            row_height=row_height,
            gap=gap,
        )


        dashboard_layout.additional_properties = d
        return dashboard_layout

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
