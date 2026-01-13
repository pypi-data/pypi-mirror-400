from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResolveLlmRequest")


@_attrs_define
class ResolveLlmRequest:
    """
    Attributes:
        organization_id (int):
        key (str):
        selection_key (Union[None, Unset, str]):
    """

    organization_id: int
    key: str
    selection_key: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_id = self.organization_id

        key = self.key

        selection_key: Union[None, Unset, str]
        if isinstance(self.selection_key, Unset):
            selection_key = UNSET
        else:
            selection_key = self.selection_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organizationId": organization_id,
                "key": key,
            }
        )
        if selection_key is not UNSET:
            field_dict["selectionKey"] = selection_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_id = d.pop("organizationId")

        key = d.pop("key")

        def _parse_selection_key(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        selection_key = _parse_selection_key(d.pop("selectionKey", UNSET))

        resolve_llm_request = cls(
            organization_id=organization_id,
            key=key,
            selection_key=selection_key,
        )

        resolve_llm_request.additional_properties = d
        return resolve_llm_request

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
