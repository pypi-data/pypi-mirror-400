from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.conflated_job_status import ConflatedJobStatus
from ...models.job_status import JobStatus
from ...models.list_jobs_output import ListJobsOutput
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    project_id: str,
    batch_id: str,
    *,
    status: JobStatus | Unset = UNSET,
    conflated_status: list[ConflatedJobStatus] | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    experience_tag_i_ds: list[str] | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    json_status: str | Unset = UNSET
    if not isinstance(status, Unset):
        json_status = status.value

    params["status"] = json_status

    json_conflated_status: list[str] | Unset = UNSET
    if not isinstance(conflated_status, Unset):
        json_conflated_status = []
        for conflated_status_item_data in conflated_status:
            conflated_status_item = conflated_status_item_data.value
            json_conflated_status.append(conflated_status_item)


    params["conflatedStatus"] = json_conflated_status

    params["name"] = name

    params["text"] = text

    json_experience_tag_i_ds: list[str] | Unset = UNSET
    if not isinstance(experience_tag_i_ds, Unset):
        json_experience_tag_i_ds = experience_tag_i_ds


    params["experienceTagIDs"] = json_experience_tag_i_ds

    params["pageSize"] = page_size

    params["pageToken"] = page_token

    params["orderBy"] = order_by


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/batches/{batch_id}/jobs".format(project_id=project_id,batch_id=batch_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ListJobsOutput | None:
    if response.status_code == 200:
        response_200 = ListJobsOutput.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ListJobsOutput]:
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
    status: JobStatus | Unset = UNSET,
    conflated_status: list[ConflatedJobStatus] | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    experience_tag_i_ds: list[str] | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Response[Any | ListJobsOutput]:
    """  List the jobs in the given batch.

    Args:
        project_id (str):
        batch_id (str):
        status (JobStatus | Unset):
        conflated_status (list[ConflatedJobStatus] | Unset):
        name (str | Unset):
        text (str | Unset):
        experience_tag_i_ds (list[str] | Unset):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListJobsOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
status=status,
conflated_status=conflated_status,
name=name,
text=text,
experience_tag_i_ds=experience_tag_i_ds,
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
    batch_id: str,
    *,
    client: AuthenticatedClient,
    status: JobStatus | Unset = UNSET,
    conflated_status: list[ConflatedJobStatus] | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    experience_tag_i_ds: list[str] | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Any | ListJobsOutput | None:
    """  List the jobs in the given batch.

    Args:
        project_id (str):
        batch_id (str):
        status (JobStatus | Unset):
        conflated_status (list[ConflatedJobStatus] | Unset):
        name (str | Unset):
        text (str | Unset):
        experience_tag_i_ds (list[str] | Unset):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListJobsOutput
     """


    return sync_detailed(
        project_id=project_id,
batch_id=batch_id,
client=client,
status=status,
conflated_status=conflated_status,
name=name,
text=text,
experience_tag_i_ds=experience_tag_i_ds,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    batch_id: str,
    *,
    client: AuthenticatedClient,
    status: JobStatus | Unset = UNSET,
    conflated_status: list[ConflatedJobStatus] | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    experience_tag_i_ds: list[str] | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Response[Any | ListJobsOutput]:
    """  List the jobs in the given batch.

    Args:
        project_id (str):
        batch_id (str):
        status (JobStatus | Unset):
        conflated_status (list[ConflatedJobStatus] | Unset):
        name (str | Unset):
        text (str | Unset):
        experience_tag_i_ds (list[str] | Unset):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListJobsOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
status=status,
conflated_status=conflated_status,
name=name,
text=text,
experience_tag_i_ds=experience_tag_i_ds,
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
    batch_id: str,
    *,
    client: AuthenticatedClient,
    status: JobStatus | Unset = UNSET,
    conflated_status: list[ConflatedJobStatus] | Unset = UNSET,
    name: str | Unset = UNSET,
    text: str | Unset = UNSET,
    experience_tag_i_ds: list[str] | Unset = UNSET,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Any | ListJobsOutput | None:
    """  List the jobs in the given batch.

    Args:
        project_id (str):
        batch_id (str):
        status (JobStatus | Unset):
        conflated_status (list[ConflatedJobStatus] | Unset):
        name (str | Unset):
        text (str | Unset):
        experience_tag_i_ds (list[str] | Unset):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListJobsOutput
     """


    return (await asyncio_detailed(
        project_id=project_id,
batch_id=batch_id,
client=client,
status=status,
conflated_status=conflated_status,
name=name,
text=text,
experience_tag_i_ds=experience_tag_i_ds,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )).parsed
