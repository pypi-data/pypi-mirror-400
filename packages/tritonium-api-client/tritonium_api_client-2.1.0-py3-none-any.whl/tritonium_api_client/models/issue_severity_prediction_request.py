from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.issue_severity_prediction_request_issues_item import IssueSeverityPredictionRequestIssuesItem





T = TypeVar("T", bound="IssueSeverityPredictionRequest")



@_attrs_define
class IssueSeverityPredictionRequest:
    """ 
        Attributes:
            app_uuid (str):
            issues (list['IssueSeverityPredictionRequestIssuesItem']):
            window_days (Union[Unset, int]):
     """

    app_uuid: str
    issues: list['IssueSeverityPredictionRequestIssuesItem']
    window_days: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.issue_severity_prediction_request_issues_item import IssueSeverityPredictionRequestIssuesItem
        app_uuid = self.app_uuid

        issues = []
        for issues_item_data in self.issues:
            issues_item = issues_item_data.to_dict()
            issues.append(issues_item)



        window_days = self.window_days


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "app_uuid": app_uuid,
            "issues": issues,
        })
        if window_days is not UNSET:
            field_dict["window_days"] = window_days

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.issue_severity_prediction_request_issues_item import IssueSeverityPredictionRequestIssuesItem
        d = dict(src_dict)
        app_uuid = d.pop("app_uuid")

        issues = []
        _issues = d.pop("issues")
        for issues_item_data in (_issues):
            issues_item = IssueSeverityPredictionRequestIssuesItem.from_dict(issues_item_data)



            issues.append(issues_item)


        window_days = d.pop("window_days", UNSET)

        issue_severity_prediction_request = cls(
            app_uuid=app_uuid,
            issues=issues,
            window_days=window_days,
        )


        issue_severity_prediction_request.additional_properties = d
        return issue_severity_prediction_request

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
