from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.error_response_error_details import ErrorResponseErrorDetails





T = TypeVar("T", bound="ErrorResponseError")



@_attrs_define
class ErrorResponseError:
    """ 
        Attributes:
            code (str): Machine readable error code.
            message (str): Human readable error description.
            details (Union[Unset, ErrorResponseErrorDetails]): Optional structured error details.
     """

    code: str
    message: str
    details: Union[Unset, 'ErrorResponseErrorDetails'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.error_response_error_details import ErrorResponseErrorDetails
        code = self.code

        message = self.message

        details: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.details, Unset):
            details = self.details.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "code": code,
            "message": message,
        })
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_response_error_details import ErrorResponseErrorDetails
        d = dict(src_dict)
        code = d.pop("code")

        message = d.pop("message")

        _details = d.pop("details", UNSET)
        details: Union[Unset, ErrorResponseErrorDetails]
        if isinstance(_details,  Unset):
            details = UNSET
        else:
            details = ErrorResponseErrorDetails.from_dict(_details)




        error_response_error = cls(
            code=code,
            message=message,
            details=details,
        )


        error_response_error.additional_properties = d
        return error_response_error

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
