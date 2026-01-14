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
    route_id: str,
    direction_id: int,
    place_code: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        'method': 'get',
        'url': '/nextrip/{route_id}/{direction_id}/{place_code}'.format(
            route_id=quote(str(route_id), safe=''),
            direction_id=quote(str(direction_id), safe=''),
            place_code=quote(str(place_code), safe=''),
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
    route_id: str,
    direction_id: int,
    place_code: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | NexTripResult | ProblemDetails]:
    """Args:
        route_id (str):
        direction_id (int):
        place_code (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | NexTripResult | ProblemDetails]
    """
    kwargs = _get_kwargs(
        route_id=route_id,
        direction_id=direction_id,
        place_code=place_code,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    route_id: str,
    direction_id: int,
    place_code: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | NexTripResult | ProblemDetails | None:
    """Args:
        route_id (str):
        direction_id (int):
        place_code (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | NexTripResult | ProblemDetails
    """
    return sync_detailed(
        route_id=route_id,
        direction_id=direction_id,
        place_code=place_code,
        client=client,
    ).parsed


async def asyncio_detailed(
    route_id: str,
    direction_id: int,
    place_code: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | NexTripResult | ProblemDetails]:
    """Args:
        route_id (str):
        direction_id (int):
        place_code (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | NexTripResult | ProblemDetails]
    """
    kwargs = _get_kwargs(
        route_id=route_id,
        direction_id=direction_id,
        place_code=place_code,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    route_id: str,
    direction_id: int,
    place_code: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | NexTripResult | ProblemDetails | None:
    """Args:
        route_id (str):
        direction_id (int):
        place_code (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | NexTripResult | ProblemDetails
    """
    return (
        await asyncio_detailed(
            route_id=route_id,
            direction_id=direction_id,
            place_code=place_code,
            client=client,
        )
    ).parsed
