from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.list_experiences_output import ListExperiencesOutput
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    project_id: str,
    system_id: str,
    *,
    archived: bool | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["archived"] = archived

    params["pageSize"] = page_size

    params["pageToken"] = page_token


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/systems/{system_id}/experiences".format(project_id=project_id,system_id=system_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ListExperiencesOutput | None:
    if response.status_code == 200:
        response_200 = ListExperiencesOutput.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ListExperiencesOutput]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    system_id: str,
    *,
    client: AuthenticatedClient,
    archived: bool | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Response[Any | ListExperiencesOutput]:
    """  Returns a list of all experiences applicable to the system.

    Args:
        project_id (str):
        system_id (str):
        archived (bool | Unset):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListExperiencesOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
system_id=system_id,
archived=archived,
page_size=page_size,
page_token=page_token,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    system_id: str,
    *,
    client: AuthenticatedClient,
    archived: bool | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Any | ListExperiencesOutput | None:
    """  Returns a list of all experiences applicable to the system.

    Args:
        project_id (str):
        system_id (str):
        archived (bool | Unset):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListExperiencesOutput
     """


    return sync_detailed(
        project_id=project_id,
system_id=system_id,
client=client,
archived=archived,
page_size=page_size,
page_token=page_token,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    system_id: str,
    *,
    client: AuthenticatedClient,
    archived: bool | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Response[Any | ListExperiencesOutput]:
    """  Returns a list of all experiences applicable to the system.

    Args:
        project_id (str):
        system_id (str):
        archived (bool | Unset):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListExperiencesOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
system_id=system_id,
archived=archived,
page_size=page_size,
page_token=page_token,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    system_id: str,
    *,
    client: AuthenticatedClient,
    archived: bool | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Any | ListExperiencesOutput | None:
    """  Returns a list of all experiences applicable to the system.

    Args:
        project_id (str):
        system_id (str):
        archived (bool | Unset):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListExperiencesOutput
     """


    return (await asyncio_detailed(
        project_id=project_id,
system_id=system_id,
client=client,
archived=archived,
page_size=page_size,
page_token=page_token,

    )).parsed
