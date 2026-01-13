from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.purge_result import PurgeResult
from ...types import Response


def _get_kwargs(
    guid: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/job/{guid}",
    }

    return _kwargs


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[PurgeResult]:
    if response.status_code == 200:
        response_200 = PurgeResult.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[PurgeResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[PurgeResult]:
    """
    Args:
        guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PurgeResult]
    """

    kwargs = _get_kwargs(
        guid=guid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[PurgeResult]:
    """
    Args:
        guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PurgeResult
    """

    return sync_detailed(
        guid=guid,
        client=client,
    ).parsed


async def asyncio_detailed(
    guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[PurgeResult]:
    """
    Args:
        guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PurgeResult]
    """

    kwargs = _get_kwargs(
        guid=guid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    guid: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[PurgeResult]:
    """
    Args:
        guid (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PurgeResult
    """

    return (
        await asyncio_detailed(
            guid=guid,
            client=client,
        )
    ).parsed
