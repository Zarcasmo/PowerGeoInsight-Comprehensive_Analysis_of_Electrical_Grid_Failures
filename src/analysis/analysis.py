# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 07:50:42 2024

@author: abartolo
"""
"""
#Módulo analysis.py

Este módulo contiene la función `analisis_fallas`, la cual realiza un análisis integral de fallas en un conjunto de elementos del sistema eléctrico, utilizando información proporcionada en diversos DataFrames.

La función comienza por importar las bibliotecas necesarias, cargar los datos requeridos y definir una función interna para buscar valores específicos dentro del DataFrame `gelemet`. Luego, filtra los DataFrames de elementos de corte, transformadores, red MT y usuarios según los valores encontrados con la función `buscar_valor`. A continuación, obtiene información sobre los eventos ocurridos en los elementos obtenidos y realiza el análisis de fallas.

Parameters
----------
entrada_dataframe : pd.DataFrame
    DataFrame con información de los elementos del sistema eléctrico.

reporte_eventos_filtrado : pd.DataFrame
    DataFrame con reportes de eventos filtrados.

circuito_name : str
    Nombre del circuito.

Returns
-------
None
    Esta función guarda resultados en archivos y no retorna valores.

Notes
-----
El análisis implica la búsqueda, filtrado y manipulación de datos en los DataFrames proporcionados, así como cálculos estadísticos para evaluar la duración y cantidad de aperturas asociadas a cada elemento.

Los resultados se almacenan en archivos, incluyendo reportes de eventos, información detallada y un mapa interactivo que muestra la ubicación de los elementos relacionados con las fallas.

Para detalles específicos sobre el funcionamiento interno de la función, se recomienda revisar el código fuente.

