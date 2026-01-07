import os
import time
from typing import Dict, Any, Optional, List
from openfoodfacts import API, APIVersion, Country, Environment as OFFEnvironment, Flavor
from openfoodfacts import utils as off_utils
from openfoodfacts.api import send_get_request

from bionexo.application.definitions import Environment
from bionexo.repository.config import RepositoryConfig
from bionexo.repository.entity.open_food_facts import SearchAdvanceParams

PRODUCT_RATE = 'product'
SEARCH_RATE = 'search'
FACET_RATE = 'facet'

# Limites por minuto
rates_limits = {
    PRODUCT_RATE: 100,
    SEARCH_RATE: 10,
    FACET_RATE: 2
}

# Peticiones por minuto: {timestamp_minuto: count}
rates = {
    PRODUCT_RATE: {},
    SEARCH_RATE: {},
    FACET_RATE: {}
}


def _get_current_minute():
    """Obtiene el timestamp redondeado al minuto actual."""
    return int(time.time() // 60)


def _get_request_count(rate_type: str) -> int:
    """Obtiene el contador de peticiones del minuto actual."""
    current_minute = _get_current_minute()
    
    # Limpiar minutos antiguos
    for timestamp in list(rates[rate_type].keys()):
        if timestamp < current_minute:
            del rates[rate_type][timestamp]
    
    return rates[rate_type].get(current_minute, 0)


def _increment_request_count(rate_type: str):
    """Incrementa el contador de peticiones del minuto actual."""
    current_minute = _get_current_minute()
    rates[rate_type][current_minute] = _get_request_count(rate_type) + 1


def check_product_rate(func):
    def wrapper(*args, **kwargs):
        if _get_request_count(PRODUCT_RATE) >= rates_limits[PRODUCT_RATE]:
            raise Exception("Límite de tasa de productos alcanzado.")
        _increment_request_count(PRODUCT_RATE)
        return func(*args, **kwargs)
    return wrapper


def check_search_rate(func):
    def wrapper(*args, **kwargs):
        if _get_request_count(SEARCH_RATE) >= rates_limits[SEARCH_RATE]:
            raise Exception("Límite de tasa de búsquedas alcanzado.")
        _increment_request_count(SEARCH_RATE)
        return func(*args, **kwargs)
    return wrapper

def check_facet_rate(func):
    def wrapper(*args, **kwargs):
        if _get_request_count(FACET_RATE) >= rates_limits[FACET_RATE]:
            raise Exception("Límite de tasa de facets alcanzado.")
        _increment_request_count(FACET_RATE)
        return func(*args, **kwargs)
    return wrapper


class OpenFoodFactsAPI:
    def __init__(self, config: RepositoryConfig):
        OPENFOODFACTS_EMAIL = os.getenv('OPENFOODFACTS_EMAIL')
        OPENFOODFACTS_APP = os.getenv('OPENFOODFACTS_APP')
        VERSION = os.getenv('VERSION')

        user_agent = f'{OPENFOODFACTS_APP}/{VERSION}'
        if OPENFOODFACTS_EMAIL:
            user_agent = f'{user_agent} ({OPENFOODFACTS_EMAIL})'

        if config.environment == Environment.DEV:
            off_environment = OFFEnvironment.test
        else:
            off_environment = OFFEnvironment.net

        self.driver = API(
            user_agent=user_agent,
            username=None,
            password=None,
            country=Country.es,
            flavor=Flavor.off,
            version=APIVersion.v2,
            environment=off_environment,
        )

    @check_product_rate
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un producto por código de barras.
        Retorna None si no se encuentra.
        """
       
        # Comma separated list of fields requested in the response.
        # Special values:

        # "none": returns no fields
        # "raw": returns all fields as stored internally in the database
        # "all": returns all fields except generated fields that need to be explicitly requested such as "knowledge_panels".
        fields = "all"
        response = self.driver.product.get(
            barcode,
            fields=fields,
            raise_if_invalid=False
        )
        if response.get('status') == 1:
            return self._parse_product(response['product'])
        return None

    @check_search_rate
    def search_products(self, query: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Busca productos por nombre o términos.
        """

        
        # v1
        response = self.driver.product.text_search(query, page=page, page_size=page_size, sort_by='unique_scans_n')
        


        products = [self._parse_product(p) for p in response.get('products', []) if p]
        return {
            'products': products,
            'count': response.get('count', 0),
            'page': page,
            'page_size': page_size
        }

    @check_search_rate
    def search_products_advanced(
            self,
            params: SearchAdvanceParams = None,
            page: int = 1,
            page_size: int = 20,
    
    ) -> Dict[str, Any]:
        # Important: search API v2 does not support full text request (search_term), you have to use search API v1 for that. Upcoming search-a-licious project will fix that.

        # Limiting results
        # You can limit the size of returned objects thanks to the fields object (see below).

        # eg: `fields=code,product_name,brands,attribute_groups``

        # Please use it as much as possible to avoid overloading the servers.

        # The search use pagination, see page and page_size parameters.

        # Beware: the page_count data in item is a bit counter intuitive…, read the description.

        # Conditions on tags
        # All `_tags`` parameters accepts either:

        # a single value
        # or a comma-separated list of values (doing a AND)
        # or a pipe separated list of values (doing a OR)
        # You can exclude terms by using a "-" prefix.

        # For taxonomized entries, you might either use the tag id (recommended), or a known synonym (without language prefix)

        # labels_tags=en:organic,en:fair-trade find items that are fair-trade AND organic
        # labels_tags=en:organic|en:fair-trade find items that are fair-trade OR organic
        # labels_tags=en:organic,en:-fair-trade find items that are organic BUT NOT fair-trade
        # Conditions on nutriments
        # To get a list of nutrients

        # You can either query on nutrient per 100g (_100g suffix) or per serving (serving suffix).

        # You can also add _prepared_ to get the nutrients in the prepared product instead of as sold.

        # You can add a comparison operator and value to the parameter name to get products with nutrient above or bellow a value. If you use a parameter value it exactly match it.

        # energy-kj_100g<200 products where energy in kj for 100g is less than 200kj
        # sugars_serving>10 products where sugar per serving is greater than 10g
        # saturated-fat_100g=1 products where saturated fat per 100g is exactly 10g
        # salt_prepared_serving<0.1 products where salt per serving for prepared product is less than 0.1g


        
        url = f"{self.driver.product.base_url}/api/{self.driver.product.api_config.version.value}/search"
        params = {

        }
        return send_get_request(
            url=url, api_config=self.api_config,
            params=params,
            return_none_on_404=True
        )

    def get_by_facets(self, query: Dict[str, str], page: int = 1, locale: str = 'world') -> List[Dict[str, Any]]:
        """
        Retorna productos para un conjunto de facets.
        """
        path = []
        keys = sorted(query.keys())
        for key in keys:
            path.append(key)
            path.append(query[key])
        url = off_utils.build_url(geography=locale, resource_type=path, parameters=str(page))
        response = self.driver.get(url[len(self.driver.config['base_url']):])  # Remover base_url ya que driver lo añade
        return [self._parse_product(p) for p in response.get('products', [])]

    def add_new_product(self, post_data: Dict[str, Any], locale: str = 'world') -> Dict[str, Any]:
        """
        Agrega un nuevo producto a la base de datos de OFF.
        """
        if not post_data.get('code') or not post_data.get('product_name'):
            raise ValueError('code or product_name not found!')
        url = off_utils.build_url(geography='world', service='cgi', resource_type='product_jqm2.pl')
        endpoint = url[len(self.driver.config['base_url']):]
        return self.driver.post(endpoint, data=post_data)

    def upload_image(self, code: str, imagefield: str, img_path: str) -> Dict[str, Any]:
        """
        Sube una nueva imagen para un producto.
        imagefield: 'front', 'ingredients', 'nutrition'
        """
        if imagefield not in ["front", "ingredients", "nutrition"]:
            raise ValueError("Imagefield not valid!")
        url = off_utils.build_url(service='cgi', resource_type='product_image_upload.pl')
        endpoint = url[len(self.driver.config['base_url']):]
        files = {f"imgupload_{imagefield}": open(img_path, 'rb')}
        data = {'code': code, 'imagefield': imagefield}
        return self.driver.post(endpoint, data=data, files=files)

    def advanced_search(self, post_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza una búsqueda avanzada.
        """
        post_query['json'] = '1'
        url = off_utils.build_url(service='cgi', resource_type='search.pl', parameters=post_query)
        endpoint = url[len(self.driver.config['base_url']):]
        return self.driver.get(endpoint)
    
    def _parse_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parsea los datos del producto para extraer info nutricional relevante.
        """
        nutriments = product_data.get('nutriments', {})
        return {
            'barcode': product_data.get('code'),
            'name': product_data.get('product_name', 'Desconocido'),
            'brands': product_data.get('brands', ''),
            'categories': product_data.get('categories', ''),
            'kcal_per_100g': nutriments.get('energy-kcal_100g') or nutriments.get('energy_100g', 0) / 4.184 if nutriments.get('energy_100g') else 0,
            'nutrients': {
                'protein': nutriments.get('proteins_100g', 0),
                'carbs': nutriments.get('carbohydrates_100g', 0),
                'fat': nutriments.get('fat_100g', 0),
                'fiber': nutriments.get('fiber_100g', 0),
                'sugars': nutriments.get('sugars_100g', 0),
                'salt': nutriments.get('salt_100g', 0),
            },
            'allergens': product_data.get('allergens_tags', []),
            'ingredients': product_data.get('ingredients_text', ''),
            'image_url': product_data.get('image_url'),
            'raw_data': product_data  # Para acceso completo si es necesario
        }