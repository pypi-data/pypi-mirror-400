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
  from ..models.prediction_response_series_item import PredictionResponseSeriesItem
  from ..models.prediction_response_metrics import PredictionResponseMetrics





T = TypeVar("T", bound="PredictionResponse")



@_attrs_define
class PredictionResponse:
    """ 
        Attributes:
            request_id (Union[Unset, str]):
            generated_at (Union[Unset, datetime.datetime]):
            metrics (Union[Unset, PredictionResponseMetrics]):
            series (Union[Unset, list['PredictionResponseSeriesItem']]):
     """

    request_id: Union[Unset, str] = UNSET
    generated_at: Union[Unset, datetime.datetime] = UNSET
    metrics: Union[Unset, 'PredictionResponseMetrics'] = UNSET
    series: Union[Unset, list['PredictionResponseSeriesItem']] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.prediction_response_series_item import PredictionResponseSeriesItem
        from ..models.prediction_response_metrics import PredictionResponseMetrics
        request_id = self.request_id

        generated_at: Union[Unset, str] = UNSET
        if not isinstance(self.generated_at, Unset):
            generated_at = self.generated_at.isoformat()

        metrics: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = self.metrics.to_dict()

        series: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.series, Unset):
            series = []
            for series_item_data in self.series:
                series_item = series_item_data.to_dict()
                series.append(series_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if request_id is not UNSET:
            field_dict["request_id"] = request_id
        if generated_at is not UNSET:
            field_dict["generated_at"] = generated_at
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if series is not UNSET:
            field_dict["series"] = series

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prediction_response_series_item import PredictionResponseSeriesItem
        from ..models.prediction_response_metrics import PredictionResponseMetrics
        d = dict(src_dict)
        request_id = d.pop("request_id", UNSET)

        _generated_at = d.pop("generated_at", UNSET)
        generated_at: Union[Unset, datetime.datetime]
        if isinstance(_generated_at,  Unset):
            generated_at = UNSET
        else:
            generated_at = isoparse(_generated_at)




        _metrics = d.pop("metrics", UNSET)
        metrics: Union[Unset, PredictionResponseMetrics]
        if isinstance(_metrics,  Unset):
            metrics = UNSET
        else:
            metrics = PredictionResponseMetrics.from_dict(_metrics)




        series = []
        _series = d.pop("series", UNSET)
        for series_item_data in (_series or []):
            series_item = PredictionResponseSeriesItem.from_dict(series_item_data)



            series.append(series_item)


        prediction_response = cls(
            request_id=request_id,
            generated_at=generated_at,
            metrics=metrics,
            series=series,
        )


        prediction_response.additional_properties = d
        return prediction_response

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
