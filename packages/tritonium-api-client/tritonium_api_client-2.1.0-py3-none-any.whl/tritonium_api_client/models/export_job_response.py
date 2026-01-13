from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.export_job import ExportJob





T = TypeVar("T", bound="ExportJobResponse")



@_attrs_define
class ExportJobResponse:
    """ 
        Attributes:
            job (Union[Unset, ExportJob]):
     """

    job: Union[Unset, 'ExportJob'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.export_job import ExportJob
        job: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.job, Unset):
            job = self.job.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if job is not UNSET:
            field_dict["job"] = job

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.export_job import ExportJob
        d = dict(src_dict)
        _job = d.pop("job", UNSET)
        job: Union[Unset, ExportJob]
        if isinstance(_job,  Unset):
            job = UNSET
        else:
            job = ExportJob.from_dict(_job)




        export_job_response = cls(
            job=job,
        )


        export_job_response.additional_properties = d
        return export_job_response

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
