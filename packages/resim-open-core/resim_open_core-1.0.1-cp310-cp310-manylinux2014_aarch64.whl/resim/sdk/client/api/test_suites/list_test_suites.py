from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.list_test_suite_output import ListTestSuiteOutput
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    project_id: str,
    *,
    experience_i_ds: list[str] | Unset = UNSET,
    system_id: str | Unset = UNSET,
    archived: bool | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    json_experience_i_ds: list[str] | Unset = UNSET
    if not isinstance(experience_i_ds, Unset):
        json_experience_i_ds = experience_i_ds


    params["experienceIDs"] = json_experience_i_ds

    params["systemID"] = system_id

    params["archived"] = archived

    params["name"] = name

    params["text"] = text

    params["pageSize"] = page_size

    params["pageToken"] = page_token

    params["orderBy"] = order_by


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/suites".format(project_id=project_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ListTestSuiteOutput | None:
    if response.status_code == 200:
        response_200 = ListTestSuiteOutput.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if response.status_code == 401:
        response_401 = cast(Any, None)
        return response_401

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ListTestSuiteOutput]:
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
    experience_i_ds: list[str] | Unset = UNSET,
    system_id: str | Unset = UNSET,
    archived: bool | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Response[Any | ListTestSuiteOutput]:
    """  Returns the list of test suites at their latest revision

    Args:
        project_id (str):
        experience_i_ds (list[str] | Unset):
        system_id (str | Unset):
        archived (bool | Unset):
        name (str | Unset):
        text (str | Unset):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListTestSuiteOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_i_ds=experience_i_ds,
system_id=system_id,
archived=archived,
name=name,
text=text,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    *,
    client: AuthenticatedClient,
    experience_i_ds: list[str] | Unset = UNSET,
    system_id: str | Unset = UNSET,
    archived: bool | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Any | ListTestSuiteOutput | None:
    """  Returns the list of test suites at their latest revision

    Args:
        project_id (str):
        experience_i_ds (list[str] | Unset):
        system_id (str | Unset):
        archived (bool | Unset):
        name (str | Unset):
        text (str | Unset):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListTestSuiteOutput
     """


    return sync_detailed(
        project_id=project_id,
client=client,
experience_i_ds=experience_i_ds,
system_id=system_id,
archived=archived,
name=name,
text=text,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    experience_i_ds: list[str] | Unset = UNSET,
    system_id: str | Unset = UNSET,
    archived: bool | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Response[Any | ListTestSuiteOutput]:
    """  Returns the list of test suites at their latest revision

    Args:
        project_id (str):
        experience_i_ds (list[str] | Unset):
        system_id (str | Unset):
        archived (bool | Unset):
        name (str | Unset):
        text (str | Unset):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListTestSuiteOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_i_ds=experience_i_ds,
system_id=system_id,
archived=archived,
name=name,
text=text,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    *,
    client: AuthenticatedClient,
    experience_i_ds: list[str] | Unset = UNSET,
    system_id: str | Unset = UNSET,
    archived: bool | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Any | ListTestSuiteOutput | None:
    """  Returns the list of test suites at their latest revision

    Args:
        project_id (str):
        experience_i_ds (list[str] | Unset):
        system_id (str | Unset):
        archived (bool | Unset):
        name (str | Unset):
        text (str | Unset):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListTestSuiteOutput
     """


    return (await asyncio_detailed(
        project_id=project_id,
client=client,
experience_i_ds=experience_i_ds,
system_id=system_id,
archived=archived,
name=name,
text=text,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )).parsed
