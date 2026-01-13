from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.rating_snapshot import RatingSnapshot





T = TypeVar("T", bound="GetRatingsHistoryResponse200")



@_attrs_define
class GetRatingsHistoryResponse200:
    """ 
        Attributes:
            snapshots (Union[Unset, list['RatingSnapshot']]):
            next_cursor (Union[Unset, str]):
     """

    snapshots: Union[Unset, list['RatingSnapshot']] = UNSET
    next_cursor: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.rating_snapshot import RatingSnapshot
        snapshots: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.snapshots, Unset):
            snapshots = []
            for snapshots_item_data in self.snapshots:
                snapshots_item = snapshots_item_data.to_dict()
                snapshots.append(snapshots_item)



        next_cursor = self.next_cursor


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if snapshots is not UNSET:
            field_dict["snapshots"] = snapshots
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rating_snapshot import RatingSnapshot
        d = dict(src_dict)
        snapshots = []
        _snapshots = d.pop("snapshots", UNSET)
        for snapshots_item_data in (_snapshots or []):
            snapshots_item = RatingSnapshot.from_dict(snapshots_item_data)



            snapshots.append(snapshots_item)


        next_cursor = d.pop("next_cursor", UNSET)

        get_ratings_history_response_200 = cls(
            snapshots=snapshots,
            next_cursor=next_cursor,
        )


        get_ratings_history_response_200.additional_properties = d
        return get_ratings_history_response_200

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
