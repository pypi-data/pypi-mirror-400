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






T = TypeVar("T", bound="GetBillForecastResponse200PointsItem")



@_attrs_define
class GetBillForecastResponse200PointsItem:
    """ 
        Attributes:
            date (Union[Unset, datetime.date]):
            amount (Union[Unset, float]):
            confidence_lower (Union[Unset, float]):
            confidence_upper (Union[Unset, float]):
     """

    date: Union[Unset, datetime.date] = UNSET
    amount: Union[Unset, float] = UNSET
    confidence_lower: Union[Unset, float] = UNSET
    confidence_upper: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        date: Union[Unset, str] = UNSET
        if not isinstance(self.date, Unset):
            date = self.date.isoformat()

        amount = self.amount

        confidence_lower = self.confidence_lower

        confidence_upper = self.confidence_upper


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if date is not UNSET:
            field_dict["date"] = date
        if amount is not UNSET:
            field_dict["amount"] = amount
        if confidence_lower is not UNSET:
            field_dict["confidence_lower"] = confidence_lower
        if confidence_upper is not UNSET:
            field_dict["confidence_upper"] = confidence_upper

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _date = d.pop("date", UNSET)
        date: Union[Unset, datetime.date]
        if isinstance(_date,  Unset):
            date = UNSET
        else:
            date = isoparse(_date).date()




        amount = d.pop("amount", UNSET)

        confidence_lower = d.pop("confidence_lower", UNSET)

        confidence_upper = d.pop("confidence_upper", UNSET)

        get_bill_forecast_response_200_points_item = cls(
            date=date,
            amount=amount,
            confidence_lower=confidence_lower,
            confidence_upper=confidence_upper,
        )


        get_bill_forecast_response_200_points_item.additional_properties = d
        return get_bill_forecast_response_200_points_item

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
