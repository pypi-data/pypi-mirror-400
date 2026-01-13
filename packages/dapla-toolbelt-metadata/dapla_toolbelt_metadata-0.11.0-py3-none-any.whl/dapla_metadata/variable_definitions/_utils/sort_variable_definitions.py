"""Utilities for sorting variable definitions."""

from enum import Enum

from dapla_metadata.variable_definitions._generated.vardef_client.models.language_string_type import (
    LanguageStringType,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.owner import (
    Owner,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.supported_languages import (
    SupportedLanguages,
)
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition


class SortOption(Enum):
    NAME_ASC = "name-ascending"
    NAME_DESC = "name-descending"
    SHORT_NAME_ASC = "short-name-ascending"
    SHORT_NAME_DESC = "short-name-descending"
    OWNER_ASC = "owner-ascending"
    OWNER_DESC = "owner-descending"


# Map enum sort options to field name and set order
MAP_SORT_OPTIONS = {
    SortOption.NAME_ASC: ("name", False),
    SortOption.NAME_DESC: ("name", True),
    SortOption.SHORT_NAME_ASC: ("short_name", False),
    SortOption.SHORT_NAME_DESC: ("short_name", True),
    SortOption.OWNER_ASC: ("owner", False),
    SortOption.OWNER_DESC: ("owner", True),
}


def make_sort_key(field_name: str):
    """Create a robust sort key function for a given object attribute."""

    def key_func(obj: VariableDefinition):
        variable_definition = getattr(obj, field_name, None)
        if variable_definition is None:
            result: str = ""
        if isinstance(variable_definition, LanguageStringType):
            val = getattr(variable_definition, SupportedLanguages.NB)
            result = val.casefold() if isinstance(val, str) else ""

        if isinstance(variable_definition, Owner):
            result = getattr(variable_definition, "team", "")

        if isinstance(variable_definition, str):
            result = variable_definition.casefold()

        return result

    return key_func
