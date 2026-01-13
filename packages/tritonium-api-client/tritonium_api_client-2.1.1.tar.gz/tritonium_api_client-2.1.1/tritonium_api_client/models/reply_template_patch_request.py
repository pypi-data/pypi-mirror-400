from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union






T = TypeVar("T", bound="ReplyTemplatePatchRequest")



@_attrs_define
class ReplyTemplatePatchRequest:
    """ 
        Attributes:
            name (Union[Unset, str]):
            language (Union[Unset, str]):
            body (Union[Unset, str]):
            tags (Union[Unset, list[str]]):
            retired (Union[Unset, bool]):
     """

    name: Union[Unset, str] = UNSET
    language: Union[Unset, str] = UNSET
    body: Union[Unset, str] = UNSET
    tags: Union[Unset, list[str]] = UNSET
    retired: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        name = self.name

        language = self.language

        body = self.body

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags



        retired = self.retired


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if language is not UNSET:
            field_dict["language"] = language
        if body is not UNSET:
            field_dict["body"] = body
        if tags is not UNSET:
            field_dict["tags"] = tags
        if retired is not UNSET:
            field_dict["retired"] = retired

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        language = d.pop("language", UNSET)

        body = d.pop("body", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))


        retired = d.pop("retired", UNSET)

        reply_template_patch_request = cls(
            name=name,
            language=language,
            body=body,
            tags=tags,
            retired=retired,
        )


        reply_template_patch_request.additional_properties = d
        return reply_template_patch_request

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
