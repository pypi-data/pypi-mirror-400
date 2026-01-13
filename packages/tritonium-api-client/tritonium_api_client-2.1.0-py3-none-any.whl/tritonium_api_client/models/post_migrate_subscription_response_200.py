from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.post_migrate_subscription_response_200_migration import PostMigrateSubscriptionResponse200Migration





T = TypeVar("T", bound="PostMigrateSubscriptionResponse200")



@_attrs_define
class PostMigrateSubscriptionResponse200:
    """ 
        Attributes:
            migration (Union[Unset, PostMigrateSubscriptionResponse200Migration]):
     """

    migration: Union[Unset, 'PostMigrateSubscriptionResponse200Migration'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.post_migrate_subscription_response_200_migration import PostMigrateSubscriptionResponse200Migration
        migration: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.migration, Unset):
            migration = self.migration.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if migration is not UNSET:
            field_dict["migration"] = migration

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_migrate_subscription_response_200_migration import PostMigrateSubscriptionResponse200Migration
        d = dict(src_dict)
        _migration = d.pop("migration", UNSET)
        migration: Union[Unset, PostMigrateSubscriptionResponse200Migration]
        if isinstance(_migration,  Unset):
            migration = UNSET
        else:
            migration = PostMigrateSubscriptionResponse200Migration.from_dict(_migration)




        post_migrate_subscription_response_200 = cls(
            migration=migration,
        )


        post_migrate_subscription_response_200.additional_properties = d
        return post_migrate_subscription_response_200

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
