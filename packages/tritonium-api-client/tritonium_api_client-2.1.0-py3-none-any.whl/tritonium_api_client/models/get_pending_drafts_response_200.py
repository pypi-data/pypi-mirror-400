from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.pending_draft import PendingDraft





T = TypeVar("T", bound="GetPendingDraftsResponse200")



@_attrs_define
class GetPendingDraftsResponse200:
    """ 
        Attributes:
            drafts (Union[Unset, list['PendingDraft']]):
     """

    drafts: Union[Unset, list['PendingDraft']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.pending_draft import PendingDraft
        drafts: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.drafts, Unset):
            drafts = []
            for drafts_item_data in self.drafts:
                drafts_item = drafts_item_data.to_dict()
                drafts.append(drafts_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if drafts is not UNSET:
            field_dict["drafts"] = drafts

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pending_draft import PendingDraft
        d = dict(src_dict)
        drafts = []
        _drafts = d.pop("drafts", UNSET)
        for drafts_item_data in (_drafts or []):
            drafts_item = PendingDraft.from_dict(drafts_item_data)



            drafts.append(drafts_item)


        get_pending_drafts_response_200 = cls(
            drafts=drafts,
        )


        get_pending_drafts_response_200.additional_properties = d
        return get_pending_drafts_response_200

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
