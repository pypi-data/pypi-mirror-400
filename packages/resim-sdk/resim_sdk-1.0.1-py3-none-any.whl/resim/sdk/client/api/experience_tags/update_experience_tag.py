from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.experience_tag import ExperienceTag
from ...models.update_experience_tag_input import UpdateExperienceTagInput
from typing import cast



def _get_kwargs(
    project_id: str,
    experience_tag_id: str,
    *,
    body: UpdateExperienceTagInput,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/projects/{project_id}/experienceTags/{experience_tag_id}".format(project_id=project_id,experience_tag_id=experience_tag_id,),
    }

    _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ExperienceTag | None:
    if response.status_code == 200:
        response_200 = ExperienceTag.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ExperienceTag]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    experience_tag_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExperienceTagInput,

) -> Response[Any | ExperienceTag]:
    """  Updates the experience tag.  Experience membership cannot be changed with this method.

    Args:
        project_id (str):
        experience_tag_id (str):
        body (UpdateExperienceTagInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ExperienceTag]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_tag_id=experience_tag_id,
body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    experience_tag_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExperienceTagInput,

) -> Any | ExperienceTag | None:
    """  Updates the experience tag.  Experience membership cannot be changed with this method.

    Args:
        project_id (str):
        experience_tag_id (str):
        body (UpdateExperienceTagInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ExperienceTag
     """


    return sync_detailed(
        project_id=project_id,
experience_tag_id=experience_tag_id,
client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    experience_tag_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExperienceTagInput,

) -> Response[Any | ExperienceTag]:
    """  Updates the experience tag.  Experience membership cannot be changed with this method.

    Args:
        project_id (str):
        experience_tag_id (str):
        body (UpdateExperienceTagInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ExperienceTag]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
experience_tag_id=experience_tag_id,
body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    experience_tag_id: str,
    *,
    client: AuthenticatedClient,
    body: UpdateExperienceTagInput,

) -> Any | ExperienceTag | None:
    """  Updates the experience tag.  Experience membership cannot be changed with this method.

    Args:
        project_id (str):
        experience_tag_id (str):
        body (UpdateExperienceTagInput):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ExperienceTag
     """


    return (await asyncio_detailed(
        project_id=project_id,
experience_tag_id=experience_tag_id,
client=client,
body=body,

    )).parsed
