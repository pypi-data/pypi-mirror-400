"""Storage filter module."""

import typing as t

import fw_utils

__all__ = ["StorageFilter"]


STORAGE_FILTERS: t.Dict[str, t.Type[fw_utils.ExpressionFilter]] = {
    "path": fw_utils.StringFilter,
    "size": fw_utils.SizeFilter,
    "created": fw_utils.TimeFilter,
    "modified": fw_utils.TimeFilter,
}


def validate_storage_field(field: str) -> str:
    """Return validated/canonic storage field name for the field shorthand."""
    return fw_utils.parse_field_name(field, allowed=list(STORAGE_FILTERS))


class StorageFilter(fw_utils.IncludeExcludeFilter):
    """Storage include/exclude filter with field validation and filter types."""

    def __init__(
        self,
        include: fw_utils.Filters = None,
        exclude: fw_utils.Filters = None,
    ) -> None:
        """Init filter with field name validators and filter types."""
        super().__init__(
            STORAGE_FILTERS,
            include=include,
            exclude=exclude,
            validate=validate_storage_field,
        )
