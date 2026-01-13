from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.competitor_metadata import CompetitorMetadata





T = TypeVar("T", bound="Competitor")



@_attrs_define
class Competitor:
    """ 
        Attributes:
            platform (Union[Unset, str]):
            external_app_id (Union[Unset, str]):
            display_name (Union[Unset, str]):
            metadata (Union[Unset, CompetitorMetadata]):
     """

    platform: Union[Unset, str] = UNSET
    external_app_id: Union[Unset, str] = UNSET
    display_name: Union[Unset, str] = UNSET
    metadata: Union[Unset, 'CompetitorMetadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.competitor_metadata import CompetitorMetadata
        platform = self.platform

        external_app_id = self.external_app_id

        display_name = self.display_name

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if platform is not UNSET:
            field_dict["platform"] = platform
        if external_app_id is not UNSET:
            field_dict["external_app_id"] = external_app_id
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.competitor_metadata import CompetitorMetadata
        d = dict(src_dict)
        platform = d.pop("platform", UNSET)

        external_app_id = d.pop("external_app_id", UNSET)

        display_name = d.pop("display_name", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CompetitorMetadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = CompetitorMetadata.from_dict(_metadata)




        competitor = cls(
            platform=platform,
            external_app_id=external_app_id,
            display_name=display_name,
            metadata=metadata,
        )


        competitor.additional_properties = d
        return competitor

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
