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






T = TypeVar("T", bound="Invoice")



@_attrs_define
class Invoice:
    """ 
        Attributes:
            invoice_id (Union[Unset, str]):
            number (Union[Unset, str]):
            amount_due (Union[Unset, int]):
            currency (Union[Unset, str]):
            status (Union[Unset, str]):
            hosted_invoice_url (Union[Unset, str]):
            created (Union[Unset, datetime.datetime]):
     """

    invoice_id: Union[Unset, str] = UNSET
    number: Union[Unset, str] = UNSET
    amount_due: Union[Unset, int] = UNSET
    currency: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    hosted_invoice_url: Union[Unset, str] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        invoice_id = self.invoice_id

        number = self.number

        amount_due = self.amount_due

        currency = self.currency

        status = self.status

        hosted_invoice_url = self.hosted_invoice_url

        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if invoice_id is not UNSET:
            field_dict["invoice_id"] = invoice_id
        if number is not UNSET:
            field_dict["number"] = number
        if amount_due is not UNSET:
            field_dict["amount_due"] = amount_due
        if currency is not UNSET:
            field_dict["currency"] = currency
        if status is not UNSET:
            field_dict["status"] = status
        if hosted_invoice_url is not UNSET:
            field_dict["hosted_invoice_url"] = hosted_invoice_url
        if created is not UNSET:
            field_dict["created"] = created

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        invoice_id = d.pop("invoice_id", UNSET)

        number = d.pop("number", UNSET)

        amount_due = d.pop("amount_due", UNSET)

        currency = d.pop("currency", UNSET)

        status = d.pop("status", UNSET)

        hosted_invoice_url = d.pop("hosted_invoice_url", UNSET)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created,  Unset):
            created = UNSET
        else:
            created = isoparse(_created)




        invoice = cls(
            invoice_id=invoice_id,
            number=number,
            amount_due=amount_due,
            currency=currency,
            status=status,
            hosted_invoice_url=hosted_invoice_url,
            created=created,
        )


        invoice.additional_properties = d
        return invoice

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
