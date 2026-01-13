from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.invoice import Invoice





T = TypeVar("T", bound="GetInvoicesResponse200")



@_attrs_define
class GetInvoicesResponse200:
    """ 
        Attributes:
            invoices (Union[Unset, list['Invoice']]):
            next_cursor (Union[Unset, str]):
     """

    invoices: Union[Unset, list['Invoice']] = UNSET
    next_cursor: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.invoice import Invoice
        invoices: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.invoices, Unset):
            invoices = []
            for invoices_item_data in self.invoices:
                invoices_item = invoices_item_data.to_dict()
                invoices.append(invoices_item)



        next_cursor = self.next_cursor


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if invoices is not UNSET:
            field_dict["invoices"] = invoices
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.invoice import Invoice
        d = dict(src_dict)
        invoices = []
        _invoices = d.pop("invoices", UNSET)
        for invoices_item_data in (_invoices or []):
            invoices_item = Invoice.from_dict(invoices_item_data)



            invoices.append(invoices_item)


        next_cursor = d.pop("next_cursor", UNSET)

        get_invoices_response_200 = cls(
            invoices=invoices,
            next_cursor=next_cursor,
        )


        get_invoices_response_200.additional_properties = d
        return get_invoices_response_200

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
