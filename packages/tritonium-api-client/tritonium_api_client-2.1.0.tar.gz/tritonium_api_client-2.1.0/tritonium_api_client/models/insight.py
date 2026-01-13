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

if TYPE_CHECKING:
  from ..models.insight_key_drivers_item import InsightKeyDriversItem





T = TypeVar("T", bound="Insight")



@_attrs_define
class Insight:
    """ 
        Attributes:
            insight_id (Union[Unset, str]):
            app_uuid (Union[Unset, str]):
            generated_at (Union[Unset, datetime.datetime]):
            summary (Union[Unset, str]):
            key_drivers (Union[Unset, list['InsightKeyDriversItem']]):
            opportunities (Union[Unset, list[str]]):
     """

    insight_id: Union[Unset, str] = UNSET
    app_uuid: Union[Unset, str] = UNSET
    generated_at: Union[Unset, datetime.datetime] = UNSET
    summary: Union[Unset, str] = UNSET
    key_drivers: Union[Unset, list['InsightKeyDriversItem']] = UNSET
    opportunities: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.insight_key_drivers_item import InsightKeyDriversItem
        insight_id = self.insight_id

        app_uuid = self.app_uuid

        generated_at: Union[Unset, str] = UNSET
        if not isinstance(self.generated_at, Unset):
            generated_at = self.generated_at.isoformat()

        summary = self.summary

        key_drivers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.key_drivers, Unset):
            key_drivers = []
            for key_drivers_item_data in self.key_drivers:
                key_drivers_item = key_drivers_item_data.to_dict()
                key_drivers.append(key_drivers_item)



        opportunities: Union[Unset, list[str]] = UNSET
        if not isinstance(self.opportunities, Unset):
            opportunities = self.opportunities




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if insight_id is not UNSET:
            field_dict["insight_id"] = insight_id
        if app_uuid is not UNSET:
            field_dict["app_uuid"] = app_uuid
        if generated_at is not UNSET:
            field_dict["generated_at"] = generated_at
        if summary is not UNSET:
            field_dict["summary"] = summary
        if key_drivers is not UNSET:
            field_dict["key_drivers"] = key_drivers
        if opportunities is not UNSET:
            field_dict["opportunities"] = opportunities

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.insight_key_drivers_item import InsightKeyDriversItem
        d = dict(src_dict)
        insight_id = d.pop("insight_id", UNSET)

        app_uuid = d.pop("app_uuid", UNSET)

        _generated_at = d.pop("generated_at", UNSET)
        generated_at: Union[Unset, datetime.datetime]
        if isinstance(_generated_at,  Unset):
            generated_at = UNSET
        else:
            generated_at = isoparse(_generated_at)




        summary = d.pop("summary", UNSET)

        key_drivers = []
        _key_drivers = d.pop("key_drivers", UNSET)
        for key_drivers_item_data in (_key_drivers or []):
            key_drivers_item = InsightKeyDriversItem.from_dict(key_drivers_item_data)



            key_drivers.append(key_drivers_item)


        opportunities = cast(list[str], d.pop("opportunities", UNSET))


        insight = cls(
            insight_id=insight_id,
            app_uuid=app_uuid,
            generated_at=generated_at,
            summary=summary,
            key_drivers=key_drivers,
            opportunities=opportunities,
        )


        insight.additional_properties = d
        return insight

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
