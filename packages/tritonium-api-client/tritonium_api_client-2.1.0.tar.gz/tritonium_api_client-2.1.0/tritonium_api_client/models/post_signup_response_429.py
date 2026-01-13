from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.post_signup_response_429_error import PostSignupResponse429Error





T = TypeVar("T", bound="PostSignupResponse429")



@_attrs_define
class PostSignupResponse429:
    """ 
        Attributes:
            error (Union[Unset, PostSignupResponse429Error]):
     """

    error: Union[Unset, 'PostSignupResponse429Error'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.post_signup_response_429_error import PostSignupResponse429Error
        error: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.error, Unset):
            error = self.error.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_signup_response_429_error import PostSignupResponse429Error
        d = dict(src_dict)
        _error = d.pop("error", UNSET)
        error: Union[Unset, PostSignupResponse429Error]
        if isinstance(_error,  Unset):
            error = UNSET
        else:
            error = PostSignupResponse429Error.from_dict(_error)




        post_signup_response_429 = cls(
            error=error,
        )


        post_signup_response_429.additional_properties = d
        return post_signup_response_429

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
