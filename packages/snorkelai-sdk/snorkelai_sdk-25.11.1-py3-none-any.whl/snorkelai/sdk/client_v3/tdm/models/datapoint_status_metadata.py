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

from ..models.data_point_status import DataPointStatus

T = TypeVar("T", bound="DatapointStatusMetadata")


@attrs.define
class DatapointStatusMetadata:
    """Model for viewing datapoint status in an annotation task.

    Attributes:
        created_at (datetime.datetime):
        status (DataPointStatus):
        updated_at (datetime.datetime):
        x_uid (str):
    """

    created_at: datetime.datetime
    status: DataPointStatus
    updated_at: datetime.datetime
    x_uid: str
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()
        status = self.status.value
        updated_at = self.updated_at.isoformat()
        x_uid = self.x_uid

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "status": status,
                "updated_at": updated_at,
                "x_uid": x_uid,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        status = DataPointStatus(d.pop("status"))

        updated_at = isoparse(d.pop("updated_at"))

        x_uid = d.pop("x_uid")

        obj = cls(
            created_at=created_at,
            status=status,
            updated_at=updated_at,
            x_uid=x_uid,
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
