import datetime
from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.paginated_response_run_response import PaginatedResponseRunResponse
from ...models.run_field import RunField
from ...models.run_status import RunStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    workflow_id: None | Unset | UUID = UNSET,
    machine_id: None | Unset | UUID = UNSET,
    session_id: None | Unset | UUID = UNSET,
    status: None | RunStatus | Unset = UNSET,
    created_at_from: datetime.datetime | None | Unset = UNSET,
    created_at_to: datetime.datetime | None | Unset = UNSET,
    fields: list[RunField] | None | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_workflow_id: None | str | Unset
    if isinstance(workflow_id, Unset):
        json_workflow_id = UNSET
    elif isinstance(workflow_id, UUID):
        json_workflow_id = str(workflow_id)
    else:
        json_workflow_id = workflow_id
    params["workflow_id"] = json_workflow_id

    json_machine_id: None | str | Unset
    if isinstance(machine_id, Unset):
        json_machine_id = UNSET
    elif isinstance(machine_id, UUID):
        json_machine_id = str(machine_id)
    else:
        json_machine_id = machine_id
    params["machine_id"] = json_machine_id

    json_session_id: None | str | Unset
    if isinstance(session_id, Unset):
        json_session_id = UNSET
    elif isinstance(session_id, UUID):
        json_session_id = str(session_id)
    else:
        json_session_id = session_id
    params["session_id"] = json_session_id

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    elif isinstance(status, RunStatus):
        json_status = status.value
    else:
        json_status = status
    params["status"] = json_status

    json_created_at_from: None | str | Unset
    if isinstance(created_at_from, Unset):
        json_created_at_from = UNSET
    elif isinstance(created_at_from, datetime.datetime):
        json_created_at_from = created_at_from.isoformat()
    else:
        json_created_at_from = created_at_from
    params["created_at_from"] = json_created_at_from

    json_created_at_to: None | str | Unset
    if isinstance(created_at_to, Unset):
        json_created_at_to = UNSET
    elif isinstance(created_at_to, datetime.datetime):
        json_created_at_to = created_at_to.isoformat()
    else:
        json_created_at_to = created_at_to
    params["created_at_to"] = json_created_at_to

    json_fields: list[str] | None | Unset
    if isinstance(fields, Unset):
        json_fields = UNSET
    elif isinstance(fields, list):
        json_fields = []
        for fields_type_0_item_data in fields:
            fields_type_0_item = fields_type_0_item_data.value
            json_fields.append(fields_type_0_item)

    else:
        json_fields = fields
    params["fields"] = json_fields

    params["skip"] = skip

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/runs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PaginatedResponseRunResponse | None:
    if response.status_code == 200:
        response_200 = PaginatedResponseRunResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | PaginatedResponseRunResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    workflow_id: None | Unset | UUID = UNSET,
    machine_id: None | Unset | UUID = UNSET,
    session_id: None | Unset | UUID = UNSET,
    status: None | RunStatus | Unset = UNSET,
    created_at_from: datetime.datetime | None | Unset = UNSET,
    created_at_to: datetime.datetime | None | Unset = UNSET,
    fields: list[RunField] | None | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
) -> Response[HTTPValidationError | PaginatedResponseRunResponse]:
    """List Runs

     List all runs for the authenticated organization.

    Supports pagination and filtering by workflow, machine, and status.
    Returns runs with their associated workflow and machine data.

    Args:
        workflow_id (None | Unset | UUID): Filter by workflow ID
        machine_id (None | Unset | UUID): Filter by machine ID
        session_id (None | Unset | UUID): Filter by session ID
        status (None | RunStatus | Unset): Filter by run status
        created_at_from (datetime.datetime | None | Unset): Filter runs created at or after this
            ISO timestamp (UTC)
        created_at_to (datetime.datetime | None | Unset): Filter runs created at or before this
            ISO timestamp (UTC)
        fields (list[RunField] | None | Unset): Optional list of fields to include per run. Always
            includes: id, workflow_id, machine_id, status, created_at. Provide multiple 'fields='
            params to include more.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PaginatedResponseRunResponse]
    """

    kwargs = _get_kwargs(
        workflow_id=workflow_id,
        machine_id=machine_id,
        session_id=session_id,
        status=status,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        fields=fields,
        skip=skip,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    workflow_id: None | Unset | UUID = UNSET,
    machine_id: None | Unset | UUID = UNSET,
    session_id: None | Unset | UUID = UNSET,
    status: None | RunStatus | Unset = UNSET,
    created_at_from: datetime.datetime | None | Unset = UNSET,
    created_at_to: datetime.datetime | None | Unset = UNSET,
    fields: list[RunField] | None | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
) -> HTTPValidationError | PaginatedResponseRunResponse | None:
    """List Runs

     List all runs for the authenticated organization.

    Supports pagination and filtering by workflow, machine, and status.
    Returns runs with their associated workflow and machine data.

    Args:
        workflow_id (None | Unset | UUID): Filter by workflow ID
        machine_id (None | Unset | UUID): Filter by machine ID
        session_id (None | Unset | UUID): Filter by session ID
        status (None | RunStatus | Unset): Filter by run status
        created_at_from (datetime.datetime | None | Unset): Filter runs created at or after this
            ISO timestamp (UTC)
        created_at_to (datetime.datetime | None | Unset): Filter runs created at or before this
            ISO timestamp (UTC)
        fields (list[RunField] | None | Unset): Optional list of fields to include per run. Always
            includes: id, workflow_id, machine_id, status, created_at. Provide multiple 'fields='
            params to include more.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PaginatedResponseRunResponse
    """

    return sync_detailed(
        client=client,
        workflow_id=workflow_id,
        machine_id=machine_id,
        session_id=session_id,
        status=status,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        fields=fields,
        skip=skip,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    workflow_id: None | Unset | UUID = UNSET,
    machine_id: None | Unset | UUID = UNSET,
    session_id: None | Unset | UUID = UNSET,
    status: None | RunStatus | Unset = UNSET,
    created_at_from: datetime.datetime | None | Unset = UNSET,
    created_at_to: datetime.datetime | None | Unset = UNSET,
    fields: list[RunField] | None | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
) -> Response[HTTPValidationError | PaginatedResponseRunResponse]:
    """List Runs

     List all runs for the authenticated organization.

    Supports pagination and filtering by workflow, machine, and status.
    Returns runs with their associated workflow and machine data.

    Args:
        workflow_id (None | Unset | UUID): Filter by workflow ID
        machine_id (None | Unset | UUID): Filter by machine ID
        session_id (None | Unset | UUID): Filter by session ID
        status (None | RunStatus | Unset): Filter by run status
        created_at_from (datetime.datetime | None | Unset): Filter runs created at or after this
            ISO timestamp (UTC)
        created_at_to (datetime.datetime | None | Unset): Filter runs created at or before this
            ISO timestamp (UTC)
        fields (list[RunField] | None | Unset): Optional list of fields to include per run. Always
            includes: id, workflow_id, machine_id, status, created_at. Provide multiple 'fields='
            params to include more.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PaginatedResponseRunResponse]
    """

    kwargs = _get_kwargs(
        workflow_id=workflow_id,
        machine_id=machine_id,
        session_id=session_id,
        status=status,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        fields=fields,
        skip=skip,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    workflow_id: None | Unset | UUID = UNSET,
    machine_id: None | Unset | UUID = UNSET,
    session_id: None | Unset | UUID = UNSET,
    status: None | RunStatus | Unset = UNSET,
    created_at_from: datetime.datetime | None | Unset = UNSET,
    created_at_to: datetime.datetime | None | Unset = UNSET,
    fields: list[RunField] | None | Unset = UNSET,
    skip: int | Unset = 0,
    limit: int | Unset = 100,
) -> HTTPValidationError | PaginatedResponseRunResponse | None:
    """List Runs

     List all runs for the authenticated organization.

    Supports pagination and filtering by workflow, machine, and status.
    Returns runs with their associated workflow and machine data.

    Args:
        workflow_id (None | Unset | UUID): Filter by workflow ID
        machine_id (None | Unset | UUID): Filter by machine ID
        session_id (None | Unset | UUID): Filter by session ID
        status (None | RunStatus | Unset): Filter by run status
        created_at_from (datetime.datetime | None | Unset): Filter runs created at or after this
            ISO timestamp (UTC)
        created_at_to (datetime.datetime | None | Unset): Filter runs created at or before this
            ISO timestamp (UTC)
        fields (list[RunField] | None | Unset): Optional list of fields to include per run. Always
            includes: id, workflow_id, machine_id, status, created_at. Provide multiple 'fields='
            params to include more.
        skip (int | Unset):  Default: 0.
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PaginatedResponseRunResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            workflow_id=workflow_id,
            machine_id=machine_id,
            session_id=session_id,
            status=status,
            created_at_from=created_at_from,
            created_at_to=created_at_to,
            fields=fields,
            skip=skip,
            limit=limit,
        )
    ).parsed
