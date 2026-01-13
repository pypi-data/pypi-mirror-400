from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

from ..models.annotator_datapoint_status import AnnotatorDatapointStatus
from ..models.filter_transform_filter_types import FilterTransformFilterTypes

if TYPE_CHECKING:
    # fmt: off
    from ..models.option_model import OptionModel  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="AnnotatorStatusFilterStructureModel")


@attrs.define
class AnnotatorStatusFilterStructureModel:
    """A wrapper around data returned to the FE to render a Annotator Status Filter options.

    Attributes:
        annotator_users (List['OptionModel']):
        description (str):
        filter_type (FilterTransformFilterTypes):
        name (str):
        status_options (List[AnnotatorDatapointStatus]):
    """

    annotator_users: List["OptionModel"]
    description: str
    filter_type: FilterTransformFilterTypes
    name: str
    status_options: List[AnnotatorDatapointStatus]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.option_model import OptionModel  # noqa: F401
        # fmt: on
        annotator_users = []
        for annotator_users_item_data in self.annotator_users:
            annotator_users_item = annotator_users_item_data.to_dict()
            annotator_users.append(annotator_users_item)

        description = self.description
        filter_type = self.filter_type.value
        name = self.name
        status_options = []
        for status_options_item_data in self.status_options:
            status_options_item = status_options_item_data.value
            status_options.append(status_options_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "annotator_users": annotator_users,
                "description": description,
                "filter_type": filter_type,
                "name": name,
                "status_options": status_options,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.option_model import OptionModel  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        annotator_users = []
        _annotator_users = d.pop("annotator_users")
        for annotator_users_item_data in _annotator_users:
            annotator_users_item = OptionModel.from_dict(annotator_users_item_data)

            annotator_users.append(annotator_users_item)

        description = d.pop("description")

        filter_type = FilterTransformFilterTypes(d.pop("filter_type"))

        name = d.pop("name")

        status_options = []
        _status_options = d.pop("status_options")
        for status_options_item_data in _status_options:
            status_options_item = AnnotatorDatapointStatus(status_options_item_data)

            status_options.append(status_options_item)

        obj = cls(
            annotator_users=annotator_users,
            description=description,
            filter_type=filter_type,
            name=name,
            status_options=status_options,
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
