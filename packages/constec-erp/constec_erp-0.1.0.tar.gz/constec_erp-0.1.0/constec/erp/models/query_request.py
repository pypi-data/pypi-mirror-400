from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="QueryRequest")



@_attrs_define
class QueryRequest:
    """ Request schema for raw SQL queries.

        Attributes:
            sql (str): SQL query to execute
            company_id (None | Unset | UUID):
            erp_system_id (None | Unset | UUID):
            connection_id (None | Unset | UUID):
            connection (str | Unset):  Default: 'production'.
            allow_mutations (bool | Unset): Required to be true for INSERT/UPDATE/DELETE/DROP queries Default: False.
            max_rows (int | Unset): Maximum rows to return Default: 1000.
            timeout (int | Unset): Query timeout in seconds Default: 30.
     """

    sql: str
    company_id: None | Unset | UUID = UNSET
    erp_system_id: None | Unset | UUID = UNSET
    connection_id: None | Unset | UUID = UNSET
    connection: str | Unset = 'production'
    allow_mutations: bool | Unset = False
    max_rows: int | Unset = 1000
    timeout: int | Unset = 30
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        sql = self.sql

        company_id: None | str | Unset
        if isinstance(self.company_id, Unset):
            company_id = UNSET
        elif isinstance(self.company_id, UUID):
            company_id = str(self.company_id)
        else:
            company_id = self.company_id

        erp_system_id: None | str | Unset
        if isinstance(self.erp_system_id, Unset):
            erp_system_id = UNSET
        elif isinstance(self.erp_system_id, UUID):
            erp_system_id = str(self.erp_system_id)
        else:
            erp_system_id = self.erp_system_id

        connection_id: None | str | Unset
        if isinstance(self.connection_id, Unset):
            connection_id = UNSET
        elif isinstance(self.connection_id, UUID):
            connection_id = str(self.connection_id)
        else:
            connection_id = self.connection_id

        connection = self.connection

        allow_mutations = self.allow_mutations

        max_rows = self.max_rows

        timeout = self.timeout


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "sql": sql,
        })
        if company_id is not UNSET:
            field_dict["company_id"] = company_id
        if erp_system_id is not UNSET:
            field_dict["erp_system_id"] = erp_system_id
        if connection_id is not UNSET:
            field_dict["connection_id"] = connection_id
        if connection is not UNSET:
            field_dict["connection"] = connection
        if allow_mutations is not UNSET:
            field_dict["allow_mutations"] = allow_mutations
        if max_rows is not UNSET:
            field_dict["max_rows"] = max_rows
        if timeout is not UNSET:
            field_dict["timeout"] = timeout

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sql = d.pop("sql")

        def _parse_company_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                company_id_type_0 = UUID(data)



                return company_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        company_id = _parse_company_id(d.pop("company_id", UNSET))


        def _parse_erp_system_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                erp_system_id_type_0 = UUID(data)



                return erp_system_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        erp_system_id = _parse_erp_system_id(d.pop("erp_system_id", UNSET))


        def _parse_connection_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                connection_id_type_0 = UUID(data)



                return connection_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        connection_id = _parse_connection_id(d.pop("connection_id", UNSET))


        connection = d.pop("connection", UNSET)

        allow_mutations = d.pop("allow_mutations", UNSET)

        max_rows = d.pop("max_rows", UNSET)

        timeout = d.pop("timeout", UNSET)

        query_request = cls(
            sql=sql,
            company_id=company_id,
            erp_system_id=erp_system_id,
            connection_id=connection_id,
            connection=connection,
            allow_mutations=allow_mutations,
            max_rows=max_rows,
            timeout=timeout,
        )


        query_request.additional_properties = d
        return query_request

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
