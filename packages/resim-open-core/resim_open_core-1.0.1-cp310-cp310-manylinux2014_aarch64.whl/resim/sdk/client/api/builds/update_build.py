from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.build import Build
from ...models.update_build_input import UpdateBuildInput
from typing import cast



def _get_kwargs(
    project_id: str,
    build_id: str,
    *,
    body: UpdateBuildInput,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/projects/{project_id}/builds/{build_id}".format(project_id=project_id,build_id=build_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Build | None:
    if response.status_code == 200:
        response_200 = Build.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Build]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBuildInput,

) -> Response[Any | Build]:
    """  Updates the build.

    Args:
        project_id (str):
        build_id (str):
        body (UpdateBuildInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Build]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
build_id=build_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBuildInput,

) -> Any | Build | None:
    """  Updates the build.

    Args:
        project_id (str):
        build_id (str):
        body (UpdateBuildInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Build
     """


    return sync_detailed(
        project_id=project_id,
build_id=build_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBuildInput,

) -> Response[Any | Build]:
    """  Updates the build.

    Args:
        project_id (str):
        build_id (str):
        body (UpdateBuildInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Build]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
build_id=build_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    build_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBuildInput,

) -> Any | Build | None:
    """  Updates the build.

    Args:
        project_id (str):
        build_id (str):
        body (UpdateBuildInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Build
     """


    return (await asyncio_detailed(
        project_id=project_id,
build_id=build_id,
client=client,
body=body,

    )).parsed
