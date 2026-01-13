from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.workflow_suite_output import WorkflowSuiteOutput
from typing import cast



def _get_kwargs(
    project_id: str,
    workflow_id: str,
    test_suite_id: str,

) -> dict[str, Any]:
    

    

    

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/workflows/{workflow_id}/test_suites/{test_suite_id}".format(project_id=project_id,workflow_id=workflow_id,test_suite_id=test_suite_id,),
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | WorkflowSuiteOutput | None:
    if response.status_code == 200:
        response_200 = WorkflowSuiteOutput.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | WorkflowSuiteOutput]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    workflow_id: str,
    test_suite_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Any | WorkflowSuiteOutput]:
    """  Gets a specific workflow test suite.

    Args:
        project_id (str):
        workflow_id (str):
        test_suite_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WorkflowSuiteOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
workflow_id=workflow_id,
test_suite_id=test_suite_id,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    workflow_id: str,
    test_suite_id: str,
    *,
    client: AuthenticatedClient,

) -> Any | WorkflowSuiteOutput | None:
    """  Gets a specific workflow test suite.

    Args:
        project_id (str):
        workflow_id (str):
        test_suite_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WorkflowSuiteOutput
     """


    return sync_detailed(
        project_id=project_id,
workflow_id=workflow_id,
test_suite_id=test_suite_id,
client=client,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    workflow_id: str,
    test_suite_id: str,
    *,
    client: AuthenticatedClient,

) -> Response[Any | WorkflowSuiteOutput]:
    """  Gets a specific workflow test suite.

    Args:
        project_id (str):
        workflow_id (str):
        test_suite_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | WorkflowSuiteOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
workflow_id=workflow_id,
test_suite_id=test_suite_id,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    workflow_id: str,
    test_suite_id: str,
    *,
    client: AuthenticatedClient,

) -> Any | WorkflowSuiteOutput | None:
    """  Gets a specific workflow test suite.

    Args:
        project_id (str):
        workflow_id (str):
        test_suite_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | WorkflowSuiteOutput
     """


    return (await asyncio_detailed(
        project_id=project_id,
workflow_id=workflow_id,
test_suite_id=test_suite_id,
client=client,

    )).parsed
