from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.test_suite_summary_output import TestSuiteSummaryOutput
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    project_id: str,
    *,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["pageSize"] = page_size

    params["pageToken"] = page_token


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/suites/summary".format(project_id=project_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> TestSuiteSummaryOutput | None:
    if response.status_code == 200:
        response_200 = TestSuiteSummaryOutput.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[TestSuiteSummaryOutput]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Response[TestSuiteSummaryOutput]:
    """  Returns an overview of test suites and high-level performance data. A test suite will only be
    returned if it has 1 or more reports on the main branch assocated to it.

    Args:
        project_id (str):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TestSuiteSummaryOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
page_size=page_size,
page_token=page_token,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> TestSuiteSummaryOutput | None:
    """  Returns an overview of test suites and high-level performance data. A test suite will only be
    returned if it has 1 or more reports on the main branch assocated to it.

    Args:
        project_id (str):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TestSuiteSummaryOutput
     """


    return sync_detailed(
        project_id=project_id,
client=client,
page_size=page_size,
page_token=page_token,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Response[TestSuiteSummaryOutput]:
    """  Returns an overview of test suites and high-level performance data. A test suite will only be
    returned if it has 1 or more reports on the main branch assocated to it.

    Args:
        project_id (str):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TestSuiteSummaryOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
page_size=page_size,
page_token=page_token,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> TestSuiteSummaryOutput | None:
    """  Returns an overview of test suites and high-level performance data. A test suite will only be
    returned if it has 1 or more reports on the main branch assocated to it.

    Args:
        project_id (str):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TestSuiteSummaryOutput
     """


    return (await asyncio_detailed(
        project_id=project_id,
client=client,
page_size=page_size,
page_token=page_token,

    )).parsed
