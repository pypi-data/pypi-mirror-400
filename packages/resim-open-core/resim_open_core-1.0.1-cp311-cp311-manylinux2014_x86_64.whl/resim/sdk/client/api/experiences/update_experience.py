from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.experience import Experience
from ...models.update_experience_input import UpdateExperienceInput
from typing import cast



def _get_kwargs(
    project_id: str,
    experience_id: str,
    *,
    body: UpdateExperienceInput,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/projects/{project_id}/experiences/{experience_id}".format(project_id=project_id,experience_id=experience_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | Experience | None:
    if response.status_code == 200:
        response_200 = Experience.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | Experience]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    experience_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExperienceInput,

) -> Response[Any | Experience]:
    """  Updates the experience. When updating environment variables, the entire array is replaced.

    Args:
        project_id (str):
        experience_id (str):
        body (UpdateExperienceInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Experience]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_id=experience_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    experience_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExperienceInput,

) -> Any | Experience | None:
    """  Updates the experience. When updating environment variables, the entire array is replaced.

    Args:
        project_id (str):
        experience_id (str):
        body (UpdateExperienceInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Experience
     """


    return sync_detailed(
        project_id=project_id,
experience_id=experience_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    experience_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExperienceInput,

) -> Response[Any | Experience]:
    """  Updates the experience. When updating environment variables, the entire array is replaced.

    Args:
        project_id (str):
        experience_id (str):
        body (UpdateExperienceInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | Experience]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_id=experience_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    experience_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExperienceInput,

) -> Any | Experience | None:
    """  Updates the experience. When updating environment variables, the entire array is replaced.

    Args:
        project_id (str):
        experience_id (str):
        body (UpdateExperienceInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | Experience
     """


    return (await asyncio_detailed(
        project_id=project_id,
experience_id=experience_id,
client=client,
body=body,

    )).parsed
