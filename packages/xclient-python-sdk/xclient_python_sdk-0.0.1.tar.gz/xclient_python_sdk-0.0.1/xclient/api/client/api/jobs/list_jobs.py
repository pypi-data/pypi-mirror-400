from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.job_list_response import JobListResponse
from ...models.job_status import JobStatus
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    status: Union[Unset, JobStatus] = UNSET,
    user_id: Union[Unset, int] = UNSET,
    team_id: Union[Unset, int] = UNSET,
    cluster_id: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["page_size"] = page_size

    json_status: Union[Unset, str] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    params["user_id"] = user_id

    params["team_id"] = team_id

    params["cluster_id"] = cluster_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/jobs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, JobListResponse]]:
    if response.status_code == 200:
        response_200 = JobListResponse.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, JobListResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    status: Union[Unset, JobStatus] = UNSET,
    user_id: Union[Unset, int] = UNSET,
    team_id: Union[Unset, int] = UNSET,
    cluster_id: Union[Unset, int] = UNSET,
) -> Response[Union[ErrorResponse, JobListResponse]]:
    """Get job list

     Get job list，支持分页和过滤

    Args:
        page (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 20.
        status (Union[Unset, JobStatus]):  Example: pending.
        user_id (Union[Unset, int]):
        team_id (Union[Unset, int]):
        cluster_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, JobListResponse]]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        status=status,
        user_id=user_id,
        team_id=team_id,
        cluster_id=cluster_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    status: Union[Unset, JobStatus] = UNSET,
    user_id: Union[Unset, int] = UNSET,
    team_id: Union[Unset, int] = UNSET,
    cluster_id: Union[Unset, int] = UNSET,
) -> Optional[Union[ErrorResponse, JobListResponse]]:
    """Get job list

     Get job list，支持分页和过滤

    Args:
        page (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 20.
        status (Union[Unset, JobStatus]):  Example: pending.
        user_id (Union[Unset, int]):
        team_id (Union[Unset, int]):
        cluster_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, JobListResponse]
    """

    return sync_detailed(
        client=client,
        page=page,
        page_size=page_size,
        status=status,
        user_id=user_id,
        team_id=team_id,
        cluster_id=cluster_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    status: Union[Unset, JobStatus] = UNSET,
    user_id: Union[Unset, int] = UNSET,
    team_id: Union[Unset, int] = UNSET,
    cluster_id: Union[Unset, int] = UNSET,
) -> Response[Union[ErrorResponse, JobListResponse]]:
    """Get job list

     Get job list，支持分页和过滤

    Args:
        page (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 20.
        status (Union[Unset, JobStatus]):  Example: pending.
        user_id (Union[Unset, int]):
        team_id (Union[Unset, int]):
        cluster_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, JobListResponse]]
    """

    kwargs = _get_kwargs(
        page=page,
        page_size=page_size,
        status=status,
        user_id=user_id,
        team_id=team_id,
        cluster_id=cluster_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    page: Union[Unset, int] = 1,
    page_size: Union[Unset, int] = 20,
    status: Union[Unset, JobStatus] = UNSET,
    user_id: Union[Unset, int] = UNSET,
    team_id: Union[Unset, int] = UNSET,
    cluster_id: Union[Unset, int] = UNSET,
) -> Optional[Union[ErrorResponse, JobListResponse]]:
    """Get job list

     Get job list，支持分页和过滤

    Args:
        page (Union[Unset, int]):  Default: 1.
        page_size (Union[Unset, int]):  Default: 20.
        status (Union[Unset, JobStatus]):  Example: pending.
        user_id (Union[Unset, int]):
        team_id (Union[Unset, int]):
        cluster_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, JobListResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            page_size=page_size,
            status=status,
            user_id=user_id,
            team_id=team_id,
            cluster_id=cluster_id,
        )
    ).parsed
