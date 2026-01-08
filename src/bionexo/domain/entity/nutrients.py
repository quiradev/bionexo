from ctypes import Union
from enum import Enum
from pydantic import BaseModel, Field

class AminoAcidEssential(Enum):
    Isoleucine = 'isoleucine'
    Leucine = 'leucine'
    Lysine = 'lysine'
    Methionine = 'methionine'
    Phenylalanine = 'phenylalanine'
    Threonine = 'threonine'
    Tryptophan = 'tryptophan'
    Valine = 'valine'
    Histidine_Kids = 'histidine_kids'

class AminoAcidNonEssential(Enum):
    Alanine = 'alanine'
    Arginine = 'arginine'
    Aspartic_acid = 'aspartic_acid'
    Cysteine = 'cysteine'
    Glutamic_acid = 'glutamic_acid'
    Glycine = 'glycine'
    Proline = 'proline'
    Serine = 'serine'
    Tyrosine = 'tyrosine'
    Histidine_Adults = 'histidine_adults'
    Taurine = 'taurine'
    Carnitine = 'carnitine'


class ProteinSource(Enum):
    Animal = 'animal'
    Plant = 'plant'


class ProteinClass(Enum):
    Caseine = 'caseine'
    Whey_Protein = 'whey_protein'
    Soy_Protein = 'soy_protein'
    Albumin = 'albumin'
    Gluten = 'gluten'
    Meet_Protein = 'meat_protein'


# https://consorciolechero.cl/libro-capitulo/LNS_SI_C2_Prote%C3%ADna.pdf
class ProteinAminoacidProfile(Enum):
    Caseine = {
        AminoAcidNonEssential.Aspartic_acid: 7.1,
        AminoAcidEssential.Threonine: 4.9,
        AminoAcidNonEssential.Serine: 6.3,
        AminoAcidNonEssential.Glutamic_acid: 22.4,
        AminoAcidNonEssential.Proline: 11.3,
        AminoAcidNonEssential.Glycine: 2.7,
        AminoAcidNonEssential.Alanine: 3.0,
        AminoAcidNonEssential.Cysteine: 0.34,
        AminoAcidEssential.Methionine: 2.8,
        AminoAcidEssential.Valine: 7.2,
        AminoAcidEssential.Isoleucine: 6.1,
        AminoAcidEssential.Leucine: 9.2,
        AminoAcidNonEssential.Tyrosine: 6.3,
        AminoAcidEssential.Phenylalanine: 5.0,
        AminoAcidEssential.Tryptophan: 1.7,
        AminoAcidEssential.Lysine: 8.2,
        AminoAcidNonEssential.Histidine_Adults: 3.1,
        AminoAcidNonEssential.Arginine: 4.1
    }
    Whey_Protein = {
        AminoAcidNonEssential.Aspartic_acid: 10.5,
        AminoAcidEssential.Threonine: 7.0,
        AminoAcidNonEssential.Serine: 4.8,
        AminoAcidNonEssential.Glutamic_acid: 17.6,
        AminoAcidNonEssential.Proline: 5.9,
        AminoAcidNonEssential.Glycine: 1.8,
        AminoAcidNonEssential.Alanine: 4.9,
        AminoAcidNonEssential.Cysteine: 2.3,
        AminoAcidEssential.Methionine: 1.7,
        AminoAcidEssential.Valine: 5.7,
        AminoAcidEssential.Isoleucine: 6.4,
        AminoAcidEssential.Leucine: 10.3,
        AminoAcidNonEssential.Tyrosine: 2.9,
        AminoAcidEssential.Phenylalanine: 3.1,
        AminoAcidEssential.Tryptophan: 2.4,
        AminoAcidEssential.Lysine: 8.7,
        AminoAcidNonEssential.Histidine_Adults: 1.7,
        AminoAcidNonEssential.Arginine: 2.3
    }

class CarboHydrateType(Enum):
    Polysaccharide = 'polysaccharide'  # Almidon por ejemplo
    Monosaccharide = 'monosaccharide'  # Galactosa, Glucosa, Fructosa
    Polyol = 'polyol'  # Alcoholes de azucar como sorbitol, manitol

class LipidType(Enum):
    Triglycerides = 'triglycerides'
    FattyAcids = 'fatty_acids'  # Acidos grasos

class LipidFattyAcidType(Enum):
    Saturated = 'saturated'
    Unsaturated = 'unsaturated'
    TransFat = 'trans_fat'
    Cholesterol = 'cholesterol'

class VitaminType(Enum):
    FatSoluble = 'fat_soluble'  # A, D, E, K
    WaterSoluble = 'water_soluble'  # B, C

class VitaminWaterSoluble(Enum):
    B1_Thiamine = 'B1_thiamine'
    B2_Riboflavin = 'B2_riboflavin'
    B3_Niacin = 'B3_niacin'
    B4_Choline = 'B4_choline'
    B5_Pantothenic_acid = 'B5_pantothenic_acid'
    B6_Pyridoxine = 'B6_pyridoxine'
    B7_Biotin = 'B7_biotin'
    B9_Folic_acid = 'B9_folic_acid'
    B12_Cobalamin = 'B12_cobalamin'
    Vitamin_C_Ascorbic_acid = 'vitamin_c_ascorbic_acid'

