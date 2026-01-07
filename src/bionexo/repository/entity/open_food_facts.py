from typing import Literal
from pydantic import BaseModel, Field, field_validator

SearchSortByType = Literal[
    # product_name sorts on name
    'product_name',
    # ecoscore_score, nova_score, nutriscore_score rank on the Eco-Score, Nova, or Nutri-Score
    'ecoscore_score', 'nova_score', 'nutriscore_score',
    # scans_n, unique_scans_n and popularity_key are about product popularity: number of scans on unique scans, rank of product
    'scans_n', 'unique_scans_n', 'popularity_key',
    # created_t, last_modified_t, are about creation and modification dates
    'created_t', 'last_modified_t',
    'nothing'
]

SearchTagsNamesType = Literal[
    'additives_tags',
    'allergens_tags',
    'brands_tags',
    'categories_tags',
    'countries_tags_en',
    'emb_codes_tags',
    'labels_tags',
    'manufacturing_places_tags',
    'nutrition_grades_tags',
    'origins_tags',
    'packaging_tags_de',
    'purchase_places_tags',
    'states_tags',
    'stores_tags',
    'traces_tags'
]

class SearchAdvanceParams(BaseModel):
    additives_tags=None,
    allergens_tags=None,
    brands_tags=None,
    categories_tags=None,
    countries_tags_en=None,
    emb_codes_tags=None,
    labels_tags=None,
    manufacturing_places_tags=None,
    nutrition_grades_tags=None,
    origins_tags=None,
    packaging_tags_de=None,
    purchase_places_tags=None,
    states_tags=None,
    stores_tags=None,
    traces_tags=None,
    map_tags_language_code: dict[SearchTagsNamesType, dict[str, str]] = Field(..., description="Mapping of tag names to language codes for localization")
    map_nutrient_value: dict[str, tuple[bool, Literal["100g", "serving"], Literal['lt', 'gt', 'eq'], float]] = Field(..., description="Mapping of nutrient names to their filter values")
    sort_by: SearchSortByType = Field(..., description="The allowed values used to sort/order the search results. Default popularity (for food) or last modification date")
    fields: list[str] = Field(default_factory=list, description="List of fields to be returned in the results")

    @property
    def tags_language_code(self) -> list[str]:
        return [f"{tag}_{lang}" for tag, lang in self.map_tags_language_code.items()]
    
    @property
    def nutrient_lt_value(self) -> list[str]:
        return {nutrient: conditions['lt'] for nutrient, conditions in self.map_nutrient_value.items() if 'lt' in conditions}

    @property    
    def nutrient_gt_value(self) -> dict[str, float]:
        return {nutrient: conditions['gt'] for nutrient, conditions in self.map_nutrient_value.items() if 'gt' in conditions}
    @property
    def nutrient_eq_value(self) -> dict[str, float]:
        return {nutrient: conditions['eq'] for nutrient, conditions in self.map_nutrient_value.items() if 'eq' in conditions}