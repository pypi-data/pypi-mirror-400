from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.alert import Alert





T = TypeVar("T", bound="GetAlertsResponse200")



@_attrs_define
class GetAlertsResponse200:
    """ 
        Attributes:
            alerts (Union[Unset, list['Alert']]):
            next_cursor (Union[Unset, str]):
     """

    alerts: Union[Unset, list['Alert']] = UNSET
    next_cursor: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.alert import Alert
        alerts: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.alerts, Unset):
            alerts = []
            for alerts_item_data in self.alerts:
                alerts_item = alerts_item_data.to_dict()
                alerts.append(alerts_item)



        next_cursor = self.next_cursor


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if alerts is not UNSET:
            field_dict["alerts"] = alerts
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.alert import Alert
        d = dict(src_dict)
        alerts = []
        _alerts = d.pop("alerts", UNSET)
        for alerts_item_data in (_alerts or []):
            alerts_item = Alert.from_dict(alerts_item_data)



            alerts.append(alerts_item)


        next_cursor = d.pop("next_cursor", UNSET)

        get_alerts_response_200 = cls(
            alerts=alerts,
            next_cursor=next_cursor,
        )


        get_alerts_response_200.additional_properties = d
        return get_alerts_response_200

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
