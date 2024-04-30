# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 07:43:03 2024

@author: abartolo
"""
"""
# load_data.py

Este script carga datos desde diferentes fuentes, incluyendo archivos CSV y una base de datos Oracle.

Primero, define una función para procesar la entrada y devuelve un DataFrame estructurado. Esta función
acepta diferentes tipos de entrada, como archivos Excel, listas o valores individuales.

Luego, carga los datos principales, incluyendo elementos principales, transformadores, usuarios y datos de red.
Si hay problemas de conexión a la base de datos Oracle, el script carga datos desde archivos CSV locales.
Los datos se filtran según un rango de fechas especificado.

Finalmente, se realizan algunas operaciones de limpieza y procesamiento de datos, como renombrar columnas,
dar formato a fechas y manejar valores faltantes.

"""

# Importar bibliotecas necesarias
import pandas as pd
import cx_Oracle

def procesar_entrada(entrada):
    """
    Función que procesa el valor de entrada y devuelve un DataFrame estructurado.

    Parameters
    ----------
    entrada : str, list
        Valor de entrada a procesar.

    Returns
    -------
    valor_entrada : pd.DataFrame
        DataFrame con columnas "TRANSFORMADOR" y, posiblemente, "circuito".

    Notes
    -----
    Esta función acepta diferentes tipos de entrada (archivo Excel, lista o valor individual)
    y adapta la estructura del DataFrame resultante en consecuencia.

    Ejemplos de Uso:
      - procesar_entrada("archivo.xlsx")
      - procesar_entrada([1, 2, 3])
      - procesar_entrada("123") 
    """
    # Crear un DataFrame vacío con columnas predeterminadas
    valor_entrada = pd.DataFrame(columns=["TRANSFORMADOR"])
    # Comprobar el tipo de entrada y realizar las operaciones correspondientes
    if not entrada:
        try:
            # Intentar cargar un archivo Excel cuando no se ingresa valor de entrada
            archivo_excel = "../data/raw/entrada.xlsx"
            valor_entrada = pd.read_excel(archivo_excel)
            valor_entrada['circuito'] = valor_entrada['TRANSFORMADOR'].map(trafos_original.set_index('CODIGO')['CIRCUITO'])
            # If there are still missing values, fill them using corte_original
            valor_entrada['circuito'] = valor_entrada['circuito'].fillna(valor_entrada['TRANSFORMADOR'].map(corte_original.set_index('CODIGO')['CIRCUITO']))
            # If there are still missing values, fill them using usuarios
            valor_entrada['circuito'] = valor_entrada['circuito'].fillna(valor_entrada['TRANSFORMADOR'].map(usuarios.set_index('NIU')['CIRCUITO']))
                        
            print("Procesando un archivo excel")
        except Exception as e:
            print(f"Error al cargar el archivo Excel: {e}")
    elif isinstance(entrada, list):
        print(f"Procesando lista de valores: {entrada}")
        valor_entrada["TRANSFORMADOR"] = entrada
       
    elif "," in entrada:
        # Divide la cadena en una lista de valores utilizando la coma como separador
        lista_valores = [valor.strip() for valor in entrada.split(',')]
        print(f"Procesando lista de valores: {lista_valores}")
        # Asegúrate de que la columna 'TRANSFORMADOR' contenga valores adecuadamente tipados
        for i, valor in enumerate(lista_valores):
            if valor[0].isdigit() or (valor[0] == '-' and len(valor) > 1 and valor[1].isdigit()):
                # Si el primer carácter es un dígito o un signo negativo seguido de un dígito, conviértelo a float
                lista_valores[i] = float(valor)
            else:
                # De lo contrario, déjalo como string
                lista_valores[i] = valor
    
        # Asigna la lista a la columna 'TRANSFORMADOR'
        valor_entrada['TRANSFORMADOR'] = lista_valores
        
        #valor_entrada["circuito"] =''
        # Crear la nueva columna 'CIRCUITO' en df_principal
        valor_entrada['circuito'] = valor_entrada['TRANSFORMADOR'].map(trafos_original.set_index('CODIGO')['CIRCUITO'])
        # If there are still missing values, fill them using corte_original
        valor_entrada['circuito'] = valor_entrada['circuito'].fillna(valor_entrada['TRANSFORMADOR'].map(corte_original.set_index('CODIGO')['CIRCUITO']))
        # If there are still missing values, fill them using usuarios
        valor_entrada['circuito'] = valor_entrada['circuito'].fillna(valor_entrada['TRANSFORMADOR'].map(usuarios.set_index('NIU')['CIRCUITO']))
        # Agregar guion al final si no está presente
        valor_entrada['circuito'] = valor_entrada['circuito'].astype(str).apply(lambda x: x + '-' if not x.endswith('-') else x)

    else:
        print(f"Procesando un solo valor: {entrada}")
        # Asegúrate de que la columna 'TRANSFORMADOR' contenga valores adecuadamente tipados
        if entrada.isdigit() or (entrada[0] == '-' and len(entrada) > 1 and entrada[1].isdigit()):
            # Si el valor es un dígito o un signo negativo seguido de un dígito, conviértelo a float
            valor_entrada.loc[0, "TRANSFORMADOR"] = float(entrada)
        else:
            # De lo contrario, déjalo como string
            valor_entrada.loc[0, "TRANSFORMADOR"] = entrada  
        # Crear la nueva columna 'circuito' en el DataFrame valor_entrada   
        valor_entrada['circuito'] = valor_entrada['TRANSFORMADOR'].map(trafos_original.set_index('CODIGO')['CIRCUITO'])
        valor_entrada['circuito'] = valor_entrada['circuito'].fillna(valor_entrada['TRANSFORMADOR'].map(corte_original.set_index('CODIGO')['CIRCUITO']))
        # If there are still missing values, fill them using usuarios
        valor_entrada['circuito'] = valor_entrada['circuito'].fillna(valor_entrada['TRANSFORMADOR'].map(usuarios.set_index('NIU')['CIRCUITO']))
           
    return valor_entrada


#%% Cargar datos CSV
"""
Cargar datos CSV desde archivos.

