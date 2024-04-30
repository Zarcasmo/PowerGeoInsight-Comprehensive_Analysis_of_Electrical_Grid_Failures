# -*- coding: utf-8 -*-

"""
Created on Tue Oct 24 11:12:52 2023

@author: abartolo
"""

"""
Módulo Main_analisis_falla.py

Este módulo sirve como punto de entrada principal para el programa de análisis de fallas. Importa funciones
de los módulos analysis y data(load_data y clear_data) para procesar la entrada del usuario, filtrar datos y realizar
el análisis de fallas.

Uso:
1. Ejecute este script para analizar interactivamente fallas basadas en la entrada del usuario.

Dependencias del Módulo:
- analysis.analysis: Proporciona la función 'analisis_fallas' para el análisis de fallas.
- data.load_data: Utiliza la función 'procesar_entrada' para procesar la entrada del usuario.
- data.clear_data: Implementa 'filtrar_fechas' y 'reporte_eventos' para el filtrado de datos.

Funciones:
1. `obtener_entrada_usuario()`: Solicita la entrada del usuario y devuelve el valor ingresado.
2. Ejecución principal: Procesa la entrada del usuario, filtra datos y realiza el análisis de fallas para cada circuito.

Ejemplo:
    Para utilizar este script, ejecútelo en un entorno de Python y siga las indicaciones para ingresar valores.

"""

#Principal
# Main_analisis_falla.pylas.py
from analysis.analysis import analisis_fallas
from data.load_data import procesar_entrada
#llamar clear_data para las dataframe que necesiten tratamiento de datos
from data.clear_data import filtrar_fechas,reporte_eventos

def obtener_entrada_usuario():
    """
    Función que solicita la entrada del usuario y devuelve el valor ingresado.

    Returns:
        str: Valor ingresado por el usuario.
    """
    # Pide una entrada al usuario
    # Valores de ejemplo CARQ0155,CARQ0122,CARQ0124
    entrada_usuario =input("Ingrese un valor: ")
    return entrada_usuario

# Procesa la entrada del usuario y filtra eventos según las fechas
entrada_usuario = obtener_entrada_usuario()
entrada_procesada = procesar_entrada(entrada_usuario)
reporte_eventos_filtrado=filtrar_fechas(reporte_eventos)

# Analiza fallas para cada circuito

circuitos = entrada_procesada["circuito"].unique()
for i in circuitos:
    entrada_x_circuito = entrada_procesada.loc[entrada_procesada['circuito']==i]
    analisis_fallas(entrada_x_circuito,reporte_eventos_filtrado, i)