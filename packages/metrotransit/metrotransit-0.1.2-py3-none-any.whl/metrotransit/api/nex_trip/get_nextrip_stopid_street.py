from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.problem_details import ProblemDetails
from ...models.street_stop_response import StreetStopResponse
from ...types import Response


def _get_kwargs(
    street: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        'method': 'get',
        'url': '/nextrip/stopid/{street}'.format(
            street=quote(str(street), safe=''),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | ProblemDetails | StreetStopResponse | None:
    if response.status_code == 200:
        response_200 = StreetStopResponse.from_dict(response.json())

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
) -> Response[Any | ProblemDetails | StreetStopResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    street: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | ProblemDetails | StreetStopResponse]:
    """Args:
        street (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | StreetStopResponse]
    """
    kwargs = _get_kwargs(
        street=street,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    street: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | ProblemDetails | StreetStopResponse | None:
    """Args:
        street (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | StreetStopResponse
    """
    return sync_detailed(
        street=street,
        client=client,
    ).parsed


async def asyncio_detailed(
    street: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Any | ProblemDetails | StreetStopResponse]:
    """Args:
        street (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ProblemDetails | StreetStopResponse]
    """
    kwargs = _get_kwargs(
        street=street,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    street: str,
    *,
    client: AuthenticatedClient | Client,
) -> Any | ProblemDetails | StreetStopResponse | None:
    """Args:
        street (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ProblemDetails | StreetStopResponse
    """
    return (
        await asyncio_detailed(
            street=street,
            client=client,
        )
    ).parsed
