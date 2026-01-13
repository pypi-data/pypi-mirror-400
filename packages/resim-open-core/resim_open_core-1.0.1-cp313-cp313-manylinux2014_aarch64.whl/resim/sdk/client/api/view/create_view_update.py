from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.view_session_update import ViewSessionUpdate
from ...types import File, FileTypes
from io import BytesIO
from typing import cast



def _get_kwargs(
    view_session_id: str,
    view_update_id: int,
    *,
    body: File,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/view/sessions/{view_session_id}/updates/{view_update_id}".format(view_session_id=view_session_id,view_update_id=view_update_id,),
    }

    _kwargs["content"] = body.payload

    headers["Content-Type"] = "application/octet-stream"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ViewSessionUpdate | None:
    if response.status_code == 201:
        response_201 = ViewSessionUpdate.from_dict(response.json())



        return response_201

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 403:
        response_403 = cast(Any, None)
        return response_403

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ViewSessionUpdate]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    view_session_id: str,
    view_update_id: int,
    *,
    client: AuthenticatedClient,
    body: File,

) -> Response[Any | ViewSessionUpdate]:
    """  Adds an update to the View session.  Updates will be serialized sequentially by ID.

    Args:
        view_session_id (str):
        view_update_id (int):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ViewSessionUpdate]
     """


    kwargs = _get_kwargs(
        view_session_id=view_session_id,
view_update_id=view_update_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    view_session_id: str,
    view_update_id: int,
    *,
    client: AuthenticatedClient,
    body: File,

) -> Any | ViewSessionUpdate | None:
    """  Adds an update to the View session.  Updates will be serialized sequentially by ID.

    Args:
        view_session_id (str):
        view_update_id (int):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ViewSessionUpdate
     """


    return sync_detailed(
        view_session_id=view_session_id,
view_update_id=view_update_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    view_session_id: str,
    view_update_id: int,
    *,
    client: AuthenticatedClient,
    body: File,

) -> Response[Any | ViewSessionUpdate]:
    """  Adds an update to the View session.  Updates will be serialized sequentially by ID.

    Args:
        view_session_id (str):
        view_update_id (int):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ViewSessionUpdate]
     """


    kwargs = _get_kwargs(
        view_session_id=view_session_id,
view_update_id=view_update_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    view_session_id: str,
    view_update_id: int,
    *,
    client: AuthenticatedClient,
    body: File,

) -> Any | ViewSessionUpdate | None:
    """  Adds an update to the View session.  Updates will be serialized sequentially by ID.

    Args:
        view_session_id (str):
        view_update_id (int):
        body (File):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ViewSessionUpdate
     """


    return (await asyncio_detailed(
        view_session_id=view_session_id,
view_update_id=view_update_id,
client=client,
body=body,

    )).parsed
