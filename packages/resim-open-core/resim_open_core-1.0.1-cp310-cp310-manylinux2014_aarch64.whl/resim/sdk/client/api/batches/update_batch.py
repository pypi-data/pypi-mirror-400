from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.batch import Batch
from ...models.update_batch_input import UpdateBatchInput
from typing import cast



def _get_kwargs(
    project_id: str,
    batch_id: str,
    *,
    body: UpdateBatchInput,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/projects/{project_id}/batches/{batch_id}".format(project_id=project_id,batch_id=batch_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Batch | None:
    if response.status_code == 200:
        response_200 = Batch.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Batch]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    batch_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBatchInput,

) -> Response[Any | Batch]:
    """  Updates the batch.

    Args:
        project_id (str):
        batch_id (str):
        body (UpdateBatchInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Batch]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    batch_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBatchInput,

) -> Any | Batch | None:
    """  Updates the batch.

    Args:
        project_id (str):
        batch_id (str):
        body (UpdateBatchInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Batch
     """


    return sync_detailed(
        project_id=project_id,
batch_id=batch_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    batch_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBatchInput,

) -> Response[Any | Batch]:
    """  Updates the batch.

    Args:
        project_id (str):
        batch_id (str):
        body (UpdateBatchInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Batch]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    batch_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateBatchInput,

) -> Any | Batch | None:
    """  Updates the batch.

    Args:
        project_id (str):
        batch_id (str):
        body (UpdateBatchInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Batch
     """


    return (await asyncio_detailed(
        project_id=project_id,
batch_id=batch_id,
client=client,
body=body,

    )).parsed
