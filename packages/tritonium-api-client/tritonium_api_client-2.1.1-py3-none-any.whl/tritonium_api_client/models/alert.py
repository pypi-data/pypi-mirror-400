from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.alert_severity import AlertSeverity
from ..models.alert_status import AlertStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime

if TYPE_CHECKING:
  from ..models.alert_metadata import AlertMetadata





T = TypeVar("T", bound="Alert")



@_attrs_define
class Alert:
    """ 
        Attributes:
            alert_id (Union[Unset, str]):
            title (Union[Unset, str]):
            description (Union[Unset, str]):
            severity (Union[Unset, AlertSeverity]):
            status (Union[Unset, AlertStatus]):
            created_at (Union[Unset, datetime.datetime]):
            updated_at (Union[Unset, datetime.datetime]):
            metadata (Union[Unset, AlertMetadata]):
     """

    alert_id: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    severity: Union[Unset, AlertSeverity] = UNSET
    status: Union[Unset, AlertStatus] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    metadata: Union[Unset, 'AlertMetadata'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.alert_metadata import AlertMetadata
        alert_id = self.alert_id

        title = self.title

        description = self.description

        severity: Union[Unset, str] = UNSET
        if not isinstance(self.severity, Unset):
            severity = self.severity.value


        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if alert_id is not UNSET:
            field_dict["alert_id"] = alert_id
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if severity is not UNSET:
            field_dict["severity"] = severity
        if status is not UNSET:
            field_dict["status"] = status
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.alert_metadata import AlertMetadata
        d = dict(src_dict)
        alert_id = d.pop("alert_id", UNSET)

        title = d.pop("title", UNSET)

        description = d.pop("description", UNSET)

        _severity = d.pop("severity", UNSET)
        severity: Union[Unset, AlertSeverity]
        if isinstance(_severity,  Unset):
            severity = UNSET
        else:
            severity = AlertSeverity(_severity)




        _status = d.pop("status", UNSET)
        status: Union[Unset, AlertStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = AlertStatus(_status)




        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _updated_at = d.pop("updated_at", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at,  Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)




        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, AlertMetadata]
        if isinstance(_metadata,  Unset):
            metadata = UNSET
        else:
            metadata = AlertMetadata.from_dict(_metadata)




        alert = cls(
            alert_id=alert_id,
            title=title,
            description=description,
            severity=severity,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata,
        )


        alert.additional_properties = d
        return alert

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
