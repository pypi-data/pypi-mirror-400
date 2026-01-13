from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import Union
import datetime






T = TypeVar("T", bound="ReplyTemplate")



@_attrs_define
class ReplyTemplate:
    """ 
        Attributes:
            template_id (Union[Unset, str]):
            name (Union[Unset, str]):
            language (Union[Unset, str]):
            body (Union[Unset, str]):
            tags (Union[Unset, list[str]]):
            created_at (Union[Unset, datetime.datetime]):
            updated_at (Union[Unset, datetime.datetime]):
     """

    template_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    language: Union[Unset, str] = UNSET
    body: Union[Unset, str] = UNSET
    tags: Union[Unset, list[str]] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        template_id = self.template_id

        name = self.name

        language = self.language

        body = self.body

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags



        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if template_id is not UNSET:
            field_dict["template_id"] = template_id
        if name is not UNSET:
            field_dict["name"] = name
        if language is not UNSET:
            field_dict["language"] = language
        if body is not UNSET:
            field_dict["body"] = body
        if tags is not UNSET:
            field_dict["tags"] = tags
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        template_id = d.pop("template_id", UNSET)

        name = d.pop("name", UNSET)

        language = d.pop("language", UNSET)

        body = d.pop("body", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))


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




        reply_template = cls(
            template_id=template_id,
            name=name,
            language=language,
            body=body,
            tags=tags,
            created_at=created_at,
            updated_at=updated_at,
        )


        reply_template.additional_properties = d
        return reply_template

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
