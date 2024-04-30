# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 07:54:06 2024

@author: abartolo
"""

"""
generate_map.py

Este módulo proporciona funciones para generar un mapa interactivo HTML que visualiza diferentes capas de información geoespacial, como elementos de corte, transformadores, redes eléctricas MT y BT, usuarios, entre otros.

Funciones
---------
graficar_html(gdf, cortes, trafo, gdf2, corte2, trafo2, red_BT_result, graf_usuario_result, total_aperturas,
              total_aperturas1, total_aperturas2, total_tiempo, total_tiempo1, total_tiempo2, suma_aperturas,
              circuito_name)
    Genera un mapa interactivo HTML que visualiza diferentes capas de información geoespacial.

    Parameters
    ----------
    Dataframes:pd.DataFrame
        Conjunto de DataFrames que contienen información del SDL

    circuito_name : str
        Nombre del circuito para incluir en el nombre del archivo HTML.

    Returns
    -------
    None
        Abre el mapa interactivo en el navegador web y guarda un archivo HTML en la carpeta de destino.

    Notes
    -----
    - El mapa incluye capas para la red MT, elementos de corte, transformadores, red BT, usuarios, y más.
    - Se utilizan diferentes colores y tamaños de marcadores para representar diversas propiedades y aperturas de los elementos.
    - El archivo HTML se guarda en la carpeta '../reports/' con un nombre que incluye el nombre del circuito.
    - Se requiere la biblioteca Folium para la generación del mapa interactivo.
