from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.list_experience_tags_order_by import ListExperienceTagsOrderBy
from ...models.list_experience_tags_output import ListExperienceTagsOutput
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    project_id: str,
    *,
    name: str | Unset = UNSET,
    order_by: ListExperienceTagsOrderBy | Unset = ListExperienceTagsOrderBy.ID,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["name"] = name

    json_order_by: str | Unset = UNSET
    if not isinstance(order_by, Unset):
        json_order_by = order_by.value

    params["orderBy"] = json_order_by

    params["pageSize"] = page_size

    params["pageToken"] = page_token


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/experienceTags".format(project_id=project_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ListExperienceTagsOutput | None:
    if response.status_code == 200:
        response_200 = ListExperienceTagsOutput.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ListExperienceTagsOutput]:
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
    name: str | Unset = UNSET,
    order_by: ListExperienceTagsOrderBy | Unset = ListExperienceTagsOrderBy.ID,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Response[Any | ListExperienceTagsOutput]:
    """  Returns a list of all experience tags.

    Args:
        project_id (str):
        name (str | Unset):
        order_by (ListExperienceTagsOrderBy | Unset):  Default: ListExperienceTagsOrderBy.ID.
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListExperienceTagsOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
name=name,
order_by=order_by,
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
    name: str | Unset = UNSET,
    order_by: ListExperienceTagsOrderBy | Unset = ListExperienceTagsOrderBy.ID,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Any | ListExperienceTagsOutput | None:
    """  Returns a list of all experience tags.

    Args:
        project_id (str):
        name (str | Unset):
        order_by (ListExperienceTagsOrderBy | Unset):  Default: ListExperienceTagsOrderBy.ID.
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListExperienceTagsOutput
     """


    return sync_detailed(
        project_id=project_id,
client=client,
name=name,
order_by=order_by,
page_size=page_size,
page_token=page_token,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    *,
    client: AuthenticatedClient,
    name: str | Unset = UNSET,
    order_by: ListExperienceTagsOrderBy | Unset = ListExperienceTagsOrderBy.ID,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Response[Any | ListExperienceTagsOutput]:
    """  Returns a list of all experience tags.

    Args:
        project_id (str):
        name (str | Unset):
        order_by (ListExperienceTagsOrderBy | Unset):  Default: ListExperienceTagsOrderBy.ID.
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListExperienceTagsOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
name=name,
order_by=order_by,
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
    name: str | Unset = UNSET,
    order_by: ListExperienceTagsOrderBy | Unset = ListExperienceTagsOrderBy.ID,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Any | ListExperienceTagsOutput | None:
    """  Returns a list of all experience tags.

    Args:
        project_id (str):
        name (str | Unset):
        order_by (ListExperienceTagsOrderBy | Unset):  Default: ListExperienceTagsOrderBy.ID.
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListExperienceTagsOutput
     """


    return (await asyncio_detailed(
        project_id=project_id,
client=client,
name=name,
order_by=order_by,
page_size=page_size,
page_token=page_token,

    )).parsed
