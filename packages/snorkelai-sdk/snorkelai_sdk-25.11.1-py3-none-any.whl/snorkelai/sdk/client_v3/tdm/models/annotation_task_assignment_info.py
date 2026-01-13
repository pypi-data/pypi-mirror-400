import datetime
from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs
from dateutil.parser import isoparse

T = TypeVar("T", bound="AnnotationTaskAssignmentInfo")


@attrs.define
class AnnotationTaskAssignmentInfo:
    """
    Attributes:
        annotation_task_uid (int):
        created_at (datetime.datetime):
        dataset_uid (int):
        last_viewed_at (datetime.datetime):
        latest_assigned_at (datetime.datetime):
        name (str):
        user_assigned_datapoints (int):
        user_remaining_datapoints (int):
        user_uid (int):
        workspace_uid (int):
    """

    annotation_task_uid: int
    created_at: datetime.datetime
    dataset_uid: int
    last_viewed_at: datetime.datetime
    latest_assigned_at: datetime.datetime
    name: str
    user_assigned_datapoints: int
    user_remaining_datapoints: int
    user_uid: int
    workspace_uid: int
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        annotation_task_uid = self.annotation_task_uid
        created_at = self.created_at.isoformat()
        dataset_uid = self.dataset_uid
        last_viewed_at = self.last_viewed_at.isoformat()
        latest_assigned_at = self.latest_assigned_at.isoformat()
        name = self.name
        user_assigned_datapoints = self.user_assigned_datapoints
        user_remaining_datapoints = self.user_remaining_datapoints
        user_uid = self.user_uid
        workspace_uid = self.workspace_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotation_task_uid": annotation_task_uid,
                "created_at": created_at,
                "dataset_uid": dataset_uid,
                "last_viewed_at": last_viewed_at,
                "latest_assigned_at": latest_assigned_at,
                "name": name,
                "user_assigned_datapoints": user_assigned_datapoints,
                "user_remaining_datapoints": user_remaining_datapoints,
                "user_uid": user_uid,
                "workspace_uid": workspace_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        annotation_task_uid = d.pop("annotation_task_uid")

        created_at = isoparse(d.pop("created_at"))

        dataset_uid = d.pop("dataset_uid")

        last_viewed_at = isoparse(d.pop("last_viewed_at"))

        latest_assigned_at = isoparse(d.pop("latest_assigned_at"))

        name = d.pop("name")

        user_assigned_datapoints = d.pop("user_assigned_datapoints")

        user_remaining_datapoints = d.pop("user_remaining_datapoints")

        user_uid = d.pop("user_uid")

        workspace_uid = d.pop("workspace_uid")

        obj = cls(
            annotation_task_uid=annotation_task_uid,
            created_at=created_at,
            dataset_uid=dataset_uid,
            last_viewed_at=last_viewed_at,
            latest_assigned_at=latest_assigned_at,
            name=name,
            user_assigned_datapoints=user_assigned_datapoints,
            user_remaining_datapoints=user_remaining_datapoints,
            user_uid=user_uid,
            workspace_uid=workspace_uid,
        )
        obj.additional_properties = d
        return obj

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
