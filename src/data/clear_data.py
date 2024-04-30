# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 07:45:15 2024

@author: abartolo
"""
"""
# clear_data.py

Este script contiene funciones para limpiar y procesar datos antes de su análisis posterior.

Primero, se define una función para quitar un carácter específico solo de algunos valores basados en una condición
específica en una columna del DataFrame.

Luego, se filtran los eventos que no están cancelados en el DataFrame de reporte de eventos.

Finalmente, se define una función para filtrar fechas de eventos basadas en la distribución gaussiana de las fechas
de energización. Esta función agrupa los eventos por tipo y filtra las fechas de energización dentro del intervalo
de confianza, manteniendo las filas más cercanas a la media de las fechas filtradas.

"""

import numpy as np
import pandas as pd

# Tratamiento de datos y llamada a load_data
from data.load_data import corte_original,reporte_eventos

  
# Condición para quitar el carácter solo a algunos valores basado en la columna 'tipo'
condicion_tipo = corte_original['TIPO'] == 'I'
caracter_a_quitar = '-'
# Aplicar la función solo a los valores que cumplen la condición en la columna 'tipo'
corte_original.loc[condicion_tipo, ['CODIGO', 'CIRCUITO']] = corte_original.loc[condicion_tipo, ['CODIGO', 'CIRCUITO']].apply(lambda x: x.str.rstrip(caracter_a_quitar))
# Filtrar eventos que no estén cancelados
reporte_eventos = reporte_eventos.loc[reporte_eventos['Estado Evento'] != 'CANCELADO']


# Definir una función para filtrar fechas basadas en la distribución gaussiana

def filtrar_fechas(reporte_eventos):
    """
    Función que filtra las fechas de eventos basándose en la distribución gaussiana de las fechas de energización.

    Parameters
    ----------
    reporte_eventos : pd.DataFrame
        DataFrame que contiene información de reporteEventos.

    Returns
    -------
    reporte_eventos_filtrado : pd.DataFrame
        DataFrame filtrado con fechas de energización dentro del intervalo de confianza.

    Notes
    -----
    Esta función toma un DataFrame de eventos y, para cada grupo de eventos, filtra las fechas de energización
    basándose en la distribución gaussiana de las diferencias temporales entre las fechas de energización y su media.

    """
    # Crear un nuevo DataFrame para almacenar las filas finales
    filas_finales = []
    # Agrupar el DataFrame por la columna "Eventos"
    grupos = reporte_eventos.groupby('EVENTO')
    for evento, grupo in grupos:
        dates_energizacion=grupo['TIE_ENERGIZACION']
        dates_finalizacion=grupo['FEC_REALFIN']
        # Verificar si todas las fechas de energización están vacías
        if dates_energizacion.isnull().all():
            # Usar las fechas de finalización si todas las fechas de energización están vacías
            fechas_a_usar = dates_finalizacion
        else:
            # Eliminar filas con fechas de energización vacías
            grupo_sin_nulos = grupo.dropna(subset=['TIE_ENERGIZACION'])
            fechas_a_usar = grupo_sin_nulos['TIE_ENERGIZACION']
        
        deltas = (fechas_a_usar - fechas_a_usar.mean()).dt.total_seconds()

        media = np.mean(deltas)
        desviacion_estandar = np.std(deltas)
        
        # Filtrar fechas dentro del intervalo de confianza
        fechas_filtradas = fechas_a_usar[(media - 1.5 * desviacion_estandar <= deltas) & (deltas <= media + 1.5 * desviacion_estandar)]
        
        # Calcular la media de las fechas filtradas y mantener la fila más cercana a la media
        fecha_media = fechas_filtradas.mean()
        if not grupo.empty:
            # Sort excluding NA values and then select the first row
            sorted_indices = fechas_filtradas.sub(fecha_media).abs().sort_values(na_position='last').index
            # Check if there are any indices left after sorting
            if len(sorted_indices) > 0:
                fila_mas_cercana = grupo.loc[sorted_indices[:1]]
                filas_finales.append(fila_mas_cercana)
            else:
                # Handle the case where there are no valid indices
                # You may choose to skip appending in this case or handle it differently
                pass
    # Crear un nuevo DataFrame con las filas finales
    reporte_eventos_filtrado = pd.concat(filas_finales)
        
    return reporte_eventos_filtrado
     