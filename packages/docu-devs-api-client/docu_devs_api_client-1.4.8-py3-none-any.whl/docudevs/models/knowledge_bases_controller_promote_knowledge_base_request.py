from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="KnowledgeBasesControllerPromoteKnowledgeBaseRequest")


@_attrs_define
class KnowledgeBasesControllerPromoteKnowledgeBaseRequest:
    """
    Attributes:
        case_id (int):
    """

    case_id: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        case_id = self.case_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "caseId": case_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        case_id = d.pop("caseId")

        knowledge_bases_controller_promote_knowledge_base_request = cls(
            case_id=case_id,
        )

        knowledge_bases_controller_promote_knowledge_base_request.additional_properties = d
        return knowledge_bases_controller_promote_knowledge_base_request

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