"""

import folium
from shapely.geometry import Point #libreria para dibujar
import webbrowser
import numpy as np
import pandas as pd
import os

#Contiene las Funciones de graficar y se llama en analysis
# La salida(HTML) se debe guardar en report

def graficar_html(gdf,cortes,trafo,gdf2,corte2,trafo2,red_BT_result,graf_usuario_result,total_aperturas,total_aperturas1,total_aperturas2,total_tiempo,total_tiempo1,total_tiempo2,suma_aperturas,circuito_name):
    """
    Genera un mapa interactivo HTML que visualiza diferentes capas de información geoespacial.

    Parameters
    ----------
    gdf : pandas.DataFrame
        DataFrame que contiene información geográfica para la red MT.

    cortes : pandas.DataFrame
        DataFrame que contiene información sobre los elementos de corte.

    trafo : pandas.DataFrame
        DataFrame que contiene información sobre los transformadores.

    gdf2 : pandas.DataFrame
        DataFrame que contiene información geográfica adicional para el SDL.

    corte2 : pandas.DataFrame
        DataFrame que contiene información adicional sobre los elementos de corte.

    trafo2 : pandas.DataFrame
        DataFrame que contiene información adicional sobre los transformadores del sistema.

    red_BT_result : pandas.DataFrame
        DataFrame con información sobre la red BT.

    graf_usuario_result : pandas.DataFrame
        DataFrame con información sobre los usuarios.

    total_aperturas : pandas.DataFrame
        DataFrame con totales de aperturas para diferentes elementos.

    total_aperturas1 : pandas.DataFrame
        DataFrame con totales de aperturas para diferentes elementos (variante 1).

    total_aperturas2 : pandas.DataFrame
        DataFrame con totales de aperturas para diferentes elementos (variante 2).

    total_tiempo : pandas.DataFrame
        DataFrame con totales de tiempo para diferentes elementos.

    total_tiempo1 : pandas.DataFrame
        DataFrame con totales de tiempo para diferentes elementos (variante 1).

    total_tiempo2 : pandas.DataFrame
        DataFrame con totales de tiempo para diferentes elementos (variante 2).

    suma_aperturas : pandas.DataFrame
        DataFrame con información consolidada sobre aperturas.

    circuito_name : str
        Nombre del circuito para incluir en el nombre del archivo HTML.

    Returns
    -------
    None
        Abre el mapa interactivo en el navegador web y guarda un archivo HTML en la carpeta de destino.

    Notes
    -----
    - El mapa incluye capas para la red MT, elementos de corte, transformadores, red BT, usuarios, y más.
    - Se utilizan diferentes colores y tamaños de marcadores para representar diversas propiedades.
    - El archivo HTML se guarda en la carpeta '../reports/' con un nombre que incluye el nombre del circuito.
    - Se requiere la biblioteca Folium para la generación del mapa interactivo.

    """
    
    # Creacion Mapa HTML(base)
    # Crear una lista de puntos geoespaciales a partir de las coordenadas
    coordenadas = [(row['X_INICIAL'], row['Y_INICIAL']) for index, row in gdf.iterrows()]
    puntos = [Point(coordenada) for coordenada in coordenadas]
    
    # Calcular el punto medio geoespacial
    centro_geoespacial = Point([sum([p.x for p in puntos])/len(puntos), sum([p.y for p in puntos])/len(puntos)])
    
    #Referencia geoespacial
    gdf = gdf.set_crs("EPSG:4326")
    
    # Crear un mapa de Folium centrado en el departamento del Quindio
    mapa = folium.Map(location=[centro_geoespacial.y, centro_geoespacial.x], zoom_start=15, opacity=0.5)
    
    #%%Funciones     
    
    #Función para bibujar marcadores tipo punto.
    def tipo_punto(dataframe, color_asignado, size,  forma, color_contorno, rotacion, nombres,capa, tipo=None):
        """
        Función que dibuja marcadores tipo punto en un mapa interactivo(mapa).
    
        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame que contiene la información para dibujar los marcadores.
    
        color_asignado : str
            Color asignado a los marcadores si no se proporciona un tipo específico.
    
        size : int
            Tamaño de los marcadores.
    
        forma : int
            Número de lados de los marcadores (para hacerlo poligonal).
    
        color_contorno : str
            Color del borde de los marcadores.
    
        rotacion : int
            Ajuste de rotación para la forma de los marcadores.
    
        nombres : str
            Nombre de la columna que contiene los nombres para los marcadores.
    
        capa : folium.Map
            Capa del mapa donde se agregarán los marcadores.
    
        tipo : dict, optional
            Diccionario que contiene información sobre tipos específicos de marcadores.
    
        Returns
        -------
        capa : folium.Map
            Capa del mapa actualizada con los nuevos marcadores.
        """
        for index, row in dataframe.iterrows():
            punto = Point(row['COOR_GPS_LON'], row['COOR_GPS_LAT'])
            nombre = row[nombres] 
            if tipo is None:
                color_definitivo=color_asignado
                tam_definitivo =size
            else:
                color_definitivo = tipo[dataframe.at[index, 'TIPO']]['color']
                #color_definitivo = tipo[dataframe['TIPO'][row]]['color']
                tam_definitivo = tipo[dataframe.at[index,'TIPO']]['tam']
            
            # Agregar un marcador en la ubicación fija segun el tipo.
            marker =folium.RegularPolygonMarker(
                location=[punto.y, punto.x],
                number_of_sides=forma,  # Cuatro lados para hacerlo cuadrado
                radius=tam_definitivo,  # Tamaño del marcador
                color=color_contorno,  # Color del borde del marcador
                fill_color=color_definitivo,  # Color de relleno del marcador
                fill_opacity=1,  # Opacidad del relleno (1)
                rotation=rotacion  # Ajusta la rotación para que sea un cuadrado
            ).add_to(capa)
            
            # Formatear el texto del tooltip con negrita y tamaño de letra personalizado
            tooltip_text = f"<b>CODIGO:</b>{nombre}<br><b>CIRCUITO:</b>{row['CIRCUITO']}"
            tooltip = folium.Tooltip(tooltip_text, sticky=True, style="font-size: 12px")
            marker.add_child(tooltip)
        return capa
          
    #Función para dibujar marcadores tipo lineas.
    def tipo_linea(dataframe,color_linea, grosor_linea,fid_linea, capa):
        """
        Función que dibuja marcadores tipo línea en un mapa interactivo(mapa).
     
        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame que contiene la información para dibujar las líneas.
     
        color_linea : str
            Color de las líneas.
     
        grosor_linea : int
            Grosor de las líneas.
     
        fid_linea : str
            Nombre de la columna que contiene los identificadores para las líneas.
     
        capa : folium.Map
            Capa del mapa donde se agregarán las líneas.
     
        Returns
        -------
        capa : folium.Map
            Capa del mapa actualizada con las nuevas líneas.
        """
        for index, row in dataframe.iterrows():
            inicio = Point(row['X_INICIAL'], row['Y_INICIAL'])
            fin = Point(row['X_FINAL'], row['Y_FINAL'])
            fid=row[fid_linea]
            #linea = LineString([inicio, fin])
            # Agrega la línea a la capa de líneas
            
            
            tooltip_text = f"<b>CIRCUITO:</b>{row['CIRCUITO']}<br><b>FID:</b>{str(fid)}"
            tooltip = folium.Tooltip(tooltip_text, sticky=True, style="font-size: 12px")

            # Agregar la línea a la capa de líneas junto con el tooltip
            folium.PolyLine(locations=[(inicio.y, inicio.x), (fin.y, fin.x)], color=color_linea, weight=grosor_linea).add_to(capa).add_child(tooltip)
            
        return capa
    
    def agregar_marcador(row, tipo, total_aperturas, total_tiempo,aperturas,horas, capa_entrada):
        """
   Función que agrega marcadores a una capa de mapa basándose en información específica del DataFrame.

   Parameters
   ----------
   row : pd.Series
       Fila actual del DataFrame.

   tipo : str
       Tipo de marcador ('corte' o 'trafo').

   total_aperturas : int
       Total de aperturas en el conjunto de datos.

   total_tiempo : float
       Tiempo total en el conjunto de datos.

   aperturas : str
       Nombre de la columna que contiene la información de aperturas.

   horas : str
       Nombre de la columna que contiene la información de horas.

   capa_entrada : folium.Map
       Capa del mapa donde se agregarán los marcadores.

   Returns
   -------
   capa_entrada : folium.Map
       Capa del mapa actualizada con los nuevos marcadores.
   """
        punto = Point(row['COOR_GPS_LON'], row['COOR_GPS_LAT'])
        
       # Obtener la suma de aperturas y tiempo para el elemento actual
        filtro_codigo = suma_aperturas['CODIGO'] == row['CODIGO']
        apertura_actual = suma_aperturas.loc[filtro_codigo, aperturas].values[0]
        tiempo_proga = suma_aperturas.loc[filtro_codigo, 'DUR_H_PROGRAMADAS'].values[0]
        tiempo_no_progra = suma_aperturas.loc[filtro_codigo, 'DUR_H_NO_PROGRAMADAS'].values[0]
        tiempo_otros = suma_aperturas.loc[filtro_codigo, 'DUR_H_OTROS'].values[0]
        tiempo_evento = suma_aperturas.loc[filtro_codigo, 'Tiempo'].values[0]
        tiempo_elemento = (suma_aperturas.loc[filtro_codigo, horas].values[0]).round(2)
        
        apertura_progra = (suma_aperturas.loc[filtro_codigo, 'NUM_APERTURAS_PROGRAMADAS'].values[0]).astype(int) 
        apertura_no_progra = (suma_aperturas.loc[filtro_codigo, 'NUM_APERTURAS_NO_PROGRAMADAS'].values[0]).astype(int) 
        apertura_otros = (suma_aperturas.loc[filtro_codigo, 'NUM_APERTURAS_OTROS'].values[0]).astype(int) 
        apertura_evento = suma_aperturas.loc[filtro_codigo, 'Cantidad_de_veces'].values[0]
        apertura_eventos = (suma_aperturas.loc[filtro_codigo, aperturas].values[0]).astype(int) 
        
        # Obtener máximos y mínimos en cantidad de aperturas y tiempo de apertura
        max_apertura, min_apertura = suma_aperturas[aperturas].max(), suma_aperturas[aperturas].min()
        max_tiempo, min_tiempo = suma_aperturas[horas].max(), suma_aperturas[horas].min()
        
        # Calcular escalas y umbrales
        escala_apertura, escala_tiempo = (max_apertura - min_apertura) * 0.25, (max_tiempo - min_tiempo) * 0.25
        umbrales_apertura = [min_apertura + i * escala_apertura for i in range(1, 4)]
        umbrales_tiempo = [min_tiempo + i * escala_tiempo for i in range(1, 4)]
        # Asignar color según el tiempo
        color = (
            'white' if tiempo_elemento == 0
            else 'green' if tiempo_elemento <= umbrales_tiempo[0]
            else 'yellow' if umbrales_tiempo[0] < tiempo_elemento <= umbrales_tiempo[1]
            else 'orange' if umbrales_tiempo[1] < tiempo_elemento <= umbrales_tiempo[2]
            else 'red'
        )
        
        # Tamaño de los elementos según las aperturas
        if np.all(apertura_actual <= umbrales_apertura[0]):
            size = 10
        elif np.all((umbrales_apertura[0] < apertura_actual) & (apertura_actual <= umbrales_apertura[1])):
            size = 14
        elif np.all((umbrales_apertura[1] < apertura_actual) & (apertura_actual <= umbrales_apertura[2])):
            size = 15
        else:
            size = 18
        # Agregar un marcador en forma de triángulo o cuadrado en la ubicación fija
        lados = 4 if tipo == 'corte' else 3
        rotation = 45 if tipo == 'corte' else 90
    
        marker = folium.RegularPolygonMarker(
            location=[punto.y, punto.x],
            number_of_sides=lados,
            radius=size,
            color='black',
            fill_color=color,
            fill_opacity=1,
            rotation=rotation
        ).add_to(capa_entrada)
        if capa_entrada==evento_layer:
            
        
            # Presentar el texto del tooltip con negrita y tamaño de letra personalizado
            tooltip_text = f"<b>CODIGO:</b>{row['CODIGO']}<br><b>Programado:</b>{tiempo_proga} horas; {apertura_progra} apertura<br><b>No Programado:</b> {tiempo_no_progra} horas; {apertura_no_progra} apertura<br><b>Otros:</b> {tiempo_otros} horas; {apertura_otros} apertura<br><b>Por eventos:</b> {tiempo_evento} horas; {apertura_evento} apertura<br><b>Totales:</b> {tiempo_elemento} horas; {apertura_eventos} apertura" 
            tooltip = folium.Tooltip(tooltip_text, sticky=True, style="font-size: 12px")
            marker.add_child(tooltip)
        elif capa_entrada==apertura_layer:
            # Presentar el texto del tooltip con negrita y tamaño de letra personalizado
            tooltip_text = f"<b>CODIGO:</b>{row['CODIGO']}<br><b>Programado:</b>{tiempo_proga} horas; {apertura_progra} apertura<br><b>No Programado:</b> {tiempo_no_progra} horas; {apertura_no_progra} apertura<br><b>Otros:</b> {tiempo_otros} horas; {apertura_otros} apertura<br><b>Totales:</b> {tiempo_elemento} horas; {apertura_eventos} apertura" 
            tooltip = folium.Tooltip(tooltip_text, sticky=True, style="font-size: 12px")
            marker.add_child(tooltip)
        elif capa_entrada==reporte_layer:
            
            tiempo_proga = suma_aperturas.loc[filtro_codigo, 'Proga_H'].values[0]
            tiempo_no_progra = suma_aperturas.loc[filtro_codigo, 'Noprogra_H'].values[0]
            apertura_progra = (suma_aperturas.loc[filtro_codigo, 'Progra_APERTURA'].values[0]).astype(int) 
            apertura_no_progra = (suma_aperturas.loc[filtro_codigo, 'Noprogra_APERTURA'].values[0]).astype(int) 
            
            # Presentar el texto del tooltip con negrita y tamaño de letra personalizado
            tooltip_text = f"<b>CODIGO:</b>{row['CODIGO']}<br><b>Programado:</b>{tiempo_proga} horas; {apertura_progra} apertura<br><b>No Programado:</b> {tiempo_no_progra} horas; {apertura_no_progra} apertura<br><b>Totales:</b> {tiempo_evento} horas; {apertura_evento} apertura" 
            tooltip = folium.Tooltip(tooltip_text, sticky=True, style="font-size: 12px")
            marker.add_child(tooltip)
            
    #%% Graficar trayectoria
    """
    Bloque de código para graficar la trayectoria, la red MT, los elementos de corte, los transformadores, la red BT y los usuarios en un mapa interactivo.
    
    Este bloque de código llama a funciones previamente definidas para agregar diferentes capas de elementos de la red eléctrica a un mapa interactivo utilizando la biblioteca Folium.
    
    Subbloques:
    - Graficar red MT: Agrega las líneas que componen la red MT al mapa interactivo con un color específico y un grosor definido.
    - Graficar elementos de corte: Agrega marcadores de elementos de corte a la capa correspondiente del mapa interactivo con colores y tamaños específicos según el tipo de corte.
    - Graficar Transformadores: Agrega marcadores de transformadores a la capa correspondiente del mapa interactivo con un color, tamaño y forma definidos.
    - Graficar red BT: Agrega las líneas que componen la red BT al mapa interactivo con un color específico y un grosor definido.
    - Graficar usuarios: Agrega marcadores de usuarios a la capa correspondiente del mapa interactivo con un color, tamaño y forma definidos.
    
    Nota: Este bloque de código llama a funciones previamente definidas para crear diferentes capas de elementos de la red eléctrica, como líneas, puntos y transformadores, en un mapa interactivo. Cada subbloque utiliza funciones específicas para agregar los elementos correspondientes a una capa particular del mapa, con propiedades como forma, color y tamaño definidos.
    """


            
    #%%% Graficar red MT
    
    # Crear una capa para las lineas que componen la red MT
    lineas_layer = folium.FeatureGroup(name='Red MT')
    # Definir color y grosor de la línea
    color_linea='blue'
    grosor_linea=3
    # Itera a través de los datos y traza líneas en el mapa
    lineas_layer = tipo_linea(gdf, color_linea, grosor_linea,'FID', lineas_layer)
    
    #Capa de postes 

    # Crear una capa para los postes
    puntos_layer = folium.FeatureGroup(name='Postes')
    for index, row in gdf.iterrows():
        inicio = Point(row['X_INICIAL'], row['Y_INICIAL'])
        fin = Point(row['X_FINAL'], row['Y_FINAL'])
        # Agrega puntos iniciales y finales como puntos con tamaño personalizado
        folium.Circle(location=(inicio.y, inicio.x), radius=3, color='blue', fill=True, fill_color='blue').add_to(puntos_layer)
        folium.Circle(location=(fin.y, fin.x), radius=3, color='blue', fill=True, fill_color='blue').add_to(puntos_layer)
        
#%%% Graficar elementos de corte          
    
    # Crear una capa para los elementos de corte.
    corte_layer = folium.FeatureGroup(name='Elementos de Corte')
    
    # Definir un diccionario que asocie cada tipo de elemento de corte con un color y tamaño específico
    tipo_corte = {
        'S': {'color':'green', 'tam':10},
        'C': {'color':'blue', 'tam':10},
        'R': {'color':'gray','tam':10},
        'I': {'color':'purple','tam':18}
        }
    # Definir propiedades adicionales para los marcadores que representan los elementos de corte
    color_contorno='black'
    forma=4
    rotacion=45    
    color_asignado='gray'
    size=10
    # Utilizar la función tipo_punto para agregar marcadores de corte a la capa correspondiente
    tipo_corte=tipo_punto(cortes, color_asignado, size, forma, color_contorno, rotacion, 'CODIGO',corte_layer,tipo_corte)
    
#%%%Graficar Transformadores    

    # Crear una capa para los transformadores
    trafo_layer = folium.FeatureGroup(name='Transformador')
    # Definir propiedades adicionales para los marcadores que representan los transformadores
    color_asignado ='green'
    size=10
    forma=3
    rotacion=90
    # Utilizar la función tipo_punto para agregar marcadores de transformadores a la capa correspondiente
    trafo_layer=tipo_punto(trafo, color_asignado, size, forma, color_contorno, rotacion, 'CODIGO',trafo_layer)
 
#%%%Graficar red BT
    
    # Crear una capa para las lineas que componen la red BT
    red_layer = folium.FeatureGroup(name='Red BT')
    if not red_BT_result.empty:
        # Definir el color y grosor de la línea
        color_linea='#FF8C00'
        tamaña_linea=2.5
        # Utilizar la función tipo_linea para agregar las líneas de la red BT a la capa correspondiente
        red_layer = tipo_linea(red_BT_result,color_linea, grosor_linea,'G3E_FID', red_layer)
        
#%%% Graficar usuarios    
    
    #Crear una capa para agregar los usuarios
    usuario_layer=folium.FeatureGroup(name= 'Usuario')
    # Definir parámetros para los marcadores de usuario
    color_asignado ='#FF00FF'
    size=6
    forma=5
    rotacion=0  
    color_contorno='black'
    # Verificar si el DataFrame de resultados de usuarios no está vacío
    if not graf_usuario_result.empty:
        # Utilizar la función tipo_punto para agregar marcadores de usuario a la capa correspondiente
        usuario_layer=tipo_punto(graf_usuario_result, color_asignado, size, forma, color_contorno, rotacion, 'NIU', usuario_layer)
             
#%% Graficar el SDL     
    """
    Bloque de código para graficar el Sistema de Distribución Local (SDL) filtrado por la subestación en un mapa interactivo.
    
    Este bloque de código llama a funciones previamente definidas para agregar líneas del SDL, elementos de corte y transformadores a un mapa interactivo utilizando la biblioteca Folium.
    
    Subbloques:
    - Graficar líneas del SDL: Agrega las líneas del SDL al mapa interactivo con un color y un grosor específicos.
    - Graficar elementos de corte del sistema: Agrega marcadores de elementos de corte del sistema al mapa interactivo con un color, tamaño y forma definidos.
    - Graficar transformadores del sistema: Agrega marcadores de transformadores del sistema al mapa interactivo con un color, tamaño y forma definidos.
    
    Nota: Este bloque de código llama a funciones previamente definidas para crear diferentes capas de elementos del Sistema de Distribución Local (SDL), como líneas y puntos, en un mapa interactivo. Cada subbloque utiliza funciones específicas para agregar los elementos correspondientes a una capa particular del mapa, con propiedades como forma, color y tamaño definidos.
    """

    # Crear una capa para el SDL filtrado por la subestación
    sistema_layer = folium.FeatureGroup(name='SDL subestación')
    # Reemplazar valores en blanco por NaN y eliminar filas con valores NaN en la columna 'X_INICIAL'
    gdf2['X_INICIAL'] = gdf2['X_INICIAL'].replace('', pd.NA)
    gdf2 = gdf2.dropna(subset=['X_INICIAL'])
    
    # Definir parámetros para las líneas del SDL
    color_contorno='gray'
    color_linea='gray'
    grosor_linea=1.5
    # Utilizar la función tipo_linea para agregar líneas del SDL a la capa correspondiente
    sistema_layer = tipo_linea(gdf2, color_linea, grosor_linea,'FID', sistema_layer)
    
    
    # Definir parámetros para los marcadores de elementos de corte del sistema
    color_asignado='gray'
    size=8
    forma=4
    rotacion=45
    # Utilizar la función tipo_punto para agregar marcadores de elementos de corte a la capa correspondiente
    sistema_layer=tipo_punto(corte2, color_asignado, size, forma, color_contorno, rotacion, 'CODIGO',sistema_layer) 
    
    # Definir parámetros para los marcadores de transformadores del sistema
    forma=3
    # Utilizar la función tipo_punto para agregar marcadores de transformadores a la capa correspondiente
    sistema_layer=tipo_punto(trafo2, color_asignado, size, forma, color_contorno, rotacion, 'CODIGO',sistema_layer)
    
#%% Graficar por REPORTE-EVENTOS
    """
    Bloque de código para graficar elementos relacionados con el REPORTE-EVENTOS en un mapa interactivo.
    
    Este bloque de código crea tres capas en un mapa interactivo, cada una dedicada a diferentes tipos de eventos relacionados con aperturas totales y parciales.
    
    Subbloques:
    - Graficar cortes: Agrega marcadores para elementos de corte a tres capas diferentes en el mapa interactivo: aperturas totales, aperturas parciales nodo-transformador y aperturas parciales por eventos.
    - Graficar Transformadores: Agrega marcadores para transformadores a las mismas tres capas en el mapa interactivo, con el mismo propósito de mostrar aperturas totales, aperturas parciales nodo-transformador y aperturas parciales por eventos.
    
    Nota: Este bloque de código utiliza funciones previamente definidas para agregar marcadores de elementos de corte y transformadores a tres capas distintas en un mapa interactivo, con el objetivo de representar diferentes tipos de eventos relacionados con aperturas totales y parciales en un sistema de distribución eléctrica.
    """

    #Crear una capa para alamacenar los elementos de corte que conforman la trayectoria según los valores_encontrados
    evento_layer=folium.FeatureGroup(name= 'Aperturas totales')
    apertura_layer = folium.FeatureGroup(name='Aperturas parciales nodo-transformador')
    reporte_layer = folium.FeatureGroup(name='Aperturas parciales por eventos')
    
#%%% Graficar cortes    
    # Agregar marcadores segun aperturas para la DataFrame 'cortes'
    for _, row_corte in cortes.iterrows():
        agregar_marcador(row_corte, 'corte', total_aperturas, total_tiempo,'TOTAL_APERTURAS','TOTAL_H', evento_layer)
        agregar_marcador(row_corte, 'corte', total_aperturas1, total_tiempo1,'NUM_APERTURAS','DUR_H', apertura_layer)
        agregar_marcador(row_corte, 'corte', total_aperturas2, total_tiempo2,'Cantidad_de_veces','Tiempo', reporte_layer)
        
#%%% Graficar Transformadores    
    # Agregar marcadores segun aperturas para la DataFrame 'trafo'
    for _, row_trafo in trafo.iterrows():
        agregar_marcador(row_trafo, 'trafo', total_aperturas, total_tiempo,'TOTAL_APERTURAS','TOTAL_H', evento_layer)
        agregar_marcador(row_trafo, 'trafo', total_aperturas1, total_tiempo1,'NUM_APERTURAS','DUR_H', apertura_layer)
        agregar_marcador(row_trafo, 'trafo', total_aperturas2, total_tiempo2,'Cantidad_de_veces','Tiempo', reporte_layer)
    
  
#%%mapa HTML 
    """
    Bloque de código para agregar capas al mapa interactivo, incluir control de capas, guardar el mapa como un archivo HTML y abrirlo en el navegador web.
    
    Este bloque de código agrega varias capas al mapa interactivo creado anteriormente, incluyendo capas para elementos del sistema eléctrico, elementos de corte, transformadores, puntos, líneas, red BT, usuarios, reporte de eventos y aperturas. Luego, se agrega un control de capas para permitir al usuario alternar la visualización de las capas en el mapa. Posteriormente, el mapa se guarda como un archivo HTML en una carpeta específica y se abre automáticamente en el navegador web.
    
    Returns:
        bool: Devuelve True si se abre correctamente el archivo HTML del mapa en el navegador web.
    
    """ 
   
    #Agregar las capas al mapa
    sistema_layer.add_to(mapa)
    corte_layer.add_to(mapa)
    trafo_layer.add_to(mapa)
    puntos_layer.add_to(mapa)
    lineas_layer.add_to(mapa)
    red_layer.add_to(mapa)
    usuario_layer.add_to(mapa)
    reporte_layer.add_to(mapa)
    apertura_layer.add_to(mapa)
    evento_layer.add_to(mapa)
    
    # Agregar control de capas
    folium.LayerControl().add_to(mapa)
    
    carpeta_destino = '../reports/'
    # Combina la carpeta con el nombre del archivo HTML
    nombre_mapa = os.path.join(carpeta_destino, 'map_analisis_falla_' + circuito_name + '.html')
    # Obtén la ruta absoluta del archivo HTML
    ruta_absoluta = os.path.abspath(nombre_mapa)
    # Abre el archivo con el navegador web
    # Verificar si el archivo HTML ya existe  
    mapa.save(ruta_absoluta) 
    
    return webbrowser.open('file://' + ruta_absoluta, new=2)  
   
    