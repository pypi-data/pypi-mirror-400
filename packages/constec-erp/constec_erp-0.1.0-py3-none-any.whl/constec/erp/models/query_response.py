from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.query_response_data_item import QueryResponseDataItem





T = TypeVar("T", bound="QueryResponse")



@_attrs_define
class QueryResponse:
    """ Response schema for raw SQL queries.

        Attributes:
            data (list[QueryResponseDataItem]):
            row_count (int):
            columns (list[str]):
            execution_time_ms (float):
            truncated (bool | Unset):  Default: False.
     """

    data: list[QueryResponseDataItem]
    row_count: int
    columns: list[str]
    execution_time_ms: float
    truncated: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.query_response_data_item import QueryResponseDataItem
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)



        row_count = self.row_count

        columns = self.columns



        execution_time_ms = self.execution_time_ms

        truncated = self.truncated


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "data": data,
            "row_count": row_count,
            "columns": columns,
            "execution_time_ms": execution_time_ms,
        })
        if truncated is not UNSET:
            field_dict["truncated"] = truncated

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.query_response_data_item import QueryResponseDataItem
        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in (_data):
            data_item = QueryResponseDataItem.from_dict(data_item_data)



            data.append(data_item)


        row_count = d.pop("row_count")

        columns = cast(list[str], d.pop("columns"))


        execution_time_ms = d.pop("execution_time_ms")

        truncated = d.pop("truncated", UNSET)

        query_response = cls(
            data=data,
            row_count=row_count,
            columns=columns,
            execution_time_ms=execution_time_ms,
            truncated=truncated,
        )


        query_response.additional_properties = d
        return query_response

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
