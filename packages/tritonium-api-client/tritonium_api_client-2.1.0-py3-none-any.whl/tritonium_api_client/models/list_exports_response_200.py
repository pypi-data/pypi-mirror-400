from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.export_job import ExportJob





T = TypeVar("T", bound="ListExportsResponse200")



@_attrs_define
class ListExportsResponse200:
    """ 
        Attributes:
            exports (Union[Unset, list['ExportJob']]):
     """

    exports: Union[Unset, list['ExportJob']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.export_job import ExportJob
        exports: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.exports, Unset):
            exports = []
            for exports_item_data in self.exports:
                exports_item = exports_item_data.to_dict()
                exports.append(exports_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if exports is not UNSET:
            field_dict["exports"] = exports

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.export_job import ExportJob
        d = dict(src_dict)
        exports = []
        _exports = d.pop("exports", UNSET)
        for exports_item_data in (_exports or []):
            exports_item = ExportJob.from_dict(exports_item_data)



            exports.append(exports_item)


        list_exports_response_200 = cls(
            exports=exports,
        )


        list_exports_response_200.additional_properties = d
        return list_exports_response_200

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
