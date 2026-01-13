from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MapReduceRuntimeStatus")


@_attrs_define
class MapReduceRuntimeStatus:
    """
    Attributes:
        total_chunks (Union[None, Unset, int]):
        completed_chunks (Union[None, Unset, int]):
        header_captured (Union[None, Unset, bool]):
        stop_when_empty (Union[None, Unset, bool]):
        early_terminated (Union[None, Unset, bool]):
        termination_chunk_index (Union[None, Unset, int]):
        termination_reason (Union[None, Unset, str]):
    """

    total_chunks: Union[None, Unset, int] = UNSET
    completed_chunks: Union[None, Unset, int] = UNSET
    header_captured: Union[None, Unset, bool] = UNSET
    stop_when_empty: Union[None, Unset, bool] = UNSET
    early_terminated: Union[None, Unset, bool] = UNSET
    termination_chunk_index: Union[None, Unset, int] = UNSET
    termination_reason: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_chunks: Union[None, Unset, int]
        if isinstance(self.total_chunks, Unset):
            total_chunks = UNSET
        else:
            total_chunks = self.total_chunks

        completed_chunks: Union[None, Unset, int]
        if isinstance(self.completed_chunks, Unset):
            completed_chunks = UNSET
        else:
            completed_chunks = self.completed_chunks

        header_captured: Union[None, Unset, bool]
        if isinstance(self.header_captured, Unset):
            header_captured = UNSET
        else:
            header_captured = self.header_captured

        stop_when_empty: Union[None, Unset, bool]
        if isinstance(self.stop_when_empty, Unset):
            stop_when_empty = UNSET
        else:
            stop_when_empty = self.stop_when_empty

        early_terminated: Union[None, Unset, bool]
        if isinstance(self.early_terminated, Unset):
            early_terminated = UNSET
        else:
            early_terminated = self.early_terminated

        termination_chunk_index: Union[None, Unset, int]
        if isinstance(self.termination_chunk_index, Unset):
            termination_chunk_index = UNSET
        else:
            termination_chunk_index = self.termination_chunk_index

        termination_reason: Union[None, Unset, str]
        if isinstance(self.termination_reason, Unset):
            termination_reason = UNSET
        else:
            termination_reason = self.termination_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total_chunks is not UNSET:
            field_dict["totalChunks"] = total_chunks
        if completed_chunks is not UNSET:
            field_dict["completedChunks"] = completed_chunks
        if header_captured is not UNSET:
            field_dict["headerCaptured"] = header_captured
        if stop_when_empty is not UNSET:
            field_dict["stopWhenEmpty"] = stop_when_empty
        if early_terminated is not UNSET:
            field_dict["earlyTerminated"] = early_terminated
        if termination_chunk_index is not UNSET:
            field_dict["terminationChunkIndex"] = termination_chunk_index
        if termination_reason is not UNSET:
            field_dict["terminationReason"] = termination_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_total_chunks(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        total_chunks = _parse_total_chunks(d.pop("totalChunks", UNSET))

        def _parse_completed_chunks(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        completed_chunks = _parse_completed_chunks(d.pop("completedChunks", UNSET))

        def _parse_header_captured(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        header_captured = _parse_header_captured(d.pop("headerCaptured", UNSET))

        def _parse_stop_when_empty(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        stop_when_empty = _parse_stop_when_empty(d.pop("stopWhenEmpty", UNSET))

        def _parse_early_terminated(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        early_terminated = _parse_early_terminated(d.pop("earlyTerminated", UNSET))

        def _parse_termination_chunk_index(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        termination_chunk_index = _parse_termination_chunk_index(d.pop("terminationChunkIndex", UNSET))

        def _parse_termination_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        termination_reason = _parse_termination_reason(d.pop("terminationReason", UNSET))

        map_reduce_runtime_status = cls(
            total_chunks=total_chunks,
            completed_chunks=completed_chunks,
            header_captured=header_captured,
            stop_when_empty=stop_when_empty,
            early_terminated=early_terminated,
            termination_chunk_index=termination_chunk_index,
            termination_reason=termination_reason,
        )

        map_reduce_runtime_status.additional_properties = d
        return map_reduce_runtime_status

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
