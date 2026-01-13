from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.metrics_build import MetricsBuild
from typing import cast



def _get_kwargs(
    project_id: str,
    metrics_build_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/metricsBuilds/{metrics_build_id}".format(project_id=project_id,metrics_build_id=metrics_build_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | MetricsBuild | None:
    if response.status_code == 200:
        response_200 = MetricsBuild.from_dict(response.json())



        return response_200

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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | MetricsBuild]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    metrics_build_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Any | MetricsBuild]:
    """  Returns a specific metrics build.

    Args:
        project_id (str):
        metrics_build_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | MetricsBuild]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
metrics_build_id=metrics_build_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    metrics_build_id: str,
    *,
    client: AuthenticatedClient,

) -> Any | MetricsBuild | None:
    """  Returns a specific metrics build.

    Args:
        project_id (str):
        metrics_build_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | MetricsBuild
     """


    return sync_detailed(
        project_id=project_id,
metrics_build_id=metrics_build_id,
client=client,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    metrics_build_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Any | MetricsBuild]:
    """  Returns a specific metrics build.

    Args:
        project_id (str):
        metrics_build_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | MetricsBuild]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
metrics_build_id=metrics_build_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    metrics_build_id: str,
    *,
    client: AuthenticatedClient,

) -> Any | MetricsBuild | None:
    """  Returns a specific metrics build.

    Args:
        project_id (str):
        metrics_build_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | MetricsBuild
     """


    return (await asyncio_detailed(
        project_id=project_id,
metrics_build_id=metrics_build_id,
client=client,

    )).parsed
