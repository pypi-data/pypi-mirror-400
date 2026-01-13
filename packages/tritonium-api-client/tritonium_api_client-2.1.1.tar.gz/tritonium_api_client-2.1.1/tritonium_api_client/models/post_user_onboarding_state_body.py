from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="PostUserOnboardingStateBody")



@_attrs_define
class PostUserOnboardingStateBody:
    """ 
        Attributes:
            onboarding_tour_completed (Union[Unset, bool]):
     """

    onboarding_tour_completed: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        onboarding_tour_completed = self.onboarding_tour_completed


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if onboarding_tour_completed is not UNSET:
            field_dict["onboarding_tour_completed"] = onboarding_tour_completed

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        onboarding_tour_completed = d.pop("onboarding_tour_completed", UNSET)

        post_user_onboarding_state_body = cls(
            onboarding_tour_completed=onboarding_tour_completed,
        )


        post_user_onboarding_state_body.additional_properties = d
        return post_user_onboarding_state_body

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
