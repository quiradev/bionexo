# Los nutrientes pueden tener sinergias o antagonismos entre ellos que afectan su absorcion y utilizacion en el cuerpo humano.
# Donde cuando hay sinergias, puede tener efectos:
# - Mejora de la absorcion de uno o ambos nutrientes o de otros nutrientes relacionados
# - Aumento de la biodisponibilidad (la fraccion del nutriente que es absorbida y utilizada por el cuerpo)
# - Potenciacion de efectos fisiologicos o metabolicos

# Y cuando hay antagonismos, puede tener efectos:
# - Disminucion de la absorcion de uno o ambos nutrientes o de otros nutrientes relacionados
# - Reduccion de la biodisponibilidad
# - Inhibicion de efectos fisiologicos o metabolicos

from typing import Literal

from pydantic import BaseModel

class AbsortionNutrientInteraction(BaseModel):
    """
    Representa una interaccion entre nutrientes que afecta su absorcion.
    La batalla en la aduana por la absorcion de nutrientes. Los minerales usan puertas llamadas transportadores
    de iones. Si tomas mucho calcio y hierro juntos, compiten por la misma puerta, y uno puede bloquear al otro. perdiendo el hierro.
    1. Sinergia: La vitamina C ayuda a absorber el hierro no hemo (de origen vegetal) al convertirlo a una forma más absorbible.
    2. Antagonismo: El calcio puede interferir con la absorción del hierro cuando se consumen juntos.
    """
    nutrients: list[str]  # Lista de nutrientes involucrados
    interaction_type: Literal['synergy', 'antagonism']  # 'synergy' o 'antagonism'
    effect_description: str  # Descripcion del efecto de la interaccion

class MetabolicNutrientInteraction(BaseModel):
    """
    Representa una interaccion entre nutrientes que afecta su metabolismo.
    Algunos nutrientes pueden influir en las vias metabolicas de otros nutrientes, afectando su utilizacion energetica o almacenamiento.
    1. Sinergia: Los carbohidratos y las proteínas juntos pueden aumentar la liberacion de insulina, lo que ayuda a transportar ambos nutrientes a las celulas para su uso o almacenamiento.
    2. Antagonismo: El exceso de grasas puede reducir la capacidad del cuerpo para utilizar carbohidratos como fuente de energia, favoreciendo el almacenamiento de grasa.
    """
    nutrients: list[str]  # Lista de nutrientes involucrados
    interaction_type: Literal['synergy', 'antagonism']  # 'synergy' o 'antagonism'
    effect_description: str  # Descripcion del efecto de la interaccion
    affected_metabolic_pathways: list[str]  # Via metabolicas afectadas

class NutrientInteractionProfile(BaseModel):
    interactions: list[AbsortionNutrientInteraction | MetabolicNutrientInteraction] = []  # Lista de interacciones entre nutrientes