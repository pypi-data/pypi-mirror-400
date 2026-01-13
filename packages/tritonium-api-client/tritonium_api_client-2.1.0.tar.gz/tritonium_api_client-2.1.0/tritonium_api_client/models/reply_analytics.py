from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.reply_analytics_metrics import ReplyAnalyticsMetrics





T = TypeVar("T", bound="ReplyAnalytics")



@_attrs_define
class ReplyAnalytics:
    """ 
        Attributes:
            response_rate (Union[Unset, float]):
            average_response_time_minutes (Union[Unset, float]):
            escalations (Union[Unset, int]):
            metrics (Union[Unset, ReplyAnalyticsMetrics]):
     """

    response_rate: Union[Unset, float] = UNSET
    average_response_time_minutes: Union[Unset, float] = UNSET
    escalations: Union[Unset, int] = UNSET
    metrics: Union[Unset, 'ReplyAnalyticsMetrics'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.reply_analytics_metrics import ReplyAnalyticsMetrics
        response_rate = self.response_rate

        average_response_time_minutes = self.average_response_time_minutes

        escalations = self.escalations

        metrics: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = self.metrics.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if response_rate is not UNSET:
            field_dict["response_rate"] = response_rate
        if average_response_time_minutes is not UNSET:
            field_dict["average_response_time_minutes"] = average_response_time_minutes
        if escalations is not UNSET:
            field_dict["escalations"] = escalations
        if metrics is not UNSET:
            field_dict["metrics"] = metrics

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.reply_analytics_metrics import ReplyAnalyticsMetrics
        d = dict(src_dict)
        response_rate = d.pop("response_rate", UNSET)

        average_response_time_minutes = d.pop("average_response_time_minutes", UNSET)

        escalations = d.pop("escalations", UNSET)

        _metrics = d.pop("metrics", UNSET)
        metrics: Union[Unset, ReplyAnalyticsMetrics]
        if isinstance(_metrics,  Unset):
            metrics = UNSET
        else:
            metrics = ReplyAnalyticsMetrics.from_dict(_metrics)




        reply_analytics = cls(
            response_rate=response_rate,
            average_response_time_minutes=average_response_time_minutes,
            escalations=escalations,
            metrics=metrics,
        )


        reply_analytics.additional_properties = d
        return reply_analytics

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