Este bloque de código carga datos desde archivos CSV ubicados en la carpeta "../data/raw/".
Se cargan los siguientes conjuntos de datos:
1. Datos de elementos principales desde el archivo "Elementos_padres.csv".
2. Datos de transformadores desde el archivo "MDE_Coordendas_Transformadores.csv".
3. Datos de usuarios desde el archivo "MDE_Coordenadas_Clientes.csv".
4. Datos de redes de baja tensión desde el archivo "MDE_Coordendas_Redes_BT.csv".
5. Datos de redes de media tensión desde el archivo "MDE_Coordendas_Red_MT.csv".
6. Datos de elementos de corte desde el archivo "MDE_Coordendas_Equipos_Corte.csv".

Los archivos CSV se cargan utilizando la biblioteca pandas. Se especifica el separador (';') y el formato decimal (',') para garantizar una carga adecuada de los datos.
Los identificadores de fila ('FID') se convierten al tipo de dato 'float64' cuando sea aplicable.

Returns
-------
- No hay valor de retorno explícito. Los conjuntos de datos cargados se almacenan en variables específicas para su posterior procesamiento.

"""

# Cargar datos de elementos principales
archivo_csv = "../data/raw/Elementos_padres.csv"     
gelemet = pd.read_csv(archivo_csv, sep=';', decimal=',')
gelemet['FID'] = gelemet['FID'].astype('float64')

# Cargar datos de transformadores
archivo3_csv = "../data/raw/MDE_Coordendas_Transformadores.csv"      
trafos_original = pd.read_csv(archivo3_csv, sep=';', decimal=',', encoding='latin-1')
trafos_original['FID'] = trafos_original['FID'].astype('float64')

# Cargar datos de usuarios
archivo4_csv = "../data/raw/MDE_Coordenadas_Clientes.csv"      
usuarios = pd.read_csv(archivo4_csv,sep=';', decimal=',')

# Cargar datos de red BT
archivo5_csv = "../data/raw/MDE_Coordendas_Redes_BT.csv"    
redes_BT = pd.read_csv(archivo5_csv,sep=';', decimal=',')

#Cargar datos de red MT
archivo2_csv = "../data/raw/MDE_Coordendas_Red_MT.csv"        
red = pd.read_csv(archivo2_csv,sep=';', decimal=',')
red['FID'] = red['FID'].astype('float64')

# Cargar datos de elementos de corte
archivo6_csv = "../data/raw/MDE_Coordendas_Equipos_Corte.csv"
corte_original=pd.read_csv(archivo6_csv,sep=';', decimal=',', encoding='latin-1')

#%% Conexión a bases de Datos

"""
Conexión a la base de datos y carga de datos desde archivos CSV.

Este bloque de código intenta establecer una conexión a una base de datos Oracle y, si la conexión falla, carga datos desde archivos CSV ubicados en la carpeta "../data/raw/".

Si la conexión a la base de datos falla, se cargan los siguientes conjuntos de datos desde archivos CSV:
1. Datos de eventos desde el archivo "ReporteEventos.csv".
2. Datos de solicitudes desde el archivo "ReporteSolicitudes.csv".
3. Datos de consulta de aperturas desde el archivo "MAR_Consulta_aperturas.csv".

Se especifica un rango de fechas (desde '2023-01-01' hasta '2023-12-04') para filtrar la información cargada desde los archivos CSV.

Los archivos CSV se cargan utilizando la biblioteca pandas. Se especifica el separador (';'), el formato decimal (',') y la codificación ('latin-1') para garantizar una carga adecuada de los datos.
Se ajustan los encabezados de las columnas y se convierten las columnas de fecha al formato datetime.

Parameters
----------
- No hay parámetros de entrada.

Returns
-------
- No hay valor de retorno explícito. Los conjuntos de datos cargados se almacenan en variables específicas para su posterior procesamiento.

