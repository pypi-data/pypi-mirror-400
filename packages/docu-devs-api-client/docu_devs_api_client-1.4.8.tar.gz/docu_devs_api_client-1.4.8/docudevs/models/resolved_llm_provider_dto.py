from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResolvedLlmProviderDto")


@_attrs_define
class ResolvedLlmProviderDto:
    """
    Attributes:
        provider_id (int):
        api_url (str):
        model_type (str):
        kwargs (Any):
        api_key (str):
        deployment_name (Union[None, Unset, str]):
    """

    provider_id: int
    api_url: str
    model_type: str
    kwargs: Any
    api_key: str
    deployment_name: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider_id = self.provider_id

        api_url = self.api_url

        model_type = self.model_type

        kwargs = self.kwargs

        api_key = self.api_key

        deployment_name: Union[None, Unset, str]
        if isinstance(self.deployment_name, Unset):
            deployment_name = UNSET
        else:
            deployment_name = self.deployment_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "providerId": provider_id,
                "apiUrl": api_url,
                "modelType": model_type,
                "kwargs": kwargs,
                "apiKey": api_key,
            }
        )
        if deployment_name is not UNSET:
            field_dict["deploymentName"] = deployment_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        provider_id = d.pop("providerId")

        api_url = d.pop("apiUrl")

        model_type = d.pop("modelType")

        kwargs = d.pop("kwargs")

        api_key = d.pop("apiKey")

        def _parse_deployment_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        deployment_name = _parse_deployment_name(d.pop("deploymentName", UNSET))

        resolved_llm_provider_dto = cls(
            provider_id=provider_id,
            api_url=api_url,
            model_type=model_type,
            kwargs=kwargs,
            api_key=api_key,
            deployment_name=deployment_name,
        )

        resolved_llm_provider_dto.additional_properties = d
        return resolved_llm_provider_dto

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
