# This file is generated from OpenAPI and not meant to be manually edited.
from typing import Any, Dict, List, overload

import requests
from typing_extensions import Literal

from snorkelai.sdk.client_v3.ctx import SnorkelSDKContext

from ..models import AnnotationTaskAssignmentInfo
from ..types import UNSET


@overload
def get_recent_annotation_tasks_assigned_recent_annotation_tasks_assigned_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_recent_annotation_tasks_assigned_recent_annotation_tasks_assigned_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> List["AnnotationTaskAssignmentInfo"]: ...


def get_recent_annotation_tasks_assigned_recent_annotation_tasks_assigned_get(
    *, workspace_uid: int, raw: bool = False
) -> List["AnnotationTaskAssignmentInfo"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/recent-annotation-tasks-assigned",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["AnnotationTaskAssignmentInfo"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['AnnotationTaskAssignmentInfo']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = AnnotationTaskAssignmentInfo.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import List, overload

import requests
from typing_extensions import Literal

from ..models import AnnotationTaskInfo


@overload
def get_recent_annotation_tasks_recent_annotation_tasks_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_recent_annotation_tasks_recent_annotation_tasks_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> List["AnnotationTaskInfo"]: ...


def get_recent_annotation_tasks_recent_annotation_tasks_get(
    *, workspace_uid: int, raw: bool = False
) -> List["AnnotationTaskInfo"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/recent-annotation-tasks",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["AnnotationTaskInfo"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['AnnotationTaskInfo']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = AnnotationTaskInfo.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import List, overload

import requests
from typing_extensions import Literal

from ..models import DatasetInfo


@overload
def get_recent_datasets_recent_datasets_get(
    *, workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_recent_datasets_recent_datasets_get(
    *, workspace_uid: int, raw: Literal[False] = False
) -> List["DatasetInfo"]: ...


def get_recent_datasets_recent_datasets_get(
    *, workspace_uid: int, raw: bool = False
) -> List["DatasetInfo"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    params: Dict[str, Any] = {}

    params["workspace_uid"] = workspace_uid

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "endpoint": "/recent-datasets",
        "params": params,
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetInfo"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetInfo']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetInfo.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import List, overload

import requests
from typing_extensions import Literal


@overload
def get_workspace_recent_annotation_tasks_workspace__workspace_uid__recent_annotation_tasks_get(
    workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_workspace_recent_annotation_tasks_workspace__workspace_uid__recent_annotation_tasks_get(
    workspace_uid: int, raw: Literal[False] = False
) -> List["AnnotationTaskInfo"]: ...


def get_workspace_recent_annotation_tasks_workspace__workspace_uid__recent_annotation_tasks_get(
    workspace_uid: int, raw: bool = False
) -> List["AnnotationTaskInfo"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workspace/{workspace_uid}/recent-annotation-tasks",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["AnnotationTaskInfo"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['AnnotationTaskInfo']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = AnnotationTaskInfo.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


from typing import List, overload

import requests
from typing_extensions import Literal


@overload
def get_workspace_recent_datasets_workspace__workspace_uid__recent_datasets_get(
    workspace_uid: int, raw: Literal[True]
) -> requests.Response: ...


@overload
def get_workspace_recent_datasets_workspace__workspace_uid__recent_datasets_get(
    workspace_uid: int, raw: Literal[False] = False
) -> List["DatasetInfo"]: ...


def get_workspace_recent_datasets_workspace__workspace_uid__recent_datasets_get(
    workspace_uid: int, raw: bool = False
) -> List["DatasetInfo"] | requests.Response:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/workspace/{workspace_uid}/recent-datasets",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.get(**_kwargs, raw=raw)

    # Handle raw response for GET requests
    if raw:
        return response

    # Parse and return the response
    def _parse_response(response: Any) -> List["DatasetInfo"]:
        """Parse response based on OpenAPI schema."""
        # Parse the success response
        # Parse as List['DatasetInfo']
        response_200 = []
        _response_200 = response
        for response_200_item_data in _response_200:
            response_200_item = DatasetInfo.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    return _parse_response(response)


def view_annotation_task_view_annotation_task__annotation_task_uid__post(
    annotation_task_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/view-annotation-task/{annotation_task_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)


from typing import Any


def view_dataset_view_dataset__dataset_uid__post(
    dataset_uid: int,
) -> Any:
    # Get the context
    ctx = SnorkelSDKContext.get_global()

    _kwargs: Dict[str, Any] = {
        "endpoint": f"/view-dataset/{dataset_uid}",
    }

    # Call the TDM endpoint
    response = ctx.tdm_client.post(**_kwargs)

    # Parse and return the response
    def _parse_response(response: Any) -> Any:
        """Parse response based on OpenAPI schema."""
        # Return type is None or Any
        return response

    return _parse_response(response)
