from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.insight import Insight





T = TypeVar("T", bound="PostAppsAnalyzeResponse200")



@_attrs_define
class PostAppsAnalyzeResponse200:
    """ 
        Attributes:
            success (Union[Unset, bool]):
            analysis_id (Union[Unset, str]):
            status (Union[Unset, str]):
            cached (Union[Unset, bool]):
            insights (Union[Unset, Insight]):
     """

    success: Union[Unset, bool] = UNSET
    analysis_id: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    cached: Union[Unset, bool] = UNSET
    insights: Union[Unset, 'Insight'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.insight import Insight
        success = self.success

        analysis_id = self.analysis_id

        status = self.status

        cached = self.cached

        insights: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.insights, Unset):
            insights = self.insights.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if success is not UNSET:
            field_dict["success"] = success
        if analysis_id is not UNSET:
            field_dict["analysis_id"] = analysis_id
        if status is not UNSET:
            field_dict["status"] = status
        if cached is not UNSET:
            field_dict["cached"] = cached
        if insights is not UNSET:
            field_dict["insights"] = insights

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.insight import Insight
        d = dict(src_dict)
        success = d.pop("success", UNSET)

        analysis_id = d.pop("analysis_id", UNSET)

        status = d.pop("status", UNSET)

        cached = d.pop("cached", UNSET)

        _insights = d.pop("insights", UNSET)
        insights: Union[Unset, Insight]
        if isinstance(_insights,  Unset):
            insights = UNSET
        else:
            insights = Insight.from_dict(_insights)




        post_apps_analyze_response_200 = cls(
            success=success,
            analysis_id=analysis_id,
            status=status,
            cached=cached,
            insights=insights,
        )


        post_apps_analyze_response_200.additional_properties = d
        return post_apps_analyze_response_200

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
