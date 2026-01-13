from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.get_app_segments_response_200_segments_item import GetAppSegmentsResponse200SegmentsItem
  from ..models.get_app_segments_response_200_summary import GetAppSegmentsResponse200Summary
  from ..models.get_app_segments_response_200_metadata import GetAppSegmentsResponse200Metadata





T = TypeVar("T", bound="GetAppSegmentsResponse200")



@_attrs_define
class GetAppSegmentsResponse200:
    """ 
        Attributes:
            segments (Union[Unset, list['GetAppSegmentsResponse200SegmentsItem']]):
            summary (Union[Unset, GetAppSegmentsResponse200Summary]):
            metadata (Union[Unset, GetAppSegmentsResponse200Metadata]):
     """

    segments: Union[Unset, list['GetAppSegmentsResponse200SegmentsItem']] = UNSET
    summary: Union[Unset, 'GetAppSegmentsResponse200Summary'] = UNSET
    metadata: Union[Unset, 'GetAppSegmentsResponse200Metadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_app_segments_response_200_segments_item import GetAppSegmentsResponse200SegmentsItem
        from ..models.get_app_segments_response_200_summary import GetAppSegmentsResponse200Summary
        from ..models.get_app_segments_response_200_metadata import GetAppSegmentsResponse200Metadata
        segments: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.segments, Unset):
            segments = []
            for segments_item_data in self.segments:
                segments_item = segments_item_data.to_dict()
                segments.append(segments_item)



        summary: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.summary, Unset):
            summary = self.summary.to_dict()

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if segments is not UNSET:
            field_dict["segments"] = segments
        if summary is not UNSET:
            field_dict["summary"] = summary
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_app_segments_response_200_segments_item import GetAppSegmentsResponse200SegmentsItem
        from ..models.get_app_segments_response_200_summary import GetAppSegmentsResponse200Summary
        from ..models.get_app_segments_response_200_metadata import GetAppSegmentsResponse200Metadata
        d = dict(src_dict)
        segments = []
        _segments = d.pop("segments", UNSET)
        for segments_item_data in (_segments or []):
            segments_item = GetAppSegmentsResponse200SegmentsItem.from_dict(segments_item_data)



            segments.append(segments_item)


        _summary = d.pop("summary", UNSET)
        summary: Union[Unset, GetAppSegmentsResponse200Summary]
        if isinstance(_summary,  Unset):
            summary = UNSET
        else:
            summary = GetAppSegmentsResponse200Summary.from_dict(_summary)




        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, GetAppSegmentsResponse200Metadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = GetAppSegmentsResponse200Metadata.from_dict(_metadata)




        get_app_segments_response_200 = cls(
            segments=segments,
            summary=summary,
            metadata=metadata,
        )


        get_app_segments_response_200.additional_properties = d
        return get_app_segments_response_200

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
