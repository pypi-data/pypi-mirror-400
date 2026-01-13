from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResolvedOcrProviderDto")


@_attrs_define
class ResolvedOcrProviderDto:
    """
    Attributes:
        provider_id (int):
        endpoint (str):
        model_id (str):
        features (Any):
        api_key (str):
    """

    provider_id: int
    endpoint: str
    model_id: str
    features: Any
    api_key: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider_id = self.provider_id

        endpoint = self.endpoint

        model_id = self.model_id

        features = self.features

        api_key = self.api_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "providerId": provider_id,
                "endpoint": endpoint,
                "modelId": model_id,
                "features": features,
                "apiKey": api_key,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        provider_id = d.pop("providerId")

        endpoint = d.pop("endpoint")

        model_id = d.pop("modelId")

        features = d.pop("features")

        api_key = d.pop("apiKey")

        resolved_ocr_provider_dto = cls(
            provider_id=provider_id,
            endpoint=endpoint,
            model_id=model_id,
            features=features,
            api_key=api_key,
        )

        resolved_ocr_provider_dto.additional_properties = d
        return resolved_ocr_provider_dto

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
