from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="IssueSeverityPredictionRequestIssuesItem")



@_attrs_define
class IssueSeverityPredictionRequestIssuesItem:
    """ 
        Attributes:
            issue_id (Union[Unset, str]):
            label (Union[Unset, str]):
            evidence_count (Union[Unset, int]):
     """

    issue_id: Union[Unset, str] = UNSET
    label: Union[Unset, str] = UNSET
    evidence_count: Union[Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        issue_id = self.issue_id

        label = self.label

        evidence_count = self.evidence_count


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if issue_id is not UNSET:
            field_dict["issue_id"] = issue_id
        if label is not UNSET:
            field_dict["label"] = label
        if evidence_count is not UNSET:
            field_dict["evidence_count"] = evidence_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        issue_id = d.pop("issue_id", UNSET)

        label = d.pop("label", UNSET)

        evidence_count = d.pop("evidence_count", UNSET)

        issue_severity_prediction_request_issues_item = cls(
            issue_id=issue_id,
            label=label,
            evidence_count=evidence_count,
        )


        issue_severity_prediction_request_issues_item.additional_properties = d
        return issue_severity_prediction_request_issues_item

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
