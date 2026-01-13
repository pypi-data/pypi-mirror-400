from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.export_job_status import ExportJobStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime






T = TypeVar("T", bound="ExportJob")



@_attrs_define
class ExportJob:
    """ 
        Attributes:
            job_id (Union[Unset, str]):
            export_type (Union[Unset, str]):
            format_ (Union[Unset, str]):
            status (Union[Unset, ExportJobStatus]):
            file_name (Union[Unset, str]):
            download_url (Union[Unset, str]):
            file_size_bytes (Union[Unset, int]):
            record_count (Union[Unset, int]):
            error_message (Union[Unset, str]):
            created_at (Union[Unset, datetime.datetime]):
            completed_at (Union[Unset, datetime.datetime]):
            expires_at (Union[Unset, datetime.datetime]):
     """

    job_id: Union[Unset, str] = UNSET
    export_type: Union[Unset, str] = UNSET
    format_: Union[Unset, str] = UNSET
    status: Union[Unset, ExportJobStatus] = UNSET
    file_name: Union[Unset, str] = UNSET
    download_url: Union[Unset, str] = UNSET
    file_size_bytes: Union[Unset, int] = UNSET
    record_count: Union[Unset, int] = UNSET
    error_message: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    completed_at: Union[Unset, datetime.datetime] = UNSET
    expires_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        export_type = self.export_type

        format_ = self.format_

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        file_name = self.file_name

        download_url = self.download_url

        file_size_bytes = self.file_size_bytes

        record_count = self.record_count

        error_message = self.error_message

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        completed_at: Union[Unset, str] = UNSET
        if not isinstance(self.completed_at, Unset):
            completed_at = self.completed_at.isoformat()

        expires_at: Union[Unset, str] = UNSET
        if not isinstance(self.expires_at, Unset):
            expires_at = self.expires_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if export_type is not UNSET:
            field_dict["export_type"] = export_type
        if format_ is not UNSET:
            field_dict["format"] = format_
        if status is not UNSET:
            field_dict["status"] = status
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
        if download_url is not UNSET:
            field_dict["download_url"] = download_url
        if file_size_bytes is not UNSET:
            field_dict["file_size_bytes"] = file_size_bytes
        if record_count is not UNSET:
            field_dict["record_count"] = record_count
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id", UNSET)

        export_type = d.pop("export_type", UNSET)

        format_ = d.pop("format", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ExportJobStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = ExportJobStatus(_status)




        file_name = d.pop("file_name", UNSET)

        download_url = d.pop("download_url", UNSET)

        file_size_bytes = d.pop("file_size_bytes", UNSET)

        record_count = d.pop("record_count", UNSET)

        error_message = d.pop("error_message", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        _completed_at = d.pop("completed_at", UNSET)
        completed_at: Union[Unset, datetime.datetime]
        if isinstance(_completed_at,  Unset):
            completed_at = UNSET
        else:
            completed_at = isoparse(_completed_at)




        _expires_at = d.pop("expires_at", UNSET)
        expires_at: Union[Unset, datetime.datetime]
        if isinstance(_expires_at,  Unset):
            expires_at = UNSET
        else:
            expires_at = isoparse(_expires_at)




        export_job = cls(
            job_id=job_id,
            export_type=export_type,
            format_=format_,
            status=status,
            file_name=file_name,
            download_url=download_url,
            file_size_bytes=file_size_bytes,
            record_count=record_count,
            error_message=error_message,
            created_at=created_at,
            completed_at=completed_at,
            expires_at=expires_at,
        )


        export_job.additional_properties = d
        return export_job

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
