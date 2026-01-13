from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.get_bill_forecast_response_200_points_item import GetBillForecastResponse200PointsItem





T = TypeVar("T", bound="GetBillForecastResponse200")



@_attrs_define
class GetBillForecastResponse200:
    """ 
        Attributes:
            points (Union[Unset, list['GetBillForecastResponse200PointsItem']]):
            current_monthly (Union[Unset, float]):
            projected_monthly (Union[Unset, float]):
            change_amount (Union[Unset, float]):
            change_percent (Union[Unset, float]):
     """

    points: Union[Unset, list['GetBillForecastResponse200PointsItem']] = UNSET
    current_monthly: Union[Unset, float] = UNSET
    projected_monthly: Union[Unset, float] = UNSET
    change_amount: Union[Unset, float] = UNSET
    change_percent: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_bill_forecast_response_200_points_item import GetBillForecastResponse200PointsItem
        points: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.points, Unset):
            points = []
            for points_item_data in self.points:
                points_item = points_item_data.to_dict()
                points.append(points_item)



        current_monthly = self.current_monthly

        projected_monthly = self.projected_monthly

        change_amount = self.change_amount

        change_percent = self.change_percent


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if points is not UNSET:
            field_dict["points"] = points
        if current_monthly is not UNSET:
            field_dict["current_monthly"] = current_monthly
        if projected_monthly is not UNSET:
            field_dict["projected_monthly"] = projected_monthly
        if change_amount is not UNSET:
            field_dict["change_amount"] = change_amount
        if change_percent is not UNSET:
            field_dict["change_percent"] = change_percent

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_bill_forecast_response_200_points_item import GetBillForecastResponse200PointsItem
        d = dict(src_dict)
        points = []
        _points = d.pop("points", UNSET)
        for points_item_data in (_points or []):
            points_item = GetBillForecastResponse200PointsItem.from_dict(points_item_data)



            points.append(points_item)


        current_monthly = d.pop("current_monthly", UNSET)

        projected_monthly = d.pop("projected_monthly", UNSET)

        change_amount = d.pop("change_amount", UNSET)

        change_percent = d.pop("change_percent", UNSET)

        get_bill_forecast_response_200 = cls(
            points=points,
            current_monthly=current_monthly,
            projected_monthly=projected_monthly,
            change_amount=change_amount,
            change_percent=change_percent,
        )


        get_bill_forecast_response_200.additional_properties = d
        return get_bill_forecast_response_200

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
