from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="BillingCheckoutRequest")



@_attrs_define
class BillingCheckoutRequest:
    """ 
        Attributes:
            plan (str): Stripe price identifier.
            seats (Union[Unset, int]):
            success_url (Union[Unset, str]):
            cancel_url (Union[Unset, str]):
     """

    plan: str
    seats: Union[Unset, int] = UNSET
    success_url: Union[Unset, str] = UNSET
    cancel_url: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        plan = self.plan

        seats = self.seats

        success_url = self.success_url

        cancel_url = self.cancel_url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "plan": plan,
        })
        if seats is not UNSET:
            field_dict["seats"] = seats
        if success_url is not UNSET:
            field_dict["success_url"] = success_url
        if cancel_url is not UNSET:
            field_dict["cancel_url"] = cancel_url

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        plan = d.pop("plan")

        seats = d.pop("seats", UNSET)

        success_url = d.pop("success_url", UNSET)

        cancel_url = d.pop("cancel_url", UNSET)

        billing_checkout_request = cls(
            plan=plan,
            seats=seats,
            success_url=success_url,
            cancel_url=cancel_url,
        )


        billing_checkout_request.additional_properties = d
        return billing_checkout_request

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
