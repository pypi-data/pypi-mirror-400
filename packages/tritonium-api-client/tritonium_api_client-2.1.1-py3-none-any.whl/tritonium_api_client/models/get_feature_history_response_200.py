from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.feature_impact_entry import FeatureImpactEntry





T = TypeVar("T", bound="GetFeatureHistoryResponse200")



@_attrs_define
class GetFeatureHistoryResponse200:
    """ 
        Attributes:
            entries (Union[Unset, list['FeatureImpactEntry']]):
            next_cursor (Union[Unset, str]):
     """

    entries: Union[Unset, list['FeatureImpactEntry']] = UNSET
    next_cursor: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.feature_impact_entry import FeatureImpactEntry
        entries: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.entries, Unset):
            entries = []
            for entries_item_data in self.entries:
                entries_item = entries_item_data.to_dict()
                entries.append(entries_item)



        next_cursor = self.next_cursor


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if entries is not UNSET:
            field_dict["entries"] = entries
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.feature_impact_entry import FeatureImpactEntry
        d = dict(src_dict)
        entries = []
        _entries = d.pop("entries", UNSET)
        for entries_item_data in (_entries or []):
            entries_item = FeatureImpactEntry.from_dict(entries_item_data)



            entries.append(entries_item)


        next_cursor = d.pop("next_cursor", UNSET)

        get_feature_history_response_200 = cls(
            entries=entries,
            next_cursor=next_cursor,
        )


        get_feature_history_response_200.additional_properties = d
        return get_feature_history_response_200

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
