
from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from ..models.get_api_v1_templates_id_response_200_default_settings import (
        GetApiV1TemplatesIdResponse200DefaultSettings,
    )
    from ..models.get_api_v1_templates_id_response_200_outcomes_item import GetApiV1TemplatesIdResponse200OutcomesItem
    from ..models.get_api_v1_templates_id_response_200_variables_item import GetApiV1TemplatesIdResponse200VariablesItem


T = TypeVar("T", bound="GetApiV1TemplatesIdResponse200")


@_attrs_define
class GetApiV1TemplatesIdResponse200:
    """
    Attributes:
        id (str):
        category (str):
        name (str):
        description (str):
        question_template (str):
        outcomes (List['GetApiV1TemplatesIdResponse200OutcomesItem']):
        default_settings (GetApiV1TemplatesIdResponse200DefaultSettings):
        variables (List['GetApiV1TemplatesIdResponse200VariablesItem']):
        tags (List[str]):
        popularity (float):
    """

    id: str
    category: str
    name: str
    description: str
    question_template: str
    outcomes: list["GetApiV1TemplatesIdResponse200OutcomesItem"]
    default_settings: "GetApiV1TemplatesIdResponse200DefaultSettings"
    variables: list["GetApiV1TemplatesIdResponse200VariablesItem"]
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
        from ..models.get_api_v1_templates_id_response_200_default_settings import (
            GetApiV1TemplatesIdResponse200DefaultSettings,
        )
        from ..models.get_api_v1_templates_id_response_200_outcomes_item import (
            GetApiV1TemplatesIdResponse200OutcomesItem,
        )
        from ..models.get_api_v1_templates_id_response_200_variables_item import (
            GetApiV1TemplatesIdResponse200VariablesItem,
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
            outcomes_item = GetApiV1TemplatesIdResponse200OutcomesItem.from_dict(outcomes_item_data)

            outcomes.append(outcomes_item)

        default_settings = GetApiV1TemplatesIdResponse200DefaultSettings.from_dict(d.pop("defaultSettings"))

        variables = []
        _variables = d.pop("variables")
        for variables_item_data in _variables:
            variables_item = GetApiV1TemplatesIdResponse200VariablesItem.from_dict(variables_item_data)

            variables.append(variables_item)

        tags = cast(list[str], d.pop("tags"))

        popularity = d.pop("popularity")

        get_api_v1_templates_id_response_200 = cls(
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

        return get_api_v1_templates_id_response_200
