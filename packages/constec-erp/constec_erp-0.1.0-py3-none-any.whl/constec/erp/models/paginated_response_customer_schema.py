from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.customer_schema import CustomerSchema





T = TypeVar("T", bound="PaginatedResponseCustomerSchema")



@_attrs_define
class PaginatedResponseCustomerSchema:
    """ 
        Attributes:
            items (list[CustomerSchema]):
            total (int):
            limit (int):
            offset (int):
     """

    items: list[CustomerSchema]
    total: int
    limit: int
    offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.customer_schema import CustomerSchema
        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)



        total = self.total

        limit = self.limit

        offset = self.offset


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.customer_schema import CustomerSchema
        d = dict(src_dict)
        items = []
        _items = d.pop("items")
        for items_item_data in (_items):
            items_item = CustomerSchema.from_dict(items_item_data)



            items.append(items_item)


        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        paginated_response_customer_schema = cls(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )


        paginated_response_customer_schema.additional_properties = d
        return paginated_response_customer_schema

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
