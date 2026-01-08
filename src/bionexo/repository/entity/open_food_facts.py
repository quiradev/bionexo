from typing import Literal, Union, type
from pydantic import BaseModel, Field, field_validator

from bionexo.domain.entity.nutrients import (
    AlcoholNutrient, AminoAcidEssential, AminoAcidNonEssential, CarboHydrateNutrient, CarboHydrateType,
    LipidFattyAcidType, LipidsNutrient, MineralCompound, MineralMacro, MineralNutrient, MineralTrace, ProteinClass, ProteinNutrient,
    VitaminFatSoluble, VitaminNutrient, VitaminWaterSoluble, WaterNutrient
)

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

class ProductSearchAdvanceParams(BaseModel):
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
    map_nutrient_value: dict[str, tuple[bool, Literal["100g", "serving"], Literal['lt', 'gt', 'eq'], int | float]] = Field(..., description="Mapping of nutrient names to their filter values")
    sort_by: SearchSortByType = Field(..., description="The allowed values used to sort/order the search results. Default popularity (for food) or last modification date")
    fields: list[str] = Field(default_factory=list, description="List of fields to be returned in the results")


    def get_params_dict(self) -> dict:
        params = {}
        # Add tags with language codes
        for tag_key, lang_dict in self.map_tags_language_code.items():
            for lang_code in lang_dict.values():
                params.setdefault(tag_key, []).append(lang_code)
        # Add nutrient value filters
        for nutrient, (is_prepared, portion, operator, value) in self.map_nutrient_value.items():
            key = f"{nutrient}{'_prepared' if is_prepared else ''}_{portion}_{operator}_{value}"
            params[key] = '1'
        # Add sort_by if specified
        if self.sort_by:
            params['sort_by'] = self.sort_by
        # Add fields if specified
        if self.fields:
            params['fields'] = ','.join(self.fields)
        return params

    @property
    def tags_language_code(self) -> list[str]:
        return [f"{tag}_{lang}" for tag, lang in self.map_tags_language_code.items()]

    def _nutrient_value_key(self, nutrient: str, is_prepared: bool, portion: Literal["100g", "serving"], operator: Literal['lt', 'gt', 'eq'], value: int | float) -> str:
        return f"{nutrient}{'_prepared' if is_prepared else ''}_{portion}_{operator}_{value}"

    @property
    def nutrient_lt_value(self) -> list[str]:
        return [self._nutrient_value_key(nutrient, is_prepared, portion, 'lt', value) for nutrient, (is_prepared, portion, operator, value) in self.map_nutrient_value.items() if operator == 'lt']

    @property    
    def nutrient_gt_value(self) -> list[str]:
        return [self._nutrient_value_key(nutrient, is_prepared, portion, 'gt', value) for nutrient, (is_prepared, portion, operator, value) in self.map_nutrient_value.items() if operator == 'gt']

    @property
    def nutrient_eq_value(self) -> list[str]:
        return [self._nutrient_value_key(nutrient, is_prepared, portion, 'eq', value) for nutrient, (is_prepared, portion, operator, value) in self.map_nutrient_value.items() if operator == 'eq']



class NutrientMap(BaseModel):
    # Chlorophyl -> Magnesio, Hierro, Zinc, Cobre, Vitaminas A, C, E y B
    nutrients: dict[str, type] = {
        "proteins": ProteinNutrient,
        "fat": LipidsNutrient,
        "vitamins": VitaminNutrient,
        "minerals": MineralNutrient,
        # "water": WaterNutrient,
        "alcohol": AlcoholNutrient,
        "carbohydrates": CarboHydrateNutrient
    }
    lipid_fatty_acid_type_map: dict[str, LipidFattyAcidType] = {
        "fat.saturated-fat": LipidFattyAcidType.Saturated,
        "fat.unsaturated-fat": LipidFattyAcidType.Unsaturated,
        "fat.trans-fat": LipidFattyAcidType.TransFat,
        "fat.cholesterol": LipidFattyAcidType.Cholesterol
    }
    carbohydrate_type_map: dict[str, CarboHydrateType] = {
        "carbohydrates.sugars": CarboHydrateType.Monosaccharide,
        "carbohydrates.psicose": CarboHydrateType.Monosaccharide,
        "carbohydrates.starch": CarboHydrateType.Polysaccharide,
        "carbohydrates.polyols": CarboHydrateType.Polyol,
        "beta-glucan": CarboHydrateType.Polysaccharide,
        "inositol": CarboHydrateType.Polyol
    }
    protein_map: dict[str, ProteinClass] = {
        "proteins.casein": ProteinClass.Caseine,
        "proteins.whey_protein": ProteinClass.Whey_Protein
    }
    vitamin_map: dict[str, Union[VitaminFatSoluble, VitaminWaterSoluble]] = {
        "vitamin-a": VitaminFatSoluble.Vitamin_A_Retinol,
        "beta-carotene": VitaminFatSoluble.Vitamin_A_Retinol,
        "vitamin-d": VitaminFatSoluble.Vitamin_D_Cholecalciferol,
        "vitamin-e": VitaminFatSoluble.Vitamin_E_Tocopherol,
        "vitamin-k": VitaminFatSoluble.Vitamin_K_Phytonadione,
        "vitamin-c": VitaminWaterSoluble.Vitamin_C_Ascorbic_acid,
        "vitamin-b1": VitaminWaterSoluble.B1_Thiamine,
        "vitamin-b2": VitaminWaterSoluble.B2_Riboflavin,
        "vitamin-pp": VitaminWaterSoluble.B3_Niacin,
        "choline": VitaminWaterSoluble.B4_Choline,
        "vitamin-b6": VitaminWaterSoluble.B6_Pyridoxine,
        "vitamin-b9": VitaminWaterSoluble.B9_Folic_acid,
        "folates": VitaminWaterSoluble.B9_Folic_acid,
        "vitamin-b12": VitaminWaterSoluble.B12_Cobalamin,
        "biotin": VitaminWaterSoluble.B7_Biotin,
        "pantothenic-acid": VitaminWaterSoluble.B5_Pantothenic_acid,
        "phylloquinone": VitaminFatSoluble.Vitamin_K_Phytonadione,
    }
    mineral_map: dict[str, Union[MineralMacro, MineralTrace]] = {
        "salt": MineralCompound.Salt,
        "sodium": MineralMacro.Sodium,
        "silica": MineralTrace.Silica,
        "bicarbonate": MineralCompound.Bicarbonate,
        "potassium": MineralMacro.Potassium,
        "chloride": MineralMacro.Chloride,
        "calcium": MineralMacro.Calcium,
        "phosphorus": MineralMacro.Phosphorus,
        "iron": MineralTrace.Iron,
        "magnesium": MineralMacro.Magnesium,
        "zinc": MineralTrace.Zinc,
        "copper": MineralTrace.Copper,
        "manganese": MineralTrace.Manganese,
        "fluoride": MineralTrace.Fluoride,
        "selenium": MineralTrace.Selenium,
        "chromium": MineralTrace.Chromium,
        "molybdenum": MineralTrace.Molybdenum,
        "iodine": MineralTrace.Iodine,
        "caffeine": MineralCompound.Caffeine,
        "methylsulfonylmethane": MineralCompound.MSM,
        "sulphate": MineralCompound.Sulphate,
        "nitrate": MineralCompound.Nitrate,
    }