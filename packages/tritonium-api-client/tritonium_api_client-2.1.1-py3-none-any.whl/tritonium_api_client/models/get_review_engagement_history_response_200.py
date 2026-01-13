from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.get_review_engagement_history_response_200_metadata import GetReviewEngagementHistoryResponse200Metadata
  from ..models.get_review_engagement_history_response_200_history_item import GetReviewEngagementHistoryResponse200HistoryItem





T = TypeVar("T", bound="GetReviewEngagementHistoryResponse200")



@_attrs_define
class GetReviewEngagementHistoryResponse200:
    """ 
        Attributes:
            history (Union[Unset, list['GetReviewEngagementHistoryResponse200HistoryItem']]):
            metadata (Union[Unset, GetReviewEngagementHistoryResponse200Metadata]):
     """

    history: Union[Unset, list['GetReviewEngagementHistoryResponse200HistoryItem']] = UNSET
    metadata: Union[Unset, 'GetReviewEngagementHistoryResponse200Metadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_review_engagement_history_response_200_metadata import GetReviewEngagementHistoryResponse200Metadata
        from ..models.get_review_engagement_history_response_200_history_item import GetReviewEngagementHistoryResponse200HistoryItem
        history: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.history, Unset):
            history = []
            for history_item_data in self.history:
                history_item = history_item_data.to_dict()
                history.append(history_item)



        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if history is not UNSET:
            field_dict["history"] = history
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_review_engagement_history_response_200_metadata import GetReviewEngagementHistoryResponse200Metadata
        from ..models.get_review_engagement_history_response_200_history_item import GetReviewEngagementHistoryResponse200HistoryItem
        d = dict(src_dict)
        history = []
        _history = d.pop("history", UNSET)
        for history_item_data in (_history or []):
            history_item = GetReviewEngagementHistoryResponse200HistoryItem.from_dict(history_item_data)



            history.append(history_item)


        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, GetReviewEngagementHistoryResponse200Metadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = GetReviewEngagementHistoryResponse200Metadata.from_dict(_metadata)




        get_review_engagement_history_response_200 = cls(
            history=history,
            metadata=metadata,
        )


        get_review_engagement_history_response_200.additional_properties = d
        return get_review_engagement_history_response_200

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
