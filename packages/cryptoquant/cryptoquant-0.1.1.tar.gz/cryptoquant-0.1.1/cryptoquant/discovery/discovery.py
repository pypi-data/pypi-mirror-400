# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 18:55:33 2025

@author: lauta
"""

from __future__ import annotations
from typing import Any, Dict
from cryptoquant.request_handler_class import RequestHandler


class Discovery(RequestHandler):
    """
    Módulo de descubrimiento de endpoints disponibles en la API de CryptoQuant.

    Este módulo forma parte del cliente principal :class:`CryptoQuant`
    y permite consultar todos los endpoints soportados junto con sus
    parámetros disponibles.

    Generalmente no se instancia directamente. En su lugar, se accede
    a través de la clase principal ``CryptoQuant``.

    Ejemplo
    -------
    >>> from cryptoquant import CryptoQuant
    >>> import os
    >>> api_key = os.environ["CQ_API"]
    >>> client = CryptoQuant(api_key)
    >>> resp = client.get_endpoints()
    >>> print(type(resp))
    <class 'dict'>
    """

    def __init__(self, api_key: str):
        """
        Inicializa el módulo Discovery con la URL base del endpoint.

        Parameters
        ----------
        api_key : str
            Token de autenticación de la API de CryptoQuant.
        """
        self.DISCOVERY_URL_ENDPOINT: str = "discovery/endpoints"
        super().__init__(api_key)

    def get_endpoints(self, **query_params: Any) -> Dict[str, Any] | str:
        """
        Devuelve la lista de endpoints disponibles en la API y sus parámetros.

        Parameters
        ----------
        **query_params : Any
            Parámetros opcionales de la consulta.
            Puede incluir `format_` o `format` para especificar el formato
            de salida. Valores válidos: ``"json"`` o ``"csv"``.

        Returns
        -------
        dict or str
            - Si `format_='json'` (por defecto): objeto JSON con los endpoints.
            - Si `format_='csv'`: texto plano CSV con la misma información.

        Raises
        ------
        requests.HTTPError
            Si la solicitud no fue exitosa (códigos 4xx o 5xx).

        Examples
        --------
        >>> from cryptoquant import CryptoQuant
        >>> import os
        >>> api_key = os.environ["CQ_API"]
        >>> client = CryptoQuant(api_key)

        # Ejemplo 1: Obtener respuesta JSON
        >>> data = client.get_endpoints()
        >>> isinstance(data, dict)
        True

        # Ejemplo 2: Obtener respuesta CSV
        >>> csv_data = client.get_endpoints(format_="csv")
        >>> print(csv_data.splitlines()[0])
        'path,parameters,required_parameters'
        """
        return super().handle_request(self.DISCOVERY_URL_ENDPOINT, query_params)

