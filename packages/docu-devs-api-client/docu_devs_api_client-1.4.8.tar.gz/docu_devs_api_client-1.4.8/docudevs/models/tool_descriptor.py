from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.tool_type import ToolType, check_tool_type
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tool_descriptor_config_type_1 import ToolDescriptorConfigType1


T = TypeVar("T", bound="ToolDescriptor")


@_attrs_define
class ToolDescriptor:
    """
    Attributes:
        type_ (ToolType):
        config (Union['ToolDescriptorConfigType1', None, Unset]):
    """

    type_: ToolType
    config: Union["ToolDescriptorConfigType1", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.tool_descriptor_config_type_1 import ToolDescriptorConfigType1

        type_: str = self.type_

        config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, ToolDescriptorConfigType1):
            config = self.config.to_dict()
        else:
            config = self.config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_descriptor_config_type_1 import ToolDescriptorConfigType1

        d = dict(src_dict)
        type_ = check_tool_type(d.pop("type"))

        def _parse_config(data: object) -> Union["ToolDescriptorConfigType1", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_1 = ToolDescriptorConfigType1.from_dict(data)

                return config_type_1
            except:  # noqa: E722
                pass
            return cast(Union["ToolDescriptorConfigType1", None, Unset], data)

        config = _parse_config(d.pop("config", UNSET))

        tool_descriptor = cls(
            type_=type_,
            config=config,
        )

        tool_descriptor.additional_properties = d
        return tool_descriptor

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
