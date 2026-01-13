from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.list_builds_output import ListBuildsOutput
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    project_id: str,
    branch_id: list[str],
    *,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["pageSize"] = page_size

    params["pageToken"] = page_token

    params["orderBy"] = order_by


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/projects/{project_id}/branches/{branch_id}/builds".format(project_id=project_id,branch_id=branch_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ListBuildsOutput | None:
    if response.status_code == 200:
        response_200 = ListBuildsOutput.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ListBuildsOutput]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    branch_id: list[str],
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Response[Any | ListBuildsOutput]:
    """  Returns the list of builds for a branch.

    Args:
        project_id (str):
        branch_id (list[str]):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListBuildsOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
branch_id=branch_id,
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
    branch_id: list[str],
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Any | ListBuildsOutput | None:
    """  Returns the list of builds for a branch.

    Args:
        project_id (str):
        branch_id (list[str]):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListBuildsOutput
     """


    return sync_detailed(
        project_id=project_id,
branch_id=branch_id,
client=client,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    branch_id: list[str],
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Response[Any | ListBuildsOutput]:
    """  Returns the list of builds for a branch.

    Args:
        project_id (str):
        branch_id (list[str]):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListBuildsOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
branch_id=branch_id,
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
    branch_id: list[str],
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,
    order_by: str | Unset = UNSET,

) -> Any | ListBuildsOutput | None:
    """  Returns the list of builds for a branch.

    Args:
        project_id (str):
        branch_id (list[str]):
        page_size (int | Unset):
        page_token (str | Unset):
        order_by (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListBuildsOutput
     """


    return (await asyncio_detailed(
        project_id=project_id,
branch_id=branch_id,
client=client,
page_size=page_size,
page_token=page_token,
order_by=order_by,

    )).parsed
