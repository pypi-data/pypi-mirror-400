from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.nex_trip_result import NexTripResult
from ...models.problem_details import ProblemDetails
from ...types import Response


def _get_kwargs(
    stop_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        'method': 'get',
        'url': '/nextrip/{stop_id}'.format(
            stop_id=quote(str(stop_id), safe=''),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | NexTripResult | ProblemDetails | None:
    if response.status_code == 200:
        response_200 = NexTripResult.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = ProblemDetails.from_dict(response.json())

        return response_400

    if response.status_code == 500:
        response_500 = cast('Any', None)
        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | NexTripResult | ProblemDetails]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    stop_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | NexTripResult | ProblemDetails]:
    """Args:
        stop_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | NexTripResult | ProblemDetails]
    """
    kwargs = _get_kwargs(
        stop_id=stop_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    stop_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | NexTripResult | ProblemDetails | None:
    """Args:
        stop_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | NexTripResult | ProblemDetails
    """
    return sync_detailed(
        stop_id=stop_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    stop_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | NexTripResult | ProblemDetails]:
    """Args:
        stop_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | NexTripResult | ProblemDetails]
    """
    kwargs = _get_kwargs(
        stop_id=stop_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    stop_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | NexTripResult | ProblemDetails | None:
    """Args:
        stop_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | NexTripResult | ProblemDetails
    """
    return (
        await asyncio_detailed(
            stop_id=stop_id,
            client=client,
        )
    ).parsed
