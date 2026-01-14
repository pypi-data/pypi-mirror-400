from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.place import Place
from ...models.problem_details import ProblemDetails
from ...types import Response


def _get_kwargs(
    route_id: str,
    direction_id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        'method': 'get',
        'url': '/nextrip/stops/{route_id}/{direction_id}'.format(
            route_id=quote(str(route_id), safe=''),
            direction_id=quote(str(direction_id), safe=''),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ProblemDetails | list[Place] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = Place.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Any | ProblemDetails | list[Place]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    route_id: str,
    direction_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | ProblemDetails | list[Place]]:
    """Args:
        route_id (str):
        direction_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | list[Place]]
    """
    kwargs = _get_kwargs(
        route_id=route_id,
        direction_id=direction_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    route_id: str,
    direction_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | ProblemDetails | list[Place] | None:
    """Args:
        route_id (str):
        direction_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | list[Place]
    """
    return sync_detailed(
        route_id=route_id,
        direction_id=direction_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    route_id: str,
    direction_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | ProblemDetails | list[Place]]:
    """Args:
        route_id (str):
        direction_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | list[Place]]
    """
    kwargs = _get_kwargs(
        route_id=route_id,
        direction_id=direction_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    route_id: str,
    direction_id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Any | ProblemDetails | list[Place] | None:
    """Args:
        route_id (str):
        direction_id (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | list[Place]
    """
    return (
        await asyncio_detailed(
            route_id=route_id,
            direction_id=direction_id,
            client=client,
        )
    ).parsed
