from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.user_summary import UserSummary
  from ..models.auth_token_pair import AuthTokenPair





T = TypeVar("T", bound="PostMicrosoftSsoResponse200")



@_attrs_define
class PostMicrosoftSsoResponse200:
    """ 
        Attributes:
            success (Union[Unset, bool]):
            user (Union[Unset, UserSummary]):
            tokens (Union[Unset, AuthTokenPair]):
     """

    success: Union[Unset, bool] = UNSET
    user: Union[Unset, 'UserSummary'] = UNSET
    tokens: Union[Unset, 'AuthTokenPair'] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.user_summary import UserSummary
        from ..models.auth_token_pair import AuthTokenPair
        success = self.success

        user: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        tokens: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tokens, Unset):
            tokens = self.tokens.to_dict()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
        })
        if success is not UNSET:
            field_dict["success"] = success
        if user is not UNSET:
            field_dict["user"] = user
        if tokens is not UNSET:
            field_dict["tokens"] = tokens

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_summary import UserSummary
        from ..models.auth_token_pair import AuthTokenPair
        d = dict(src_dict)
        success = d.pop("success", UNSET)

        _user = d.pop("user", UNSET)
        user: Union[Unset, UserSummary]
        if isinstance(_user,  Unset):
            user = UNSET
        else:
            user = UserSummary.from_dict(_user)




        _tokens = d.pop("tokens", UNSET)
        tokens: Union[Unset, AuthTokenPair]
        if isinstance(_tokens,  Unset):
            tokens = UNSET
        else:
            tokens = AuthTokenPair.from_dict(_tokens)




        post_microsoft_sso_response_200 = cls(
            success=success,
            user=user,
            tokens=tokens,
        )


        post_microsoft_sso_response_200.additional_properties = d
        return post_microsoft_sso_response_200

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
