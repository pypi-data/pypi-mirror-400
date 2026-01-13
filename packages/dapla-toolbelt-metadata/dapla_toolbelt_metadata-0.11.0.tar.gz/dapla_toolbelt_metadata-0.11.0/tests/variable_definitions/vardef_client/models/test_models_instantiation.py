from datetime import date

import pytest
from pydantic import BaseModel
from pydantic import ValidationError

from dapla_metadata.variable_definitions._generated.vardef_client.models.complete_view import (
    CompleteView,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.contact import (
    Contact,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.create_draft import (
    CreateDraft,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.create_patch import (
    CreatePatch,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.create_validity_period import (
    CreateValidityPeriod,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.language_string_type import (
    LanguageStringType,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.owner import (
    Owner,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.update_draft import (
    UpdateDraft,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.variable_status import (
    VariableStatus,
)

# NOTE: If we need to change these tests, that will normally mean it's a BREAKING CHANGE for users


@pytest.mark.parametrize(
    "model",
    [
        CreateDraft,
        CompleteView,
        Contact,
        Owner,
        CreateValidityPeriod,
    ],
)
def test_empty_instantiation_model_with_required_fields(model: type[BaseModel]):
    with pytest.raises(ValidationError):
        model()


@pytest.mark.parametrize(
    "model",
    [
        LanguageStringType,
        CreatePatch,
        UpdateDraft,
    ],
)
def test_empty_instantiation_model_without_required_fields(model: type[BaseModel]):
    model()


def test_instantiate_draft_all_fields(language_string_type, contact):
    CreateDraft(
        name=language_string_type,
        short_name="test",
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
    )


def test_instantiate_update_draft_all_fields(language_string_type, contact, owner):
    UpdateDraft(
        name=language_string_type,
        short_name="test",
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
        owner=owner,
    )


def test_instantiate_patch_all_fields(language_string_type, contact, owner):
    CreatePatch(
        name=language_string_type,
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        variable_status=VariableStatus.PUBLISHED_EXTERNAL,
        measurement_type="test",
        valid_until=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
        owner=owner,
    )


def test_instantiate_validity_period_all_fields(language_string_type, contact):
    CreateValidityPeriod(
        name=language_string_type,
        definition=language_string_type,
        classification_reference="91",
        unit_types=["a", "b"],
        subject_fields=["a", "b"],
        contains_special_categories_of_personal_data=True,
        measurement_type="test",
        valid_from=date(2024, 11, 1),
        external_reference_uri="http://www.example.com",
        comment=language_string_type,
        related_variable_definition_uris=["http://www.example.com"],
        contact=contact,
    )
