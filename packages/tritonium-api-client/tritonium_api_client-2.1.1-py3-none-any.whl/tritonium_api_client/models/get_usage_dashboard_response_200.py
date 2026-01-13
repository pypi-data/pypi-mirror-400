from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.get_usage_dashboard_response_200_billing_period import GetUsageDashboardResponse200BillingPeriod
  from ..models.get_usage_dashboard_response_200_apps import GetUsageDashboardResponse200Apps
  from ..models.get_usage_dashboard_response_200_members import GetUsageDashboardResponse200Members
  from ..models.get_usage_dashboard_response_200_syncs import GetUsageDashboardResponse200Syncs





T = TypeVar("T", bound="GetUsageDashboardResponse200")



@_attrs_define
class GetUsageDashboardResponse200:
    """ 
        Attributes:
            billing_period (Union[Unset, GetUsageDashboardResponse200BillingPeriod]):
            apps (Union[Unset, GetUsageDashboardResponse200Apps]):
            members (Union[Unset, GetUsageDashboardResponse200Members]):
            syncs (Union[Unset, GetUsageDashboardResponse200Syncs]):
            current_cost (Union[Unset, float]):
            projected_cost (Union[Unset, float]):
     """

    billing_period: Union[Unset, 'GetUsageDashboardResponse200BillingPeriod'] = UNSET
    apps: Union[Unset, 'GetUsageDashboardResponse200Apps'] = UNSET
    members: Union[Unset, 'GetUsageDashboardResponse200Members'] = UNSET
    syncs: Union[Unset, 'GetUsageDashboardResponse200Syncs'] = UNSET
    current_cost: Union[Unset, float] = UNSET
    projected_cost: Union[Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.get_usage_dashboard_response_200_billing_period import GetUsageDashboardResponse200BillingPeriod
        from ..models.get_usage_dashboard_response_200_apps import GetUsageDashboardResponse200Apps
        from ..models.get_usage_dashboard_response_200_members import GetUsageDashboardResponse200Members
        from ..models.get_usage_dashboard_response_200_syncs import GetUsageDashboardResponse200Syncs
        billing_period: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.billing_period, Unset):
            billing_period = self.billing_period.to_dict()

        apps: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.apps, Unset):
            apps = self.apps.to_dict()

        members: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.members, Unset):
            members = self.members.to_dict()

        syncs: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.syncs, Unset):
            syncs = self.syncs.to_dict()

        current_cost = self.current_cost

        projected_cost = self.projected_cost


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if billing_period is not UNSET:
            field_dict["billing_period"] = billing_period
        if apps is not UNSET:
            field_dict["apps"] = apps
        if members is not UNSET:
            field_dict["members"] = members
        if syncs is not UNSET:
            field_dict["syncs"] = syncs
        if current_cost is not UNSET:
            field_dict["current_cost"] = current_cost
        if projected_cost is not UNSET:
            field_dict["projected_cost"] = projected_cost

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_usage_dashboard_response_200_billing_period import GetUsageDashboardResponse200BillingPeriod
        from ..models.get_usage_dashboard_response_200_apps import GetUsageDashboardResponse200Apps
        from ..models.get_usage_dashboard_response_200_members import GetUsageDashboardResponse200Members
        from ..models.get_usage_dashboard_response_200_syncs import GetUsageDashboardResponse200Syncs
        d = dict(src_dict)
        _billing_period = d.pop("billing_period", UNSET)
        billing_period: Union[Unset, GetUsageDashboardResponse200BillingPeriod]
        if isinstance(_billing_period,  Unset):
            billing_period = UNSET
        else:
            billing_period = GetUsageDashboardResponse200BillingPeriod.from_dict(_billing_period)




        _apps = d.pop("apps", UNSET)
        apps: Union[Unset, GetUsageDashboardResponse200Apps]
        if isinstance(_apps,  Unset):
            apps = UNSET
        else:
            apps = GetUsageDashboardResponse200Apps.from_dict(_apps)




        _members = d.pop("members", UNSET)
        members: Union[Unset, GetUsageDashboardResponse200Members]
        if isinstance(_members,  Unset):
            members = UNSET
        else:
            members = GetUsageDashboardResponse200Members.from_dict(_members)




        _syncs = d.pop("syncs", UNSET)
        syncs: Union[Unset, GetUsageDashboardResponse200Syncs]
        if isinstance(_syncs,  Unset):
            syncs = UNSET
        else:
            syncs = GetUsageDashboardResponse200Syncs.from_dict(_syncs)




        current_cost = d.pop("current_cost", UNSET)

        projected_cost = d.pop("projected_cost", UNSET)

        get_usage_dashboard_response_200 = cls(
            billing_period=billing_period,
            apps=apps,
            members=members,
            syncs=syncs,
            current_cost=current_cost,
            projected_cost=projected_cost,
        )


        get_usage_dashboard_response_200.additional_properties = d
        return get_usage_dashboard_response_200

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
