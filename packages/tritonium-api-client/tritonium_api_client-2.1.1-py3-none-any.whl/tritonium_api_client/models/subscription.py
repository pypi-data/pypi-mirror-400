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






T = TypeVar("T", bound="Subscription")



@_attrs_define
class Subscription:
    """ 
        Attributes:
            subscription_id (Union[Unset, str]):
            plan (Union[Unset, str]):
            status (Union[Unset, str]):
            seats (Union[Unset, int]):
            renews_at (Union[Unset, datetime.datetime]):
            cancel_at_period_end (Union[Unset, bool]):
     """

    subscription_id: Union[Unset, str] = UNSET
    plan: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    seats: Union[Unset, int] = UNSET
    renews_at: Union[Unset, datetime.datetime] = UNSET
    cancel_at_period_end: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        subscription_id = self.subscription_id

        plan = self.plan

        status = self.status

        seats = self.seats

        renews_at: Union[Unset, str] = UNSET
        if not isinstance(self.renews_at, Unset):
            renews_at = self.renews_at.isoformat()

        cancel_at_period_end = self.cancel_at_period_end


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if subscription_id is not UNSET:
            field_dict["subscription_id"] = subscription_id
        if plan is not UNSET:
            field_dict["plan"] = plan
        if status is not UNSET:
            field_dict["status"] = status
        if seats is not UNSET:
            field_dict["seats"] = seats
        if renews_at is not UNSET:
            field_dict["renews_at"] = renews_at
        if cancel_at_period_end is not UNSET:
            field_dict["cancel_at_period_end"] = cancel_at_period_end

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        subscription_id = d.pop("subscription_id", UNSET)

        plan = d.pop("plan", UNSET)

        status = d.pop("status", UNSET)

        seats = d.pop("seats", UNSET)

        _renews_at = d.pop("renews_at", UNSET)
        renews_at: Union[Unset, datetime.datetime]
        if isinstance(_renews_at,  Unset):
            renews_at = UNSET
        else:
            renews_at = isoparse(_renews_at)




        cancel_at_period_end = d.pop("cancel_at_period_end", UNSET)

        subscription = cls(
            subscription_id=subscription_id,
            plan=plan,
            status=status,
            seats=seats,
            renews_at=renews_at,
            cancel_at_period_end=cancel_at_period_end,
        )


        subscription.additional_properties = d
        return subscription

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
