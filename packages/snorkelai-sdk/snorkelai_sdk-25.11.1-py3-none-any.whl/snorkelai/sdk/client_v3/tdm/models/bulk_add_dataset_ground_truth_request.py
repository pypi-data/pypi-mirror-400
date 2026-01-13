from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
)

import attrs

if TYPE_CHECKING:
    # fmt: off
    from ..models.label_schema_labels import LabelSchemaLabels  # noqa: F401
    # fmt: on


T = TypeVar("T", bound="BulkAddDatasetGroundTruthRequest")


@attrs.define
class BulkAddDatasetGroundTruthRequest:
    """
    Attributes:
        ground_truth_entries (List['LabelSchemaLabels']):
    """

    ground_truth_entries: List["LabelSchemaLabels"]
    additional_properties: Dict[str, Any] = attrs.field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        # fmt: off
        from ..models.label_schema_labels import LabelSchemaLabels  # noqa: F401
        # fmt: on
        ground_truth_entries = []
        for ground_truth_entries_item_data in self.ground_truth_entries:
            ground_truth_entries_item = ground_truth_entries_item_data.to_dict()
            ground_truth_entries.append(ground_truth_entries_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ground_truth_entries": ground_truth_entries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        # fmt: off
        from ..models.label_schema_labels import LabelSchemaLabels  # noqa: F401
        # fmt: on
        d = src_dict.copy()
        ground_truth_entries = []
        _ground_truth_entries = d.pop("ground_truth_entries")
        for ground_truth_entries_item_data in _ground_truth_entries:
            ground_truth_entries_item = LabelSchemaLabels.from_dict(
                ground_truth_entries_item_data
            )

            ground_truth_entries.append(ground_truth_entries_item)

        obj = cls(
            ground_truth_entries=ground_truth_entries,
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
