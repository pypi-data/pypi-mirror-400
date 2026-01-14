from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.supplier_schema import SupplierSchema
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    supplier_id: str,
    *,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    json_connection_id: None | str | Unset
    if isinstance(connection_id, Unset):
        json_connection_id = UNSET
    elif isinstance(connection_id, UUID):
        json_connection_id = str(connection_id)
    else:
        json_connection_id = connection_id
    params["connection_id"] = json_connection_id

    json_erp_system_id: None | str | Unset
    if isinstance(erp_system_id, Unset):
        json_erp_system_id = UNSET
    elif isinstance(erp_system_id, UUID):
        json_erp_system_id = str(erp_system_id)
    else:
        json_erp_system_id = erp_system_id
    params["erp_system_id"] = json_erp_system_id

    json_company_id: None | str | Unset
    if isinstance(company_id, Unset):
        json_company_id = UNSET
    elif isinstance(company_id, UUID):
        json_company_id = str(company_id)
    else:
        json_company_id = company_id
    params["company_id"] = json_company_id

    params["connection"] = connection


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/erp/v1/suppliers/{supplier_id}".format(supplier_id=quote(str(supplier_id), safe=""),),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> HTTPValidationError | SupplierSchema | None:
    if response.status_code == 200:
        response_200 = SupplierSchema.from_dict(response.json())



        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())



        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[HTTPValidationError | SupplierSchema]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    supplier_id: str,
    *,
    client: AuthenticatedClient | Client,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',

) -> Response[HTTPValidationError | SupplierSchema]:
    """ Get Supplier

     Get a single supplier by ID (pro_Cod).

    Args:
        supplier_id (str):
        connection_id (None | Unset | UUID): Direct connection UUID
        erp_system_id (None | Unset | UUID): ERP System UUID
        company_id (None | Unset | UUID): Company UUID
        connection (str | Unset): Connection slug Default: 'production'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SupplierSchema]
     """


    kwargs = _get_kwargs(
        supplier_id=supplier_id,
connection_id=connection_id,
erp_system_id=erp_system_id,
company_id=company_id,
connection=connection,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    supplier_id: str,
    *,
    client: AuthenticatedClient | Client,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',

) -> HTTPValidationError | SupplierSchema | None:
    """ Get Supplier

     Get a single supplier by ID (pro_Cod).

    Args:
        supplier_id (str):
        connection_id (None | Unset | UUID): Direct connection UUID
        erp_system_id (None | Unset | UUID): ERP System UUID
        company_id (None | Unset | UUID): Company UUID
        connection (str | Unset): Connection slug Default: 'production'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SupplierSchema
     """


    return sync_detailed(
        supplier_id=supplier_id,
client=client,
connection_id=connection_id,
erp_system_id=erp_system_id,
company_id=company_id,
connection=connection,

    ).parsed

async def asyncio_detailed(
    supplier_id: str,
    *,
    client: AuthenticatedClient | Client,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',

) -> Response[HTTPValidationError | SupplierSchema]:
    """ Get Supplier

     Get a single supplier by ID (pro_Cod).

    Args:
        supplier_id (str):
        connection_id (None | Unset | UUID): Direct connection UUID
        erp_system_id (None | Unset | UUID): ERP System UUID
        company_id (None | Unset | UUID): Company UUID
        connection (str | Unset): Connection slug Default: 'production'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SupplierSchema]
     """


    kwargs = _get_kwargs(
        supplier_id=supplier_id,
connection_id=connection_id,
erp_system_id=erp_system_id,
company_id=company_id,
connection=connection,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    supplier_id: str,
    *,
    client: AuthenticatedClient | Client,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',

) -> HTTPValidationError | SupplierSchema | None:
    """ Get Supplier

     Get a single supplier by ID (pro_Cod).

    Args:
        supplier_id (str):
        connection_id (None | Unset | UUID): Direct connection UUID
        erp_system_id (None | Unset | UUID): ERP System UUID
        company_id (None | Unset | UUID): Company UUID
        connection (str | Unset): Connection slug Default: 'production'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SupplierSchema
     """


    return (await asyncio_detailed(
        supplier_id=supplier_id,
client=client,
connection_id=connection_id,
erp_system_id=erp_system_id,
company_id=company_id,
connection=connection,

    )).parsed
