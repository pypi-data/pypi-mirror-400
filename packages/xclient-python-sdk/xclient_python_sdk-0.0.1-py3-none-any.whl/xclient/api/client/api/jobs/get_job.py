from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error_response import ErrorResponse
from ...models.job import Job
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: int,
    *,
    cluster_id: Union[Unset, int] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["cluster_id"] = cluster_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/jobs/{id}",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ErrorResponse, Job]]:
    if response.status_code == 200:
        response_200 = Job.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = ErrorResponse.from_dict(response.json())

        return response_401
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[ErrorResponse, Job]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: int,
    *,
    client: AuthenticatedClient,
    cluster_id: Union[Unset, int] = UNSET,
) -> Response[Union[ErrorResponse, Job]]:
    """Get job details

     Get detailed job information by job ID and cluster ID

    Args:
        id (int):
        cluster_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, Job]]
    """

    kwargs = _get_kwargs(
        id=id,
        cluster_id=cluster_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient,
    cluster_id: Union[Unset, int] = UNSET,
) -> Optional[Union[ErrorResponse, Job]]:
    """Get job details

     Get detailed job information by job ID and cluster ID

    Args:
        id (int):
        cluster_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, Job]
    """

    return sync_detailed(
        id=id,
        client=client,
        cluster_id=cluster_id,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient,
    cluster_id: Union[Unset, int] = UNSET,
) -> Response[Union[ErrorResponse, Job]]:
    """Get job details

     Get detailed job information by job ID and cluster ID

    Args:
        id (int):
        cluster_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ErrorResponse, Job]]
    """

    kwargs = _get_kwargs(
        id=id,
        cluster_id=cluster_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient,
    cluster_id: Union[Unset, int] = UNSET,
) -> Optional[Union[ErrorResponse, Job]]:
    """Get job details

     Get detailed job information by job ID and cluster ID

    Args:
        id (int):
        cluster_id (Union[Unset, int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ErrorResponse, Job]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            cluster_id=cluster_id,
        )
    ).parsed
