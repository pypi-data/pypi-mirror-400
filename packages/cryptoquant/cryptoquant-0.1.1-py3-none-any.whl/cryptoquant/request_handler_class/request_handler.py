# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 18:14:29 2025

@author: lauta
"""

from __future__ import annotations
import re
from datetime import datetime
from typing import Any, Dict, Mapping, Optional, Union

import requests


DEFAULT_TIMEOUT: float = 10

# Timestamp format patterns for validation and formatting
TIMESTAMP_FULL_FORMAT_PATTERN: str = r'^\d{8}T\d{6}$'  # YYYYMMDDTHHMMSS
TIMESTAMP_DATE_FORMAT_PATTERN: str = r'^\d{8}$'  # YYYYMMDD


class RequestHandler:
    """
    Clase encargada de manejar las solicitudes HTTP hacia la API de CryptoQuant.

    Esta clase centraliza la configuración del endpoint base, encabezados de autenticación
    y la lógica para formatear los parámetros y procesar las respuestas.
    Permite obtener resultados tanto en formato JSON como CSV (texto plano).

    """

    def __init__(
        self,
        api_key: str,
        session: Optional[requests.Session] = None,
        default_timeout: Optional[float] = None,
    ) -> None:
        """
        Inicializa el manejador con la clave API de autenticación.

        Parameters
        ----------
        api_key : str
            Token de acceso personal proporcionado por CryptoQuant.
        session : requests.Session, optional
            Sesión HTTP reutilizable para realizar las solicitudes.
            Si no se proporciona, se crea una nueva instancia.
        default_timeout : float, optional
            Tiempo de espera por defecto (en segundos) para las solicitudes.
            Si no se especifica, se utiliza ``DEFAULT_TIMEOUT``.
        """
        self.API_KEY_ = api_key
        self.resp: Optional[requests.Response] = None
        self.HEADERS_: Dict[str, str] = {"Authorization": "Bearer " + self.API_KEY_}
        self.HOST_: str = "https://api.cryptoquant.com/v1/"
        self.session: requests.Session = session or requests.Session()
        self.timeout: float = DEFAULT_TIMEOUT if default_timeout is None else default_timeout

    # ---------------------------------------------------------------------
    # Métodos internos (uso privado)
    # ---------------------------------------------------------------------

    def __append_fmt(self, dict_to_append: Optional[Mapping[str, str]]) -> Dict[str, str]:
        """
        Normaliza las claves de un diccionario de parámetros de consulta (`query_params`).

        Este método:
        - Elimina nombres reservados conflictivos (`from`, `type`, `filter`, `format`).
        - Reemplaza las claves con sufijo "_" (ej. `from_`) por su versión correcta
          para ajustarse a los parámetros esperados por la API.
        - Acepta tanto `format` como `format_`, priorizando `format_` cuando ambos
          estén presentes.
        - Valida el formato de timestamps cuando se especifica window='hour' para
          consultas intradiarias.

        Parameters
        ----------
        dict_to_append : Mapping[str, str] or None
            Diccionario original de parámetros a normalizar.

        Returns
        -------
        dict
            Diccionario con las claves normalizadas, apto para ser enviado en la query.

        Raises
        ------
        ValueError
            Si se detecta una consulta intradiaria (window='hour') con timestamps
            en formato incorrecto.
        """
        normalized_params: Dict[str, str] = {}
        preferred_format: Optional[str] = None
        if dict_to_append:
            normalized_params.update(dict_to_append)
            preferred_format = dict_to_append.get("format_")
            if preferred_format is None:
                preferred_format = dict_to_append.get("format")

        # Eliminar nombres reservados para evitar colisiones
        for reserved in ("from", "type", "filter", "format", "to"):
            normalized_params.pop(reserved, None)

        # Mapear variantes con sufijo "_"
        replacements = {
            "from_": "from",
            "type_": "type",
            "filter_": "filter",
            "format_": "format",
            "to_": "to",
        }

        for current_key, target_key in replacements.items():
            if current_key in normalized_params:
                normalized_params[target_key] = normalized_params.pop(current_key)

        if preferred_format is not None:
            normalized_params["format"] = preferred_format

        # Validar timestamps para consultas intradiarias
        window = normalized_params.get("window", "").lower()
        if window == "hour":
            # Validar 'from' timestamp si está presente
            if "from" in normalized_params:
                from_ts = normalized_params["from"]
                if not self.validate_timestamp(from_ts, window):
                    raise ValueError(
                        f"For intraday queries (window='hour'), 'from' timestamp must be in format "
                        f"YYYYMMDDTHHMMSS. Got: '{from_ts}'. Example: '20240101T120000'"
                    )

            # Validar 'to' timestamp si está presente
            if "to" in normalized_params:
                to_ts = normalized_params["to"]
                if not self.validate_timestamp(to_ts, window):
                    raise ValueError(
                        f"For intraday queries (window='hour'), 'to' timestamp must be in format "
                        f"YYYYMMDDTHHMMSS. Got: '{to_ts}'. Example: '20240101T235959'"
                    )

        return normalized_params

    def __url_api(self, url_to_append: str) -> str:
        """
        Construye la URL completa para una solicitud específica de la API.

        Parameters
        ----------
        url_to_append : str
            Ruta parcial del recurso o endpoint dentro de la API.

        Returns
        -------
        str
            URL completa lista para ser usada en la llamada HTTP.
        """
        return self.HOST_ + url_to_append

    # ---------------------------------------------------------------------
    # Métodos públicos
    # ---------------------------------------------------------------------

    def handle_request(
        self,
        endpoint_url: str,
        query_params: Optional[Mapping[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Union[Dict[str, Any], str]:
        """
        Envía una solicitud GET a la API de CryptoQuant y maneja la respuesta.

        Según el valor del parámetro `format`/`format_`, la respuesta se interpreta como:
        - `format='csv'`: Devuelve el cuerpo en texto plano CSV.
        - Por defecto: Devuelve un objeto JSON (tipo `dict`).
        Si el contenido no es JSON válido, devuelve el texto crudo.

        Parameters
        ----------
        endpoint_url : str
            Ruta relativa del endpoint (por ejemplo, `"btc/network/hashrate"`).
        query_params : Mapping[str, str], optional
            Parámetros de consulta (`window`, `interval`, `format_`, etc.).
            Las claves con sufijo `_` se normalizan automáticamente. Si se pasan
            `format` y `format_`, prevalece `format_`.
        timeout : float, optional
            Tiempo de espera para esta solicitud en particular. Si no se
            especifica, se utiliza el ``default_timeout`` configurado en la
            instancia.

        Returns
        -------
        dict or str
            Objeto JSON (si `format` no es `'csv'`) o texto CSV (si `format='csv'`).

        Raises
        ------
        requests.HTTPError
            Si la API devuelve un código de estado diferente de 200.

        """
        # Construir URL completa
        endpoint_url_ = self.__url_api(endpoint_url)

        # Normalizar parámetros
        query_params_ = self.__append_fmt(query_params)

        request_timeout = self.timeout if timeout is None else timeout

        # Realizar la solicitud HTTP
        self.resp = self.session.get(
            url=endpoint_url_,
            headers=self.HEADERS_,
            params=query_params_,
            timeout=request_timeout,
        )

        # Evaluar la respuesta
        if self.resp.status_code == 200:
            fmt = query_params_.get("format", "").lower()

            # Si se solicitó CSV → devolver texto plano
            if fmt == "csv":
                return self.resp.text

            # Intentar decodificar JSON
            try:
                return self.resp.json()
            except ValueError:
                # Si no es JSON válido, devolver texto crudo
                return self.resp.text

        # Si la respuesta no fue exitosa → lanzar excepción
        self.resp.raise_for_status()

    @staticmethod
    def validate_timestamp(timestamp: str, window: Optional[str] = None) -> bool:
        """
        Valida el formato de timestamp según el tipo de ventana.

        Para consultas intradiarias (window='hour'), se requiere el formato completo
        YYYYMMDDTHHMMSS. Para consultas diarias (window='day'), se acepta tanto
        YYYYMMDD como YYYYMMDDTHHMMSS.

        Parameters
        ----------
        timestamp : str
            Timestamp a validar.
        window : str, optional
            Tipo de ventana ('day', 'hour', 'block'). Si no se especifica,
            solo se valida el formato básico.

        Returns
        -------
        bool
            True si el formato es válido, False en caso contrario.

        Examples
        --------
        >>> RequestHandler.validate_timestamp('20240101', 'day')
        True
        >>> RequestHandler.validate_timestamp('20240101T120000', 'hour')
        True
        >>> RequestHandler.validate_timestamp('20240101', 'hour')
        False
        """
        # Si window es 'hour', se requiere formato completo
        if window == 'hour':
            if not re.match(TIMESTAMP_FULL_FORMAT_PATTERN, timestamp):
                return False
            # Validar que la fecha y hora sean válidas
            try:
                datetime.strptime(timestamp, '%Y%m%dT%H%M%S')
                return True
            except ValueError:
                return False

        # Si window es 'day', se acepta tanto formato completo como solo fecha
        if window == 'day':
            if re.match(TIMESTAMP_DATE_FORMAT_PATTERN, timestamp):
                try:
                    datetime.strptime(timestamp, '%Y%m%d')
                    return True
                except ValueError:
                    return False
            elif re.match(TIMESTAMP_FULL_FORMAT_PATTERN, timestamp):
                try:
                    datetime.strptime(timestamp, '%Y%m%dT%H%M%S')
                    return True
                except ValueError:
                    return False
            return False

        # Si no se especifica window, validar formato básico
        if re.match(TIMESTAMP_DATE_FORMAT_PATTERN, timestamp):
            try:
                datetime.strptime(timestamp, '%Y%m%d')
                return True
            except ValueError:
                return False
        elif re.match(TIMESTAMP_FULL_FORMAT_PATTERN, timestamp):
            try:
                datetime.strptime(timestamp, '%Y%m%dT%H%M%S')
                return True
            except ValueError:
                return False

        return False

    @staticmethod
    def format_timestamp_for_window(timestamp: Union[str, datetime], window: str = 'day') -> str:
        """
        Formatea un timestamp según el tipo de ventana especificado.

        Para consultas intradiarias (window='hour'), devuelve el formato
        YYYYMMDDTHHMMSS. Para consultas diarias (window='day'), puede devolver
        YYYYMMDD o YYYYMMDDTHHMMSS.

        Parameters
        ----------
        timestamp : str or datetime
            Timestamp a formatear. Puede ser un string en formato YYYYMMDD,
            YYYYMMDDTHHMMSS, o un objeto datetime.
        window : str, optional
            Tipo de ventana ('day' o 'hour'). Por defecto 'day'.

        Returns
        -------
        str
            Timestamp formateado apropiadamente para el tipo de ventana.

        Raises
        ------
        ValueError
            Si el timestamp no tiene un formato válido o si se requiere formato
            completo para window='hour' pero solo se proporciona fecha.

        Examples
        --------
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 1, 12, 0, 0)
        >>> RequestHandler.format_timestamp_for_window(dt, 'hour')
        '20240101T120000'
        >>> RequestHandler.format_timestamp_for_window('20240101', 'day')
        '20240101'
        """
        # Si es un objeto datetime, convertir a string
        if isinstance(timestamp, datetime):
            if window == 'hour':
                return timestamp.strftime('%Y%m%dT%H%M%S')
            else:  # window == 'day' o cualquier otro
                return timestamp.strftime('%Y%m%d')

        # Si es un string, validar y ajustar formato
        timestamp = str(timestamp).strip()

        # Formato completo: YYYYMMDDTHHMMSS
        if re.match(TIMESTAMP_FULL_FORMAT_PATTERN, timestamp):
            # Validar que sea una fecha válida
            try:
                datetime.strptime(timestamp, '%Y%m%dT%H%M%S')
            except ValueError:
                raise ValueError(f"Invalid timestamp format: {timestamp}")
            return timestamp

        # Formato solo fecha: YYYYMMDD
        if re.match(TIMESTAMP_DATE_FORMAT_PATTERN, timestamp):
            # Validar que sea una fecha válida
            try:
                datetime.strptime(timestamp, '%Y%m%d')
            except ValueError:
                raise ValueError(f"Invalid date format: {timestamp}")

            # Para window='hour', necesitamos formato completo
            if window == 'hour':
                raise ValueError(
                    f"For intraday queries (window='hour'), timestamp must include time. "
                    f"Got: {timestamp}. Expected format: YYYYMMDDTHHMMSS (e.g., '20240101T120000')"
                )
            return timestamp

        # Si no coincide con ningún formato conocido
        raise ValueError(
            f"Invalid timestamp format: {timestamp}. "
            f"Expected YYYYMMDD or YYYYMMDDTHHMMSS"
        )
