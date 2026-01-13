from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.app_connection_request_metadata import AppConnectionRequestMetadata





T = TypeVar("T", bound="AppConnectionRequest")



@_attrs_define
class AppConnectionRequest:
    """ 
        Attributes:
            platform (str): External platform identifier (e.g. app_store_connect, google_play).
            credential_id (str):
            app_identifier (str):
            display_name (Union[Unset, str]):
            metadata (Union[Unset, AppConnectionRequestMetadata]):
     """

    platform: str
    credential_id: str
    app_identifier: str
    display_name: Union[Unset, str] = UNSET
    metadata: Union[Unset, 'AppConnectionRequestMetadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.app_connection_request_metadata import AppConnectionRequestMetadata
        platform = self.platform

        credential_id = self.credential_id

        app_identifier = self.app_identifier

        display_name = self.display_name

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "platform": platform,
            "credential_id": credential_id,
            "app_identifier": app_identifier,
        })
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.app_connection_request_metadata import AppConnectionRequestMetadata
        d = dict(src_dict)
        platform = d.pop("platform")

        credential_id = d.pop("credential_id")

        app_identifier = d.pop("app_identifier")

        display_name = d.pop("display_name", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, AppConnectionRequestMetadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = AppConnectionRequestMetadata.from_dict(_metadata)




        app_connection_request = cls(
            platform=platform,
            credential_id=credential_id,
            app_identifier=app_identifier,
            display_name=display_name,
            metadata=metadata,
        )


        app_connection_request.additional_properties = d
        return app_connection_request

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
