from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="InsightKeyDriversItem")



@_attrs_define
class InsightKeyDriversItem:
    """ 
        Attributes:
            driver (Union[Unset, str]):
            sentiment (Union[Unset, str]):
            change (Union[Unset, float]):
     """

    driver: Union[Unset, str] = UNSET
    sentiment: Union[Unset, str] = UNSET
    change: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        driver = self.driver

        sentiment = self.sentiment

        change = self.change


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if driver is not UNSET:
            field_dict["driver"] = driver
        if sentiment is not UNSET:
            field_dict["sentiment"] = sentiment
        if change is not UNSET:
            field_dict["change"] = change

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        driver = d.pop("driver", UNSET)

        sentiment = d.pop("sentiment", UNSET)

        change = d.pop("change", UNSET)

        insight_key_drivers_item = cls(
            driver=driver,
            sentiment=sentiment,
            change=change,
        )


        insight_key_drivers_item.additional_properties = d
        return insight_key_drivers_item

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
