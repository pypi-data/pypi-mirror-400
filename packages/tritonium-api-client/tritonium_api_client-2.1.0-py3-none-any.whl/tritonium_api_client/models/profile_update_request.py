from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.profile_update_request_notification_preferences import ProfileUpdateRequestNotificationPreferences





T = TypeVar("T", bound="ProfileUpdateRequest")



@_attrs_define
class ProfileUpdateRequest:
    """ 
        Attributes:
            name (Union[Unset, str]):
            company_name (Union[Unset, str]):
            role (Union[Unset, str]):
            timezone (Union[Unset, str]):
            notification_preferences (Union[Unset, ProfileUpdateRequestNotificationPreferences]):
     """

    name: Union[Unset, str] = UNSET
    company_name: Union[Unset, str] = UNSET
    role: Union[Unset, str] = UNSET
    timezone: Union[Unset, str] = UNSET
    notification_preferences: Union[Unset, 'ProfileUpdateRequestNotificationPreferences'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.profile_update_request_notification_preferences import ProfileUpdateRequestNotificationPreferences
        name = self.name

        company_name = self.company_name

        role = self.role

        timezone = self.timezone

        notification_preferences: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.notification_preferences, Unset):
            notification_preferences = self.notification_preferences.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if name is not UNSET:
            field_dict["name"] = name
        if company_name is not UNSET:
            field_dict["company_name"] = company_name
        if role is not UNSET:
            field_dict["role"] = role
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if notification_preferences is not UNSET:
            field_dict["notification_preferences"] = notification_preferences

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_update_request_notification_preferences import ProfileUpdateRequestNotificationPreferences
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        company_name = d.pop("company_name", UNSET)

        role = d.pop("role", UNSET)

        timezone = d.pop("timezone", UNSET)

        _notification_preferences = d.pop("notification_preferences", UNSET)
        notification_preferences: Union[Unset, ProfileUpdateRequestNotificationPreferences]
        if isinstance(_notification_preferences,  Unset):
            notification_preferences = UNSET
        else:
            notification_preferences = ProfileUpdateRequestNotificationPreferences.from_dict(_notification_preferences)




        profile_update_request = cls(
            name=name,
            company_name=company_name,
            role=role,
            timezone=timezone,
            notification_preferences=notification_preferences,
        )


        profile_update_request.additional_properties = d
        return profile_update_request

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
