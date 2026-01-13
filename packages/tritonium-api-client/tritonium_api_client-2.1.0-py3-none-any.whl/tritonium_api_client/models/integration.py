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

if TYPE_CHECKING:
  from ..models.integration_configuration import IntegrationConfiguration





T = TypeVar("T", bound="Integration")



@_attrs_define
class Integration:
    """ 
        Attributes:
            integration_id (Union[Unset, str]):
            provider (Union[Unset, str]):
            status (Union[Unset, str]):
            connected_at (Union[Unset, datetime.datetime]):
            configuration (Union[Unset, IntegrationConfiguration]):
     """

    integration_id: Union[Unset, str] = UNSET
    provider: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    connected_at: Union[Unset, datetime.datetime] = UNSET
    configuration: Union[Unset, 'IntegrationConfiguration'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.integration_configuration import IntegrationConfiguration
        integration_id = self.integration_id

        provider = self.provider

        status = self.status

        connected_at: Union[Unset, str] = UNSET
        if not isinstance(self.connected_at, Unset):
            connected_at = self.connected_at.isoformat()

        configuration: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.configuration, Unset):
            configuration = self.configuration.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if integration_id is not UNSET:
            field_dict["integration_id"] = integration_id
        if provider is not UNSET:
            field_dict["provider"] = provider
        if status is not UNSET:
            field_dict["status"] = status
        if connected_at is not UNSET:
            field_dict["connected_at"] = connected_at
        if configuration is not UNSET:
            field_dict["configuration"] = configuration

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.integration_configuration import IntegrationConfiguration
        d = dict(src_dict)
        integration_id = d.pop("integration_id", UNSET)

        provider = d.pop("provider", UNSET)

        status = d.pop("status", UNSET)

        _connected_at = d.pop("connected_at", UNSET)
        connected_at: Union[Unset, datetime.datetime]
        if isinstance(_connected_at,  Unset):
            connected_at = UNSET
        else:
            connected_at = isoparse(_connected_at)




        _configuration = d.pop("configuration", UNSET)
        configuration: Union[Unset, IntegrationConfiguration]
        if isinstance(_configuration,  Unset):
            configuration = UNSET
        else:
            configuration = IntegrationConfiguration.from_dict(_configuration)




        integration = cls(
            integration_id=integration_id,
            provider=provider,
            status=status,
            connected_at=connected_at,
            configuration=configuration,
        )


        integration.additional_properties = d
        return integration

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
