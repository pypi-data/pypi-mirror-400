from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.pool_with_machines import PoolWithMachines
from ...types import UNSET, Response, Unset


def _get_kwargs(
    pool_id: UUID,
    *,
    include_machines: bool | Unset = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["include_machines"] = include_machines

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/pools/{pool_id}".format(
            pool_id=quote(str(pool_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PoolWithMachines | None:
    if response.status_code == 200:
        response_200 = PoolWithMachines.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | PoolWithMachines]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    include_machines: bool | Unset = False,
) -> Response[HTTPValidationError | PoolWithMachines]:
    """Get Pool

     Get a specific pool by ID.

    Args:
        pool_id (UUID):
        include_machines (bool | Unset): Include full machine details Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PoolWithMachines]
    """

    kwargs = _get_kwargs(
        pool_id=pool_id,
        include_machines=include_machines,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    include_machines: bool | Unset = False,
) -> HTTPValidationError | PoolWithMachines | None:
    """Get Pool

     Get a specific pool by ID.

    Args:
        pool_id (UUID):
        include_machines (bool | Unset): Include full machine details Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PoolWithMachines
    """

    return sync_detailed(
        pool_id=pool_id,
        client=client,
        include_machines=include_machines,
    ).parsed


async def asyncio_detailed(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    include_machines: bool | Unset = False,
) -> Response[HTTPValidationError | PoolWithMachines]:
    """Get Pool

     Get a specific pool by ID.

    Args:
        pool_id (UUID):
        include_machines (bool | Unset): Include full machine details Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PoolWithMachines]
    """

    kwargs = _get_kwargs(
        pool_id=pool_id,
        include_machines=include_machines,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    pool_id: UUID,
    *,
    client: AuthenticatedClient,
    include_machines: bool | Unset = False,
) -> HTTPValidationError | PoolWithMachines | None:
    """Get Pool

     Get a specific pool by ID.

    Args:
        pool_id (UUID):
        include_machines (bool | Unset): Include full machine details Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PoolWithMachines
    """

    return (
        await asyncio_detailed(
            pool_id=pool_id,
            client=client,
            include_machines=include_machines,
        )
    ).parsed