class VitaminFatSoluble(Enum):
    Vitamin_A_Retinol = 'vitamin_a_retinol'
    Vitamin_D_Cholecalciferol = 'vitamin_d_cholecalciferol'
    Vitamin_E_Tocopherol = 'vitamin_e_tocopherol'
    Vitamin_K_Phytonadione = 'vitamin_k_phytonadione'


class MineralType(Enum):
    MacroMineral = 'macro_mineral'  # e.g., Calcium, Magnesium
    TraceMineral = 'trace_mineral'  # e.g., Iron, Zinc
    CompoundMineral = 'compound_mineral'  # e.g., Bicarbonate, Caffeine

class MineralMacro(Enum):
    Calcium = 'calcium'
    Magnesium = 'magnesium'
    Phosphorus = 'phosphorus'
    Potassium = 'potassium'
    Sodium = 'sodium'
    Sulfur = 'sulfur'
    Chloride = 'chloride'
    

class MineralTrace(Enum):
    Iron = 'iron'
    Zinc = 'zinc'
    Copper = 'copper'
    Manganese = 'manganese'
    Selenium = 'selenium'
    Iodine = 'iodine'
    Fluoride = 'fluoride'
    Silica = 'silica'
    Chromium = 'chromium'
    Molybdenum = 'molybdenum'

class MineralCompound(Enum):
    Salt = 'salt'
    Bicarbonate = 'bicarbonate'
    Caffeine = 'caffeine'
    MSM = 'methylsulfonylmethane'
    Sulphate = 'sulphate'
    Nitrate = 'nitrate'

class MineralCompoundParts(Enum):
    Salt = [MineralMacro.Sodium, MineralMacro.Chloride]
    Bicarbonate = [MineralMacro.Sodium]
    Caffeine = [
        MineralMacro.Potassium, MineralMacro.Phosphorus, MineralMacro.Magnesium,
        MineralTrace.Zinc, MineralTrace.Selenium, MineralTrace.Iodine
    ]
    MSM = [MineralMacro.Sulfur]
    Sulphate = ["SO4--"]  # Ion sulfato
    Nitrate = ["NO3-"]  # Ion nitrato

# Macrominerales (Macroelementos):
# - Calcio: Huesos, dientes, coagulación, función muscular.
# - Fósforo: Huesos, dientes, parte de todas las células.
# - Magnesio: Huesos, producción de proteínas, contracción muscular, sistema inmune.
# - Sodio: Equilibrio de líquidos, transmisión nerviosa.
# - Potasio: Equilibrio de líquidos, función nerviosa y muscular.
# - Cloro: Equilibrio de líquidos, parte del ácido estomacal.
# - Azufre: Componente de aminoácidos, hormonas y vitaminas. 
# Oligoelementos (Minerales Traza):
# - Hierro: Transporte de oxígeno (hemoglobina).
# - Zinc: Función inmune, cicatrización, síntesis de proteínas.
# - Yodo: Función tiroidea.
# - Cobre: Formación de glóbulos rojos, función nerviosa.
# - Selenio: Antioxidante, función tiroidea.
# - Manganeso: Metabolismo, formación ósea.
# - Flúor: Salud dental y ósea.
# - Cromo: Metabolismo de la glucosa.
# - Molibdeno: Coenzima en varias reacciones enzimáticas. 

class Nutrient(BaseModel):
    id: str
    name: str
    unit: str
    amount_per_100g: float = None
    amount_per_serving: float = None


class AminoAcidNutrient(Nutrient):
    is_essential: bool


class ProteinNutrient(Nutrient):
    amino_acid_profile: list[tuple[AminoAcidEssential | AminoAcidNonEssential, float]]  # e.g., [('leucine', 1.5), ('lysine', 2.0)]

# Digestion de las proteinas se produce con las enzimas:
# - Estomago (pepsina)
# - Pancreas (tripsina, quimotripsina)
# - Duodeno e intestino delgado (carboxipeptidasas, aminopeptidasas, dipeptidasas, tripsina, elastasa)
# - Intestino delgado (peptidasas)
#
# - Pepsina: proteinas -> polipeptidos
# - Tripsina y quimotripsina: polipeptidos -> peptidos mas cortos
# - Carboxipeptidasas, aminopeptidasas, dipeptidasas: peptidos -> aminoacidos libres
# - Peptidasas: peptidos -> aminoacidos libres

class CarboHydrateNutrient(Nutrient):
    type: CarboHydrateType

