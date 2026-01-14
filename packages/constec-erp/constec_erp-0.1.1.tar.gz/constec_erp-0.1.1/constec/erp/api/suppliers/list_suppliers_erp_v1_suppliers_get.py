from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.http_validation_error import HTTPValidationError
from ...models.paginated_response_supplier_schema import PaginatedResponseSupplierSchema
from ...types import UNSET, Unset
from typing import cast
from uuid import UUID



def _get_kwargs(
    *,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',
    cuit: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    email: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,

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

    json_cuit: None | str | Unset
    if isinstance(cuit, Unset):
        json_cuit = UNSET
    else:
        json_cuit = cuit
    params["cuit"] = json_cuit

    json_name: None | str | Unset
    if isinstance(name, Unset):
        json_name = UNSET
    else:
        json_name = name
    params["name"] = json_name

    json_email: None | str | Unset
    if isinstance(email, Unset):
        json_email = UNSET
    else:
        json_email = email
    params["email"] = json_email

    params["limit"] = limit

    params["offset"] = offset


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/erp/v1/suppliers",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> HTTPValidationError | PaginatedResponseSupplierSchema | None:
    if response.status_code == 200:
        response_200 = PaginatedResponseSupplierSchema.from_dict(response.json())



        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())



        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[HTTPValidationError | PaginatedResponseSupplierSchema]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',
    cuit: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    email: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,

) -> Response[HTTPValidationError | PaginatedResponseSupplierSchema]:
    """ List Suppliers

     List/search suppliers from Bejerman database.

    Provide ONE of: connection_id, erp_system_id, or company_id.
    Filters can be combined. All filters use partial (LIKE) matching.

    Args:
        connection_id (None | Unset | UUID): Direct connection UUID
        erp_system_id (None | Unset | UUID): ERP System UUID
        company_id (None | Unset | UUID): Company UUID
        connection (str | Unset): Connection slug Default: 'production'.
        cuit (None | str | Unset): Filter by CUIT (partial match)
        name (None | str | Unset): Filter by name/razon social (partial match)
        email (None | str | Unset): Filter by email (partial match)
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PaginatedResponseSupplierSchema]
     """


    kwargs = _get_kwargs(
        connection_id=connection_id,
erp_system_id=erp_system_id,
company_id=company_id,
connection=connection,
cuit=cuit,
name=name,
email=email,
limit=limit,
offset=offset,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient | Client,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',
    cuit: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    email: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,

) -> HTTPValidationError | PaginatedResponseSupplierSchema | None:
    """ List Suppliers

     List/search suppliers from Bejerman database.

    Provide ONE of: connection_id, erp_system_id, or company_id.
    Filters can be combined. All filters use partial (LIKE) matching.

    Args:
        connection_id (None | Unset | UUID): Direct connection UUID
        erp_system_id (None | Unset | UUID): ERP System UUID
        company_id (None | Unset | UUID): Company UUID
        connection (str | Unset): Connection slug Default: 'production'.
        cuit (None | str | Unset): Filter by CUIT (partial match)
        name (None | str | Unset): Filter by name/razon social (partial match)
        email (None | str | Unset): Filter by email (partial match)
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PaginatedResponseSupplierSchema
     """


    return sync_detailed(
        client=client,
connection_id=connection_id,
erp_system_id=erp_system_id,
company_id=company_id,
connection=connection,
cuit=cuit,
name=name,
email=email,
limit=limit,
offset=offset,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',
    cuit: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    email: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,

) -> Response[HTTPValidationError | PaginatedResponseSupplierSchema]:
    """ List Suppliers

     List/search suppliers from Bejerman database.

    Provide ONE of: connection_id, erp_system_id, or company_id.
    Filters can be combined. All filters use partial (LIKE) matching.

    Args:
        connection_id (None | Unset | UUID): Direct connection UUID
        erp_system_id (None | Unset | UUID): ERP System UUID
        company_id (None | Unset | UUID): Company UUID
        connection (str | Unset): Connection slug Default: 'production'.
        cuit (None | str | Unset): Filter by CUIT (partial match)
        name (None | str | Unset): Filter by name/razon social (partial match)
        email (None | str | Unset): Filter by email (partial match)
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PaginatedResponseSupplierSchema]
     """


    kwargs = _get_kwargs(
        connection_id=connection_id,
erp_system_id=erp_system_id,
company_id=company_id,
connection=connection,
cuit=cuit,
name=name,
email=email,
limit=limit,
offset=offset,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    connection_id: None | Unset | UUID = UNSET,
    erp_system_id: None | Unset | UUID = UNSET,
    company_id: None | Unset | UUID = UNSET,
    connection: str | Unset = 'production',
    cuit: None | str | Unset = UNSET,
    name: None | str | Unset = UNSET,
    email: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,

) -> HTTPValidationError | PaginatedResponseSupplierSchema | None:
    """ List Suppliers

     List/search suppliers from Bejerman database.

    Provide ONE of: connection_id, erp_system_id, or company_id.
    Filters can be combined. All filters use partial (LIKE) matching.

    Args:
        connection_id (None | Unset | UUID): Direct connection UUID
        erp_system_id (None | Unset | UUID): ERP System UUID
        company_id (None | Unset | UUID): Company UUID
        connection (str | Unset): Connection slug Default: 'production'.
        cuit (None | str | Unset): Filter by CUIT (partial match)
        name (None | str | Unset): Filter by name/razon social (partial match)
        email (None | str | Unset): Filter by email (partial match)
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PaginatedResponseSupplierSchema
     """


    return (await asyncio_detailed(
        client=client,
connection_id=connection_id,
erp_system_id=erp_system_id,
company_id=company_id,
connection=connection,
cuit=cuit,
name=name,
email=email,
limit=limit,
offset=offset,

    )).parsed