"""

#Agregar un rango de fecha para filtrar la información

fecha_inicial=pd.to_datetime('2023-01-01')
fecha_final=pd.to_datetime('2024-02-22')

try:
    #Conexion MAR
    dsn_tns1=cx_Oracle.makedsn('EPM-PO35.corp.epm.com.co',1521,service_name='EPM09')
    connection=cx_Oracle.connect('DMSANALISTA','junio2009',dsn_tns1)
    
    """
    
    
    Aquí va lo de las consultas !!!!
    
    """
except cx_Oracle.DatabaseError:
    # En caso de error de conexión, cargar datos desde archivos CSV
    
    # Cargar eventos desde el archivo CSV
    eventos_csv = "../data/raw/ReporteEventos.csv"
    # Lee las primeras filas del archivo para identificar la fila que contiene la etiqueta "Evento"
    header_row = pd.read_csv(eventos_csv, sep=';', decimal=',', encoding='latin-1', nrows=50)  # Ajusta el número de filas según sea necesario
    
    # Encuentra la fila que contiene la etiqueta "Evento" en las primeras 5 columnas de manera insensible a mayúsculas y minúsculas
    fila_evento = header_row.iloc[:, :5].apply(lambda row: any('Evento' in str(cell) for cell in row), axis=1).idxmax()
    
    # Usa la fila que contiene "Evento" como fila de inicio y define esa fila como encabezado
    reporte_eventos = pd.read_csv(eventos_csv, sep=';', decimal=',', encoding='latin-1', header=fila_evento+1,low_memory=False)
    
    # Elimina las columnas que contienen solo valores nulos en todas las filas
    reporte_eventos = reporte_eventos.dropna(axis=1, how='all')
    # Se cambian los nombres de las columnas de reporte_eventos para que coincida con los de la consulta
    reporte_eventos.rename(columns={'Fecha Real de Inicio(dd/mm/aaaa)':'FEC_REALINICIO',
                                    'Fecha Energización(dd/mm/aaaa)':'TIE_ENERGIZACION',
                                    'Fecha Finalización(dd/mm/aaaa)':'FEC_REALFIN',
                                    'Causa Evento':'CAUSA_EVENTO',
                                    'Observaciones del Evento':'OBSERVACION_EVENTO',
                                    'Evento':'EVENTO',
                                    'Generación':'NOM_GENERACION'},inplace=True)

    #Dar formato de fechas a las columnas de interes 
    reporte_eventos['FEC_REALINICIO'] = reporte_eventos['FEC_REALINICIO'].str[:-4]
    reporte_eventos['FEC_REALFIN'] = reporte_eventos['FEC_REALFIN'].str[:-4]

    # Asegúrate de que ambas columnas de fecha estén en formato datetime
    reporte_eventos['FEC_REALINICIO'] = pd.to_datetime(reporte_eventos['FEC_REALINICIO'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    reporte_eventos['TIE_ENERGIZACION'] = pd.to_datetime(reporte_eventos['TIE_ENERGIZACION'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    reporte_eventos['FEC_REALFIN'] = pd.to_datetime(reporte_eventos['FEC_REALFIN'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    
    # Filtra el DataFrame para incluir solo las filas dentro del rango de fechas
    reporte_eventos =  reporte_eventos[( reporte_eventos['FEC_REALINICIO'] >= fecha_inicial) & (reporte_eventos['FEC_REALINICIO'] <= fecha_final)]
    
    if reporte_eventos.empty:
        print(f"En reporte_eventos, no se tienen valores para el rango:  {fecha_inicial}  -  {fecha_final}")
        
     # Cargar solicitudes desde el archivo CSV
    solicitudes_csv = "../data/raw/ReporteSolicitudes.csv"
    
    # Lee el archivo CSV, tomando la fila de inicio como encabezado y omitiendo las filas y columnas anteriores a la celda de inicio      
    header_row_s = pd.read_csv(solicitudes_csv, sep=';', decimal=',', encoding='latin-1', nrows=50)  # Ajusta el número de filas según sea necesario
    
    # Encuentra la fila que contiene la etiqueta "Solicitud" en las primeras 5 columnas de manera insensible a mayúsculas y minúsculas
    fila_solicitud = header_row_s.iloc[:, :5].apply(lambda row: any('Solicitud' in str(cell) for cell in row), axis=1).idxmax()
    
    # Usa la fila que contiene "Solicitud" como fila de inicio y define esa fila como encabezado
    reporte_solicitudes = pd.read_csv(solicitudes_csv, sep=';', decimal=',', encoding='latin-1', header=fila_solicitud+1).dropna(axis=1, how='all')
    reporte_solicitudes.rename(columns={'Evento':'EVENTO'},inplace=True)
    # Cargar datos de consulta_aperturas desde el archivo CSV
    consulta_csv = "../data/raw/MAR_Consulta_aperturas.csv"      
    consulta_aperturas = pd.read_csv(consulta_csv,sep=';',decimal=',',encoding='latin-1')
    
    # Se cambian los nombres de las columnas de consulta_aperturas para que coincida con los de la consulta
    consulta_aperturas.rename(columns={'COD_ELEMENTO':'CODIGO',
                                       'IDE_EVENTO':'Evento'},inplace=True)
    consulta_aperturas['DUR_H']=consulta_aperturas['DUR_H'].astype('float64')
   