# Digestion de los carboHidratos se produce con las enzimas:
# - Saliva (amilasa salival), continua parte en el estomago pero se desace
# - Pancreas (amilasa pancreatica)
# - Intestino delgado (maltasa, lactasa, sacarasa) de disacaridos a monosacaridos
#  - Maltasa: maltosa | maltriosa -> glucosa + glucosa | glucosa + glucosa + glucosa
#  - Lactasa: lactosa -> glucosa + galactosa
#  - Sacarasa: sacarosa -> glucosa + fructosa

class LipidsNutrient(Nutrient):
    type: LipidType
    fatty_acid_type: LipidFattyAcidType = None

# Digestion de los lipidos se produce con:
# - Boca (lipasa lingual) - low
# - Estomago (lipasa gastrica) - medium
# - Pancreas (lipasa pancreatica) - high

# Funcion principal de los lipidos es:
# - Fuente de energia
# - Componente estructural de membranas celulares
# - Precursores de moleculas biologicamente activas (hormonas, vitaminas liposolubles)
# - Aislante termico y proteccion mecanica de organos vitales
# - Transporte y absorcion de vitaminas liposolubles (A, D, E, K)

class VitaminNutrient(Nutrient):
    type: VitaminType
    vitamin_class: Union[VitaminFatSoluble, VitaminWaterSoluble]

class MineralNutrient(Nutrient):
    type: MineralType
    mineral_class: Union[MineralMacro, MineralTrace]

MacroNutrientType = Union[ProteinNutrient, CarboHydrateNutrient, LipidsNutrient]
MicroNutrientType = Union[VitaminNutrient, MineralNutrient]


class WaterNutrient(Nutrient):
    pass

class AlcoholNutrient(Nutrient):
    pass

class Aliment(BaseModel):
    id: str
    name: str
    macro_nutrients: list[MacroNutrientType] = Field(default_factory=list)
    micro_nutrients: list[MicroNutrientType] = Field(default_factory=list)
    water: WaterNutrient = None
    alcohol: AlcoholNutrient = None

# DEFECTO
# El cuerpo humano usa como fuente de energia en orden:
# 1. Carbohidratos (glucosa)
# 2. Lipidos (acidos grasos)
#  - Glicerol - via gluconeogenesis puede convertirse en glucosa
#  - Acidos grasos - via beta-oxidacion en cuerpos cetonicos
# 3. Proteinas (aminoacidos) - en casos extremos

# Dias sin ingesta:
# Dia 1-2: glucogeno hepatico y muscular
# Dia 3-5: lipolisis y beta-oxidacion de acidos grasos
# Dia 5+: proteolisis de musculo esquelético para obtener aminoacidos

# Los efectos, son falta de apetito, el metabolismo, cae el ritmo cardiaco, la presion arterial baja, la temperatura corporal disminuye, la funcion cognitiva se ve afectada, debilidad muscular y fatiga extrema.

# EXCESO
# El exceso de nutrientes puede llevar a:
# - Obesidad
# - Enfermedades cardiovasculares
# - Diabetes tipo 2
# - Problemas renales
# - Deficiencias de vitaminas y minerales
# - Cancer
# - Hipertension (Exceso de sodio o sal)


# Funciones de los nutrientes en el cuerpo humano:
# - Proteinas: construccion y reparacion de tejidos, enzimas, hormonas, transporte de moleculas
# - Carbohidratos: principal fuente de energia, reserva energetica (glucogeno)
# - Lipidos: reserva energetica, aislamiento termico, proteccion de organos, transporte y absorcion de vitaminas liposolubles
# - Vitaminas: regulacion de procesos metabolicos, funcion inmunologica, salud de piel y vision
# - Minerales: formacion de huesos y dientes, equilibrio de fluidos, funcion nerviosa y muscular

# Problemas nutricionales asociados a deficiencias o excesos de nutrientes:
# - Deficiencia de proteinas: retraso en el crecimiento, debilidad muscular, sistema inmunologico debilitado
# - Deficiencia de carbohidratos: fatiga, debilidad, problemas cognitivos
# - Deficiencia de lipidos: problemas de piel, deficiencias de vitaminas liposolubles, alteraciones hormonales
# - Deficiencia de vitaminas: escorbuto (vitamina C), raquitismo (vitamina D), anemia (vitamina B12, hierro)
# - Deficiencia de minerales: osteoporosis (calcio), anemia (hierro), hipotiroidismo (yodo)
# - Exceso de proteinas: problemas renales, deshidratacion, perdida de calcio
# - Exceso de carbohidratos: obesidad, diabetes tipo 2, enfermedades cardiovasculares
# - Exceso de lipidos: obesidad, enfermedades cardiovasculares, resistencia a la insulina
# - Exceso de vitaminas: toxicidad por vitamina A, D, E, K (liposolubles)
# - Exceso de minerales: toxicidad por hierro, zinc, cobre
# La ingesta diaria recomendada (IDR) varía según la edad, género, estado fisiológico (embarazo, lactancia), nivel de actividad física y condiciones de salud específicas.
# Es importante mantener una dieta equilibrada que incluya una variedad de alimentos para asegurar una ingesta adecuada de todos los nutrientes esenciales.
