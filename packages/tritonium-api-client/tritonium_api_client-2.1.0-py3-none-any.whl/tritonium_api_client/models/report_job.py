from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.report_job_status import ReportJobStatus
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime






T = TypeVar("T", bound="ReportJob")



@_attrs_define
class ReportJob:
    """ 
        Attributes:
            job_id (Union[Unset, str]):
            template_id (Union[Unset, str]):
            status (Union[Unset, ReportJobStatus]):
            output_format (Union[Unset, str]):
            download_url (Union[Unset, str]):
            error_message (Union[Unset, str]):
            created_at (Union[Unset, datetime.datetime]):
            completed_at (Union[Unset, datetime.datetime]):
     """

    job_id: Union[Unset, str] = UNSET
    template_id: Union[Unset, str] = UNSET
    status: Union[Unset, ReportJobStatus] = UNSET
    output_format: Union[Unset, str] = UNSET
    download_url: Union[Unset, str] = UNSET
    error_message: Union[Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    completed_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        template_id = self.template_id

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value


        output_format = self.output_format

        download_url = self.download_url

        error_message = self.error_message

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        completed_at: Union[Unset, str] = UNSET
        if not isinstance(self.completed_at, Unset):
            completed_at = self.completed_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if template_id is not UNSET:
            field_dict["template_id"] = template_id
        if status is not UNSET:
            field_dict["status"] = status
        if output_format is not UNSET:
            field_dict["output_format"] = output_format
        if download_url is not UNSET:
            field_dict["download_url"] = download_url
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id", UNSET)

        template_id = d.pop("template_id", UNSET)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ReportJobStatus]
        if isinstance(_status,  Unset):
            status = UNSET
        else:
            status = ReportJobStatus(_status)




        output_format = d.pop("output_format", UNSET)

        download_url = d.pop("download_url", UNSET)

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




        report_job = cls(
            job_id=job_id,
            template_id=template_id,
            status=status,
            output_format=output_format,
            download_url=download_url,
            error_message=error_message,
            created_at=created_at,
            completed_at=completed_at,
        )


        report_job.additional_properties = d
        return report_job

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
