from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.test_suite import TestSuite
from typing import cast



def _get_kwargs(
    project_id: str,
    test_suite_id: str,
    revision: int,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/suites/{test_suite_id}/revisions/{revision}".format(project_id=project_id,test_suite_id=test_suite_id,revision=revision,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | TestSuite | None:
    if response.status_code == 200:
        response_200 = TestSuite.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | TestSuite]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    test_suite_id: str,
    revision: int,
    *,
    client: AuthenticatedClient,

) -> Response[Any | TestSuite]:
    """  Returns a specified revision of a test suite.

    Args:
        project_id (str):
        test_suite_id (str):
        revision (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | TestSuite]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
test_suite_id=test_suite_id,
revision=revision,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    test_suite_id: str,
    revision: int,
    *,
    client: AuthenticatedClient,

) -> Any | TestSuite | None:
    """  Returns a specified revision of a test suite.

    Args:
        project_id (str):
        test_suite_id (str):
        revision (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | TestSuite
     """


    return sync_detailed(
        project_id=project_id,
test_suite_id=test_suite_id,
revision=revision,
client=client,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    test_suite_id: str,
    revision: int,
    *,
    client: AuthenticatedClient,

) -> Response[Any | TestSuite]:
    """  Returns a specified revision of a test suite.

    Args:
        project_id (str):
        test_suite_id (str):
        revision (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | TestSuite]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
test_suite_id=test_suite_id,
revision=revision,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    test_suite_id: str,
    revision: int,
    *,
    client: AuthenticatedClient,

) -> Any | TestSuite | None:
    """  Returns a specified revision of a test suite.

    Args:
        project_id (str):
        test_suite_id (str):
        revision (int):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | TestSuite
     """


    return (await asyncio_detailed(
        project_id=project_id,
test_suite_id=test_suite_id,
revision=revision,
client=client,

    )).parsed