"""

# funcion_analisis_fallas.py
#Librerías necesarias
import pandas as pd  # Para manipulación y análisis de datos
import geopandas as gpd # Para trabajar con datos geoespaciales
from shapely.geometry import LineString #libreria para dibujar
import sys # Para interactuar con el sistema operativo

#llamar load_data y traer las dataframe gelemet,trafos_original,usuarios,redes_BT,red,reporte_solicitudes y consulta_aperturas
from data.load_data import gelemet,trafos_original,usuarios,redes_BT,red,reporte_solicitudes,consulta_aperturas
#Traer la dataframe corte_origonal
from data.clear_data import corte_original
#Llamar la función para graficar
from visualization.generate_map import graficar_html
# Este script debe ser invocado en el main (Main_analisis_falla) para realizar el análisis.
    
def analisis_fallas(entrada_dataframe,reporte_eventos_filtrado, circuito_name):
    """
    Función que realiza el análisis de fallas en un circuito eléctrico.

    Parameters
    ----------
    gelemet : pd.DataFrame
        DataFrame con información de los elementos del SDL.

    red : pd.DataFrame
        DataFrame con información de la red MT.

    corte_original : pd.DataFrame
        DataFrame con información de los elementos de corte.

    trafos_original : pd.DataFrame
        DataFrame con información de los transformadores.

    consulta_aperturas : pd.DataFrame
        DataFrame con consultas de aperturas.

    reporte_solicitudes : pd.DataFrame
        DataFrame con reporte de solicitudes.

    circuito_name : str
        Nombre del circuito.

    Returns
    -------
    None
        Guarda resultados en archivos y no retorna valores.

    Notes
    -----
    La función realiza un análisis integral de fallas en un conjunto de eleentos del SDL,
    utilizando la información proporcionada en los DataFrames de entrada.

    Los resultados se almacenan en archivos, incluyendo reportes de eventos, información detallada,
    y un mapa interactivo que muestra la ubicación de los elementos relacionados con las fallas.

    El análisis involucra la búsqueda de valores en DataFrames, filtrado y manipulación de datos,
    así como cálculos estadísticos para evaluar la duración y cantidad de aperturas asociadas a cada elemento.

    Para detalles específicos, revisar el código interno de la función.
    """
          
    #FUNCIÓN FID_EQUIPOS_PADRE
    def buscar_valor(valor_inicial,valor_funcion,gelemet):
        """
        Función que busca el valor de 'FID_EQUIPO_PADRE' de forma recursiva para un 'valor_funcion' dado dentro de un DataFrame 'gelemet'.
    
        Parameters
        ----------
        valor_inicial : int
            El valor para iniciar la búsqueda.
    
        valor_funcion : int
            El valor de 'FID' que se busca dentro del DataFrame.
    
        gelemet : pandas.DataFrame
            El DataFrame que contiene los datos donde se realizará la búsqueda.
    
        Returns
        -------
        valores_encontrados:list
            Una lista que contiene todos los valores encontrados de 'FID_EQUIPO_PADRE',
            comenzando desde 'valor_inicial' y siguiendo las relaciones definidas por 'FID'.
    
        Notes
        -----
        La función realiza una búsqueda recursiva en el DataFrame 'gelemet' hasta encontrar
        una coincidencia para 'valor_funcion' en la columna 'FID_EQUIPO_PADRE'.
    
        La búsqueda se detiene si se alcanza el número máximo de iteraciones (50 por defecto).
    
        Si se alcanza el número máximo de iteraciones sin encontrar una coincidencia,
        se imprime un mensaje indicando esto.
        """
        max_iteraciones=50
        valores_encontrados = [valor_inicial,valor_funcion]
        iteraciones = 0
        while iteraciones < max_iteraciones:
            # Filtrar el DataFrame por el valor actual de la función
            filtro_fid = gelemet["FID"] == valor_funcion
            # Obtener el valor en la columna 'FID_EQUIPO_PADRE'
            resultado_fid = gelemet.loc[filtro_fid, "FID_EQUIPO_PADRE"]
            if resultado_fid.empty:
                break
            
            valor_encontrado = resultado_fid.values[0]
            valores_encontrados.append(valor_encontrado)
            valor_funcion = valor_encontrado
            iteraciones += 1
        else:
            # Se ejecuta si el bucle se completa sin un break (sin encontrar una coincidencia)
            print(f"Se alcanzó el número máximo de iteraciones ({max_iteraciones}). No se encontró coincidencia.")
           
        return valores_encontrados
    
#%% Llamado a la función buscar_valor

    """
    Llamado a la función buscar_valor.
    
    Este bloque de código llama a la función buscar_valor para buscar valores específicos en varios conjuntos de datos (usuarios, trafos_original y gelemet). 
    El resultado de la búsqueda se almacena en la lista valores_encontrados, y se manejan errores para manejar los casos en los que los valores no se encuentran en ninguno de los conjuntos de datos.
    
    Parameters
    ----------
    - entrada_dataframe: DataFrame de entrada que contiene los valores a buscar en los conjuntos de datos.
    
    Returns
    -------
    - valores_encontrados: Lista que contiene los valores encontrados en los conjuntos de datos.
    - valores_no_encontrados: DataFrame que contiene los valores de entrada que no se encontraron en ningún conjunto de datos.
    
    """

    # Se llama la función buscar_valor manejando errores
    valores_encontrados = [] 
    graf_usuarios = []
    redes_BT_list = []
    
    #DataFrame para almacenar valores no encontrados en(usuarios,trafos,elementos de corte)
    valores_no_encontrados = pd.DataFrame(columns=["Valor_No_Encontrado"])
    # Iterar sobre los valores de la columna 'TRANSFORMADOR' en el conjunto de datos de entrada
    for valor in entrada_dataframe["TRANSFORMADOR"]:
        encontrado = False
        # Verificar si el valor se encuentra en el DataFrame 'usuarios'
        filtro = usuarios["NIU"] == valor
        if filtro.any():
            # Obtener la red_BT y los usuarios si valor se encuentra en 'usuarios'
            graf_usuario = usuarios.loc[usuarios["NIU"] == valor]
            nombre_trafo = usuarios.loc[filtro, "TRANSFORMADOR"] 
            nombre_trafo= nombre_trafo.values[0]
            red_BT = redes_BT.loc[redes_BT["TRANSFORMADOR"] == nombre_trafo]
            filtro_trafo=trafos_original["CODIGO"] == nombre_trafo
            resultado = trafos_original.loc[filtro_trafo, "FID_EQUIPO_PADRE"]
            valor_inicial=trafos_original.loc[filtro_trafo, "FID"]
            
            # Append DataFrames to the list
            graf_usuarios.append(graf_usuario)
            redes_BT_list.append(red_BT)
            encontrado = True
        # Verificar si el valor se encuentra en 'trafos_original'    
        elif  (trafos_original["CODIGO"] == valor).any():
            filtro= trafos_original["CODIGO"] == valor
            resultado = trafos_original.loc[filtro, "FID_EQUIPO_PADRE"]
            valor_inicial=trafos_original.loc[filtro, "FID"]
            encontrado = True
        # Verificar si el valor se encuentra en 'gelemet'    
        else:
            filtro = gelemet["EQUIPO_CORTE"] == valor
            resultado = gelemet.loc[filtro, "FID_EQUIPO_PADRE"]
            valor_inicial=gelemet.loc[filtro, "FID"]
            encontrado = True
            
        # Verificar si el valor fue encontrado en alguna de las condiciones
        if encontrado:
            if not resultado.empty:
                valor_funcion = resultado.values[0]
                valor_inicial = valor_inicial.values[0]
    
                # Extend the results directly to the same list
                valores_encontrados += buscar_valor(valor_inicial, valor_funcion, gelemet)
                valores_encontrados.pop()  # Assuming you still want to remove the last element
            else:
            
                # Almacenar el valor no encontrado en el DataFrame valores_no_encontrados
                valores_no_encontrados = pd.concat([valores_no_encontrados, pd.DataFrame({"Valor_No_Encontrado": [valor]})], ignore_index=True)
    # Verificar si no se encontraron valores en ninguna iteración
    if not valores_encontrados:
        print("No se encontraron valores en ninguna iteración. Deteniendo la ejecucion.")
        sys.exit()  # Detener la ejecución del script
    
    # Elimina duplicados de la lista
    valores_encontrados = list(set(valores_encontrados))
    
#%% DF para graficar la trayactoria
    """
    Creación de GeoDataFrames para graficar la trayectoria de los elementos.
    
    Este bloque de código obtiene los GeoDataFrames para los elementos asociados a los FID obtenidos con buscar_valor. 
    
    """

    # Filtrar toda la DataFrame por los valores
    resultado_filtrado = gelemet.loc[gelemet["FID_EQUIPO_PADRE"].isin(valores_encontrados)]
    
    df_combinado = pd.merge(resultado_filtrado, red, on="FID", how='left')   
    
    # Crea una nueva columna 'geometry' que contiene objetos LineString a partir de las coordenadas iniciales y finales.
    df_combinado['geometry'] = df_combinado.apply(lambda row: LineString([(row['X_INICIAL'], row['Y_INICIAL']), (row['X_FINAL'], row['Y_FINAL'])]), axis=1)
    
    # Convierte el DataFrame en un GeoDataFrame y define el sistema de referencia espacial (CRS) si es necesario
    gdf = gpd.GeoDataFrame(df_combinado, geometry='geometry', crs="EPSG:4326")

    gdf['X_INICIAL'] = gdf['X_INICIAL'].replace('', pd.NA)
    # Eliminar filas con valores NaN en la columnas
    gdf = gdf.dropna(subset=['X_INICIAL'])
    
    #Filtrar las coordenadas de los elementos de corte con la lista de valores encontrados
    cortes = corte_original.loc[corte_original["FID"].isin(valores_encontrados)]
    
    #Filtrar las coordenadas de los transformadores con la lista de valores encontrados
    trafo=trafos_original.loc[trafos_original["FID"].isin(valores_encontrados)]
    
    #PROCEDIMIENTO PARA LA RED_BT
    # Concatenar DataFrames acumulados para graf_usuario y redes_BT si las listas no están vacías
    graf_usuario_result = pd.concat(graf_usuarios) if graf_usuarios else pd.DataFrame()
    red_BT_result = pd.concat(redes_BT_list) if redes_BT_list else pd.DataFrame()
        
    # Verificar si red_BT_result no es un DataFrame vacío antes de aplicar transformaciones
    if not red_BT_result.empty:
        red_BT_result['geometry'] = red_BT_result.apply(lambda row: LineString([(row['X_INICIAL'], row['Y_INICIAL']), (row['X_FINAL'], row['Y_FINAL'])]), axis=1)
        # Convert the DataFrame to a GeoDataFrame and define the spatial reference system (CRS) if necessary.
        red_BT_result = gpd.GeoDataFrame(red_BT_result, geometry='geometry', crs="EPSG:4326")
       
#%% Búsqueda y filtrado de elementos por subestación.

    """
    Este bloque de código realiza la búsqueda y filtrado de elementos relacionados con una subestación específica, identificada por los valores encontrados en la lista valores_encontrados.
    Se filtran los elementos de gelemet, elementos de corte (corte_original) y transformadores (trafos_original) relacionados con la subestación actual.
    Luego, se combinan estos resultados con los datos de la red (red) para crear un GeoDataFrame que contenga la información relevante para la subestación.
    
    Parameters
    ----------
    - valores_encontrados: Lista que contiene los valores encontrados en los conjuntos de datos (gelemet, corte_original, trafos_original).
    
    Returns
    -------
    - gdf2: GeoDataFrame que contiene los datos filtrados y combinados para los elementos relacionados con la subestación.
    - corte2: DataFrame que contiene los datos de elementos de corte relacionados con la subestación.
    - trafo2: DataFrame que contiene los datos de transformadores relacionados con la subestación.
    """
    # Filtrar por la subestación
    subestaciones = []
    resultado_red = pd.DataFrame()  # Crear un DataFrame vacío para acumular resultados
    corte = pd.DataFrame()
    trafos= pd.DataFrame()
    for subestacion_id in valores_encontrados:
        #Obtener el código de la subestación a partir del DataFrame de los elementos de corte.
        codigo_subestacion = corte_original.loc[corte_original["FID"] == subestacion_id, "CODIGO"].values
        # Verificar si se encontró un código de subestación y si está presente en la columna 'CIRCUITO' de corte_original
        if len(codigo_subestacion) > 0 and codigo_subestacion[0] in corte_original["CIRCUITO"].values:
            codigo_subestacion = codigo_subestacion[0]
            # Filtra los elementos de gelemet relacionados con la subestación actual
            resultado_subestacion_temp = gelemet.loc[gelemet["CIRCUITO"].astype(str).str[:3] == codigo_subestacion[:3]]
            # Filtrar los elementos de corte y transformadores relacionados con la subestación actual
            corte__temp=corte_original.loc[corte_original["CIRCUITO"].astype(str).str[:3]==codigo_subestacion[:3]]
            trafos_temp=trafos_original.loc[trafos_original["CIRCUITO"].astype(str).str[:3]==codigo_subestacion[:3]]
            
            # Concatenar los resultados a los DataFrames acumulados
            resultado_red = pd.concat([resultado_red, resultado_subestacion_temp], ignore_index=True)
            corte= pd.concat([ corte, corte__temp], ignore_index=True)
            trafos= pd.concat([trafos, trafos_temp], ignore_index=True)
            subestaciones.append(codigo_subestacion)
            # Ahora, 'subestaciones' contiene las subestaciones encontradas, y 'resultado_red' contiene el DataFrame acumulado
    
    
    # Filtrar la DataFrame  de la red MT por los valores encontrados
    resultado_filtrado2 = resultado_red.loc[~resultado_red["FID_EQUIPO_PADRE"].isin(valores_encontrados)]
    
    # Realizar la combinación de datos con el DataFrame 'red'
    df_combinado2 = pd.merge(resultado_filtrado2, red, on="FID", how='left')   
    # Crear la columna 'geometry' con objetos LineString a partir de las coordenadas iniciales y finales
    df_combinado2['geometry'] = df_combinado2.apply(lambda row: LineString([(row['X_INICIAL'], row['Y_INICIAL']), (row['X_FINAL'], row['Y_FINAL'])]), axis=1)
    # Convierte el DataFrame en un GeoDataFrame y define el sistema de referencia espacial (CRS) si es necesario.
    gdf2 = gpd.GeoDataFrame(df_combinado2, geometry='geometry', crs="EPSG:4326")
    
    # Filtrar la DataFrame  de los elementos de corte por los valores encontrados
    corte2 = corte.loc[~corte["FID"].isin(valores_encontrados)]
    # Filtrar la DataFrame  de los transformadores por los valores encontrados
    trafo2=trafos.loc[~trafos["FID"].isin(valores_encontrados)]                  
    
#%% Aperturas nodo-transformador
    """
    Consulta y procesamiento de aperturas de elementos.
    
    Este bloque de código realiza un procesamiento de aperturas(nodo-trasformador) para los elementos de la red eléctrica, utilizando información de los DataFrames trafo, cortes, y consulta_aperturas.
    
    Se crea un DataFrame 'info' que contiene los valores encontrados. Luego, se realizan operaciones de combinación y fusión de datos para obtener información detallada sobre los eventos de apertura de los elementos.
    Finalmente, se realizan filtrados por tipo de evento y se calcula la suma de aperturas y tiempo para cada elemento.
    
   Parameters
   ----------
    - valores_encontrados: Lista que contiene los valores encontrados en los conjuntos de datos (trafo, cortes, consulta_aperturas).
    - circuito_name: Nombre del circuito para incluir en el nombre del archivo de salida.
    
    Returns
    -------
    - aperturas_total: DataFrame que contiene la información filtrada y procesada de los eventos de apertura.
    - programadas: DataFrame que contiene las aperturas programadas.
    - no_programadas: DataFrame que contiene las aperturas no programadas.
    - otros: DataFrame que contiene los eventos que no pertenecen a las categorías anteriores.
    - suma_aperturas: DataFrame que contiene la suma de aperturas y tiempo para cada elemento.
    """
    
    info = pd.DataFrame()
    # Agrega la lista como una nueva columna llamada 'FID'
    info['FID'] = valores_encontrados
    
    # Merge de los DataFrames usando la columna 'FID' y seleccionar solo la columna 'CODIGO_trafo'
    resultado_trafo = pd.merge(info, trafo[['FID', 'CODIGO']], on='FID', how='left')
    
    # Merge de los DataFrames usando la columna 'FID' y seleccionar solo la columna 'CODIGO_cortes'
    resultado_cortes = pd.merge(info, cortes[['FID', 'CODIGO']], on='FID', how='left')
    
    # Combinar las columnas 'CODIGO' de resultado_trafo y resultado_cortes
    elementos = resultado_trafo.set_index('FID').combine_first(resultado_cortes.set_index('FID')).reset_index()
    
    # Merge de los DataFrames usando la columna 'CODIGO' y Llenar los valores nulos con cero
    cortes_eventos = (pd.merge(cortes, consulta_aperturas, on='CODIGO', how='left')).fillna(0)
    
    # Merge de los DataFrames usando la columna 'CODIGO' y Llenar los valores nulos con cero
    trafo_eventos = (pd.merge(trafo, consulta_aperturas, on='CODIGO', how='left')).fillna(0)
    
    if not cortes_eventos['CODIGO'].isin(trafo_eventos['CODIGO']).any():
        # Si no está presente, agregar la fila
        aperturas_total = pd.concat([cortes_eventos, trafo_eventos], ignore_index=True)
        
    aperturas_total['Evento'] = aperturas_total['Evento'].astype(int)    
    name_excel= '../data/processed/consulta_apertura_filtrada_' + circuito_name + '.xlsx'
    aperturas_total.to_excel(name_excel)
    #Filtrar reporte_eventos_filtrado por el circuito
    #----------
    # Eliminar el guion al final
    circuito_filtro = circuito_name.rstrip('-')
    reporte_eventos_filtrado=reporte_eventos_filtrado[reporte_eventos_filtrado['Circuito']==circuito_filtro]
    
    evento_funcion= '../data/processed/eventos_funcion_' + circuito_name + '.xlsx'
    reporte_eventos_filtrado.to_excel(evento_funcion)        
    
    #Filtrar por tipo de evento.
    programadas = aperturas_total.loc[aperturas_total["IDE_CODIGO_CLASE"] == 'Interrupciones Programadas no Excluibles']
    
    no_programadas = aperturas_total.loc[aperturas_total['IDE_CODIGO_CLASE'] == 'Interrupciones No Programadas no Excluibles']
    
    # Filtrar "otros" que no pertenecen a las dos clases anteriores
    otros = aperturas_total.loc[~((aperturas_total["IDE_CODIGO_CLASE"] == 'Interrupciones Programadas no Excluibles') | (aperturas_total['IDE_CODIGO_CLASE'] == 'Interrupciones No Programadas no Excluibles'))]
    
    # Calcular la suma de aperturas y tiempo para cada elemento
    suma_aperturas = aperturas_total.groupby('CODIGO').agg({
        'NUM_APERTURAS': 'sum',
        'DUR_H': 'sum',
        'Evento': lambda x: list(x)
    }).reset_index()
    
#%% Aperturas reporteEventos 
    """
    Procesamiento de aperturas y generación de informes.
    
    Este bloque de código realiza el procesamiento de aperturas y genera informes a partir de los datos de los eventos reportados y los elementos de la red eléctrica. Se llevan a cabo diversas operaciones de filtrado, combinación y cálculo para obtener estadísticas detalladas sobre las aperturas de los elementos. Finalmente, se genera un informe en formato Excel que contiene la información procesada.
    
    Parameters:
    - reporte_eventos_filtrado: DataFrame que contiene los eventos reportados con información filtrada.
    - elementos: DataFrame que contiene los elementos de la red eléctrica.
    - aperturas_total: DataFrame que contiene información detallada sobre las aperturas de los elementos.
    - programa_duracion: Duración de las aperturas programadas.
    - no_programa_duracion: Duración de las aperturas no programadas.
    - otros_duracion: Duración de las aperturas de otros tipos.
    - programa_aperturas: Número de aperturas programadas.
    - no_programa_aperturas: Número de aperturas no programadas.
    - otros_aperturas: Número de aperturas de otros tipos.
    - circuito_name: Nombre del circuito para incluir en los nombres de archivo de salida.
    
    Returns:
    - suma_aperturas: DataFrame que contiene información consolidada sobre las aperturas de los elementos.
    - mapa: Resultado de la función para generar un mapa HTML.
    
    Nota: Para obtener detalles específicos sobre la estructura de los DataFrames y las operaciones realizadas, se recomienda revisar el código fuente directamente.
    """

    # Convertir tanto la columna de texto como las palabras a mayúsculas
    reporte_eventos_filtrado['OBSERVACION_EVENTO'] = reporte_eventos_filtrado['OBSERVACION_EVENTO'].apply(lambda x: str(x).upper() if pd.notnull(x) else '')  # Convertir a cadena y luego a mayúsculas
    elementos['CODIGO'] = elementos['CODIGO'].str.upper()
    
    # Reemplazar celdas vacías en 'OBSERVACION_EVENTO' con valor NA
    reporte_eventos_filtrado['OBSERVACION_EVENTO'] = reporte_eventos_filtrado['OBSERVACION_EVENTO'].replace('', pd.NA)
    # Eliminar filas con valores NaN en 'OBSERVACION_EVENTO'
    reporte_eventos_filtrado = reporte_eventos_filtrado.dropna(subset=['OBSERVACION_EVENTO'])
    
    # Obtener las filas de reporte_eventos que no se encuentran en consulta_aperturas
    filas_no_encontradas_filtrada = reporte_eventos_filtrado[~reporte_eventos_filtrado['EVENTO'].isin(aperturas_total['Evento'])]
    
    # Verificar si los valores de la columna "Evento" en filas_no_encontradas de reporte_eventos están en reporte_solicitudes
    resultado = filas_no_encontradas_filtrada['EVENTO'].isin(reporte_solicitudes['EVENTO'])
    
    # Filtrar las filas no encontradas
    filas_no_encontradas_filtrada = filas_no_encontradas_filtrada[resultado]
    
    # Crear una lista de palabras a buscar, eliminando valores nulos (NaN)
    palabras_a_buscar = elementos['CODIGO'].dropna().tolist()
    
    # Inicializar una nueva columna 'Cantidad_de_veces' en la DataFrame elementos
    elementos['Cantidad_de_veces'] = 0
    
    # Agregar una nueva columna 'Tiempo' en la DataFrame elementos
    elementos['Tiempo'] = 0.0
    
    #Clasificación del tipo de evento que sale de reporte eventos
    elementos['Proga_H'] = 0.0
    elementos['Noprogra_H'] = 0.0
    elementos['Progra_APERTURA'] = 0
    elementos['Noprogra_APERTURA'] = 0
    
    
    # Crear una nueva columna en filas_no_encontradas para almacenar el CODIGO
    filas_no_encontradas_filtrada['CODIGO'] = None
    # Inicializar la columna 'Eventos' en la DataFrame elementos
    elementos['Eventos'] = elementos['CODIGO'].apply(lambda palabra: [])
    
    # Rastrear las palabras que ya se han encontrado en el mismo texto
    palabras_encontradas = set()
      
    # Inicializar una nueva columna 'Texto_encontrado' en la DataFrame de texto
    filas_no_encontradas_filtrada['Texto_encontrado'] = False
    
    # Buscar coincidencias y actualizar la cantidad de veces y la información deseada
    for palabra in palabras_a_buscar:
        for i, fila in filas_no_encontradas_filtrada.iterrows():
            # Verificar si la palabra está presente en la observación del evento y no se ha marcado como encontrada
            if not fila['Texto_encontrado'] and pd.notna(fila['OBSERVACION_EVENTO']) and palabra in fila['OBSERVACION_EVENTO']:
                # Obtener el índice de la fila correspondiente en elementos
                indice_elementos = elementos.index[elementos['CODIGO'] == palabra].tolist()
                # Verificar si se encontró el CODIGO en elementos
                if len(indice_elementos) > 0:
                    # Obtener el CODIGO y actualizar la fila en filas_no_encontradas
                    codigo_encontrado = elementos.loc[indice_elementos[0], 'CODIGO']
                    filas_no_encontradas_filtrada.at[i, 'CODIGO'] = codigo_encontrado
                
                # Obtener las fechas del reporte_eventos
                tiempo_inicial = fila['FEC_REALINICIO']
                tiempo_final = fila['TIE_ENERGIZACION']
            
                # Verificar y utilizar la columna 'Fecha Finalizacion(dd/mm/aaaa)' si 'Fecha Finalizacion(dd/mm/aaaa)' es NaN
                if pd.isna(tiempo_final):
                    tiempo_final = fila['FEC_REALFIN']
                
                # Calcular la resta entre tiempo_final y tiempo_inicial
                tiempo_resta = (tiempo_final - tiempo_inicial).total_seconds()
                tiempo_resta= tiempo_resta / 3600
                
                # Actualizar la columna 'Tiempo' en elementos con la resta calculada
                elementos.loc[elementos['CODIGO'] == palabra, 'Tiempo'] += tiempo_resta
                
                # Actualizar la columna 'Cantidad_de_veces'
                elementos.loc[elementos['CODIGO'] == palabra, 'Cantidad_de_veces'] += 1
                
                # Actualizar la columna 'Eventos'
                elementos.loc[elementos['CODIGO'] == palabra, 'Eventos'].iat[0].extend([fila['EVENTO']])
                
                # Marcar el texto como encontrado
                filas_no_encontradas_filtrada.at[i, 'Texto_encontrado'] = True
                # Verificar la condición en 'CAUSA_EVENTO'
                if fila['CAUSA_EVENTO'] in ["Falla en Redes de Distribución", "Falla instalación prepago","Solicitud particular","Corte y Reconexión"]:
                    # Actualizar las columnas 'Noprogra_H' y 'Noprogra_APERTURA' en elementos
                    elementos.loc[elementos['CODIGO'] == palabra, 'Noprogra_H'] += tiempo_resta
                    elementos.loc[elementos['CODIGO'] == palabra, 'Noprogra_APERTURA'] += 1
                elif fila['CAUSA_EVENTO'] in ["Solicitud de Otras Dependencias", "Solicitud de Subestaciones y Líneas"]:
                    # Verificar si 'Generacion' es igual a "PROGRAMADA"
                    if fila['NOM_GENERACION'] == "PROGRAMADA":
                        # Si es PROGRAMADA, actualizar 'Proga_H' y 'Progra_APERTURA'
                        elementos.loc[elementos['CODIGO'] == palabra, 'Proga_H'] += tiempo_resta
                        elementos.loc[elementos['CODIGO'] == palabra, 'Progra_APERTURA'] += 1
                    else:
                        # Si no es PROGRAMADA, actualizar 'Noprogra_H' y 'Noprogra_APERTURA'
                        elementos.loc[elementos['CODIGO'] == palabra, 'Noprogra_H'] += tiempo_resta
                        elementos.loc[elementos['CODIGO'] == palabra, 'Noprogra_APERTURA'] += 1
                else:
                    # Si no cumple las condiciones anteriores, actualizar 'Proga_H' y 'Progra_APERTURA'
                    elementos.loc[elementos['CODIGO'] == palabra, 'Proga_H'] += tiempo_resta
                    elementos.loc[elementos['CODIGO'] == palabra, 'Progra_APERTURA'] += 1
    
    # DataFrame que contiene los eventos y el CODIGO del elemento asociado a dicho evento.
    name_excel = '../data/processed/reporte_eventos_' + circuito_name + '.xlsx'
    filas_no_encontradas_filtrada.to_excel(name_excel)
    
    # Combinar los DataFrames usando la columna 'CODIGO' como llave
    suma_aperturas = pd.merge(suma_aperturas, elementos[['CODIGO', 'Cantidad_de_veces', 'Tiempo','Eventos', 'Proga_H', 'Noprogra_H', 'Progra_APERTURA', 'Noprogra_APERTURA']], on='CODIGO', how='left')
    
    # Combinar las listas de eventos en una sola columna 'Eventos'
    suma_aperturas['Eventos'] = suma_aperturas.apply(lambda row: row['Evento'] + row['Eventos'], axis=1)
    
    # Eliminar las columnas 'Evento' y 'Eventos'
    suma_aperturas = suma_aperturas.drop(['Evento'], axis=1)
    
    # Sumar las columnas 'NUM_APERTURAS' y 'Cantidad_de_veces' y guardar el resultado como una nueva columna 'suma_aperturas'
    suma_aperturas['TOTAL_APERTURAS'] = suma_aperturas['NUM_APERTURAS'] + suma_aperturas['Cantidad_de_veces']
    
    # Sumar las columnas 'DUR_H' y 'Tiempo' y guardar el resultado como una nueva columna 'suma_aperturas'
    suma_aperturas['TOTAL_H'] = suma_aperturas['DUR_H'] + suma_aperturas['Tiempo']
    
    # Calcular el total de aperturas
    total_aperturas = suma_aperturas['NUM_APERTURAS'].sum()+suma_aperturas['Cantidad_de_veces'].sum()
    total_aperturas1=suma_aperturas['NUM_APERTURAS'].sum()
    total_aperturas2=suma_aperturas['Cantidad_de_veces'].sum()
    #Calcular el tiempo total
    total_tiempo = suma_aperturas['DUR_H'].sum()+suma_aperturas['Tiempo'].sum()
    total_tiempo1=suma_aperturas['DUR_H'].sum()
    total_tiempo2=suma_aperturas['Tiempo'].sum()
    
    # Calcular la suma de tiempo para cada CODIGO en cada subconjunto
    suma_tiempo = programadas.groupby('CODIGO')['DUR_H'].sum().reset_index()
    suma_tiempo_2 = no_programadas.groupby('CODIGO')['DUR_H'].sum().reset_index()
    suma_tiempo_3 =otros.groupby('CODIGO')['DUR_H'].sum().reset_index()
    
    # Calcular la suma de las aperturas segun el tipo_(programado;no programado;otros).
    
    suma_apertura = programadas.groupby('CODIGO')['NUM_APERTURAS'].sum().reset_index()
    suma_apertura_2 = no_programadas.groupby('CODIGO')['NUM_APERTURAS'].sum().reset_index()
    suma_apertura_3 = otros.groupby('CODIGO')['NUM_APERTURAS'].sum().reset_index()
    
    # Convertir la columna 'NUM_APERTURAS' a tipo int
    suma_aperturas['NUM_APERTURAS'] = suma_aperturas['NUM_APERTURAS'].astype(int)
    
    # Fusionar las sumas de tiempo con suma_aperturas
    suma_aperturas = pd.merge(suma_aperturas, suma_tiempo, on='CODIGO', how='left', suffixes=('', '_PROGRAMADAS'))
    suma_aperturas = pd.merge(suma_aperturas, suma_tiempo_2, on='CODIGO', how='left', suffixes=('', '_NO_PROGRAMADAS'))
    suma_aperturas = pd.merge(suma_aperturas, suma_tiempo_3, on='CODIGO', how='left', suffixes=('', '_OTROS'))
    
    suma_aperturas = pd.merge(suma_aperturas, suma_apertura, on='CODIGO', how='left', suffixes=('', '_PROGRAMADAS'))
    suma_aperturas = pd.merge(suma_aperturas, suma_apertura_2, on='CODIGO', how='left', suffixes=('', '_NO_PROGRAMADAS'))
    suma_aperturas = pd.merge(suma_aperturas, suma_apertura_3, on='CODIGO', how='left', suffixes=('', '_OTROS'))
    
    # Rellenar NaN con ceros en el DataFrame suma_aperturas
    # Redondear todos los valores a dos decimales
    suma_aperturas = (suma_aperturas.fillna(0)).round(2)
    #Guardar la informacion de interes
    name_excel = '../data/processed/informacion_' + circuito_name + '.xlsx'
    suma_aperturas.to_excel(name_excel)
    mapa=graficar_html(gdf,cortes,trafo,gdf2,corte2,trafo2,red_BT_result,graf_usuario_result,total_aperturas,total_aperturas1,total_aperturas2,total_tiempo,total_tiempo1,total_tiempo2,suma_aperturas,circuito_name)        