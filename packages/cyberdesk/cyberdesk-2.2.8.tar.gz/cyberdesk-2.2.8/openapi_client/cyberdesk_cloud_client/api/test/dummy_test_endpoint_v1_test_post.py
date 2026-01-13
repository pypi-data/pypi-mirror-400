from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dummy_test_endpoint_v1_test_post_response_dummy_test_endpoint_v1_test_post import (
    DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    idempotency_key: UUID | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(idempotency_key, Unset):
        headers["Idempotency-Key"] = idempotency_key

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/v1/test",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost | None:
    if response.status_code == 200:
        response_200 = DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    idempotency_key: UUID | Unset = UNSET,
) -> Response[DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost]:
    """Dummy Test Endpoint

     Test endpoint that performs a sequence of actions:
    1. Click at three different places
    2. Right click
    3. Take a screenshot

    Returns all action results and the screenshot base64.

    Args:
        idempotency_key (UUID | Unset):  Example: 550e8400-e29b-41d4-a716-446655440000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost]
    """

    kwargs = _get_kwargs(
        idempotency_key=idempotency_key,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    idempotency_key: UUID | Unset = UNSET,
) -> DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost | None:
    """Dummy Test Endpoint

     Test endpoint that performs a sequence of actions:
    1. Click at three different places
    2. Right click
    3. Take a screenshot

    Returns all action results and the screenshot base64.

    Args:
        idempotency_key (UUID | Unset):  Example: 550e8400-e29b-41d4-a716-446655440000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost
    """

    return sync_detailed(
        client=client,
        idempotency_key=idempotency_key,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    idempotency_key: UUID | Unset = UNSET,
) -> Response[DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost]:
    """Dummy Test Endpoint

     Test endpoint that performs a sequence of actions:
    1. Click at three different places
    2. Right click
    3. Take a screenshot

    Returns all action results and the screenshot base64.

    Args:
        idempotency_key (UUID | Unset):  Example: 550e8400-e29b-41d4-a716-446655440000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost]
    """

    kwargs = _get_kwargs(
        idempotency_key=idempotency_key,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    idempotency_key: UUID | Unset = UNSET,
) -> DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost | None:
    """Dummy Test Endpoint

     Test endpoint that performs a sequence of actions:
    1. Click at three different places
    2. Right click
    3. Take a screenshot

    Returns all action results and the screenshot base64.

    Args:
        idempotency_key (UUID | Unset):  Example: 550e8400-e29b-41d4-a716-446655440000.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DummyTestEndpointV1TestPostResponseDummyTestEndpointV1TestPost
    """

    return (
        await asyncio_detailed(
            client=client,
            idempotency_key=idempotency_key,
        )
    ).parsed
