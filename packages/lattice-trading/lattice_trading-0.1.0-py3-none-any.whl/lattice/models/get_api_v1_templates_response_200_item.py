
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_templates_response_200_item_default_settings import (
        GetApiV1TemplatesResponse200ItemDefaultSettings,
    )
    from ..models.get_api_v1_templates_response_200_item_outcomes_item import (
        GetApiV1TemplatesResponse200ItemOutcomesItem,
    )
    from ..models.get_api_v1_templates_response_200_item_variables_item import (
        GetApiV1TemplatesResponse200ItemVariablesItem,
    )


T = TypeVar("T", bound="GetApiV1TemplatesResponse200Item")


@_attrs_define
class GetApiV1TemplatesResponse200Item:
    """
    Attributes:
        id (str):
        category (str):
        name (str):
        description (str):
        question_template (str):
        outcomes (List['GetApiV1TemplatesResponse200ItemOutcomesItem']):
        default_settings (GetApiV1TemplatesResponse200ItemDefaultSettings):
        variables (List['GetApiV1TemplatesResponse200ItemVariablesItem']):
        tags (List[str]):
        popularity (float):
    """

    id: str
    category: str
    name: str
    description: str
    question_template: str
    outcomes: list["GetApiV1TemplatesResponse200ItemOutcomesItem"]
    default_settings: "GetApiV1TemplatesResponse200ItemDefaultSettings"
    variables: list["GetApiV1TemplatesResponse200ItemVariablesItem"]
    tags: list[str]
    popularity: float

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        category = self.category

        name = self.name

        description = self.description

        question_template = self.question_template

        outcomes = []
        for outcomes_item_data in self.outcomes:
            outcomes_item = outcomes_item_data.to_dict()
            outcomes.append(outcomes_item)

        default_settings = self.default_settings.to_dict()

        variables = []
        for variables_item_data in self.variables:
            variables_item = variables_item_data.to_dict()
            variables.append(variables_item)

        tags = self.tags

        popularity = self.popularity

        field_dict: dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
                "category": category,
                "name": name,
                "description": description,
                "questionTemplate": question_template,
                "outcomes": outcomes,
                "defaultSettings": default_settings,
                "variables": variables,
                "tags": tags,
                "popularity": popularity,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.get_api_v1_templates_response_200_item_default_settings import (
            GetApiV1TemplatesResponse200ItemDefaultSettings,
        )
        from ..models.get_api_v1_templates_response_200_item_outcomes_item import (
            GetApiV1TemplatesResponse200ItemOutcomesItem,
        )
        from ..models.get_api_v1_templates_response_200_item_variables_item import (
            GetApiV1TemplatesResponse200ItemVariablesItem,
        )

        d = src_dict.copy()
        id = d.pop("id")

        category = d.pop("category")

        name = d.pop("name")

        description = d.pop("description")

        question_template = d.pop("questionTemplate")

        outcomes = []
        _outcomes = d.pop("outcomes")
        for outcomes_item_data in _outcomes:
            outcomes_item = GetApiV1TemplatesResponse200ItemOutcomesItem.from_dict(outcomes_item_data)

            outcomes.append(outcomes_item)

        default_settings = GetApiV1TemplatesResponse200ItemDefaultSettings.from_dict(d.pop("defaultSettings"))

        variables = []
        _variables = d.pop("variables")
        for variables_item_data in _variables:
            variables_item = GetApiV1TemplatesResponse200ItemVariablesItem.from_dict(variables_item_data)

            variables.append(variables_item)

        tags = cast(list[str], d.pop("tags"))

        popularity = d.pop("popularity")

        get_api_v1_templates_response_200_item = cls(
            id=id,
            category=category,
            name=name,
            description=description,
            question_template=question_template,
            outcomes=outcomes,
            default_settings=default_settings,
            variables=variables,
            tags=tags,
            popularity=popularity,
        )

        return get_api_v1_templates_response_200_item
