from http import HTTPStatus
from typing import Any, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.list_tags_for_job_metrics_output import ListTagsForJobMetricsOutput
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    project_id: str,
    batch_id: str,
    job_id: str,
    metric_id: list[str],
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
        "url": "/projects/{project_id}/batches/{batch_id}/jobs/{job_id}/metrics/{metric_id}/tags".format(project_id=project_id,batch_id=batch_id,job_id=job_id,metric_id=metric_id,),
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Any | ListTagsForJobMetricsOutput | None:
    if response.status_code == 200:
        response_200 = ListTagsForJobMetricsOutput.from_dict(response.json())



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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Any | ListTagsForJobMetricsOutput]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    project_id: str,
    batch_id: str,
    job_id: str,
    metric_id: list[str],
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Response[Any | ListTagsForJobMetricsOutput]:
    """  List the tags associated to the given job metric id(s)

    Args:
        project_id (str):
        batch_id (str):
        job_id (str):
        metric_id (list[str]):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListTagsForJobMetricsOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
job_id=job_id,
metric_id=metric_id,
page_size=page_size,
page_token=page_token,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    project_id: str,
    batch_id: str,
    job_id: str,
    metric_id: list[str],
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Any | ListTagsForJobMetricsOutput | None:
    """  List the tags associated to the given job metric id(s)

    Args:
        project_id (str):
        batch_id (str):
        job_id (str):
        metric_id (list[str]):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListTagsForJobMetricsOutput
     """


    return sync_detailed(
        project_id=project_id,
batch_id=batch_id,
job_id=job_id,
metric_id=metric_id,
client=client,
page_size=page_size,
page_token=page_token,

    ).parsed

async def asyncio_detailed(
    project_id: str,
    batch_id: str,
    job_id: str,
    metric_id: list[str],
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Response[Any | ListTagsForJobMetricsOutput]:
    """  List the tags associated to the given job metric id(s)

    Args:
        project_id (str):
        batch_id (str):
        job_id (str):
        metric_id (list[str]):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | ListTagsForJobMetricsOutput]
     """


    kwargs = _get_kwargs(
        project_id=project_id,
batch_id=batch_id,
job_id=job_id,
metric_id=metric_id,
page_size=page_size,
page_token=page_token,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    project_id: str,
    batch_id: str,
    job_id: str,
    metric_id: list[str],
    *,
    client: AuthenticatedClient,
    page_size: int | Unset = UNSET,
    page_token: str | Unset = UNSET,

) -> Any | ListTagsForJobMetricsOutput | None:
    """  List the tags associated to the given job metric id(s)

    Args:
        project_id (str):
        batch_id (str):
        job_id (str):
        metric_id (list[str]):
        page_size (int | Unset):
        page_token (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | ListTagsForJobMetricsOutput
     """


    return (await asyncio_detailed(
        project_id=project_id,
batch_id=batch_id,
job_id=job_id,
metric_id=metric_id,
client=client,
page_size=page_size,
page_token=page_token,

    )).parsed
