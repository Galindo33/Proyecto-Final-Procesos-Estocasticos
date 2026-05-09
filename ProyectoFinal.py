import pandas as pd     #LIBRERIA PARA MANIPULAR LOS DATOS
import numpy as np      #LIBRERIA PARA CALCULOS MATEMATICOS

#EXPORTAMOS LOS DATOS DEL ARCHIVO EXCEL A UN DATAFRAME
datos = pd.read_excel(r"C:\Users\sofii\Downloads\base banxico.xlsx")

#OBTENEMOS EL NUMERO DE REGISTROS Y NOMBRES DE LAS COLUMNAS
registros = len(datos)
columnas = datos.columns

#EXPLORAMOS UN POCO DE LOS DATOS
print(f"\n\tNUMERO DE REGISTROS ENCONTRADOS: {registros}")
print(f"\n\tCAMPOS ENCONTRADOS: {columnas}")

#CONVERTIMOS A VALORES NUMERICOS LAS COLUMNAS SELECCIONADAS
datos["tasa_objetivo"] = pd.to_numeric(datos["tasa_objetivo"], errors="coerce")
datos["tiie_28d"] = pd.to_numeric(datos["tiie_28d"], errors="coerce")
datos["tipo_cambio_fix"] = pd.to_numeric(datos["tipo_cambio_fix"], errors="coerce")

#IMPRIMIMOS EL NUMERO DE VALORES FALTANTES DE CADA COLUMNA
print("\n\tVALORES FALTANTES: ")
print(datos.isnull().sum())

#UTILIZAMOS LA FUNCION .interpolate PARA APROXIMAR LOS VALORES FALTANTES
#A TRAVES DE LOS VALORES CERCANOS
datos["tasa_objetivo"] = datos["tasa_objetivo"].interpolate()
datos["tiie_28d"] = datos["tiie_28d"].interpolate()
datos["tipo_cambio_fix"] = datos["tipo_cambio_fix"].interpolate()

#ELIMINAMOS LOS VALORES QUE SIGUEN SIENDO NULOS EN EL DATAFRAME
datos = datos.dropna()

#DATAFRAME DESPUES DE LIMPIAR E INTERPOLAR LOS DATOS
registros = len(datos)
columnas = datos.columns

print("\n\tESTATUS DEL DATAFRAME DESPUES DE LIMPIAR E INTERPOLAR")

print("\n\tVALORES FALTANTES: ")
print(datos.isnull().sum())

print(f"\n\tNUMERO DE REGISTROS ENCONTRADOS: {registros}")
print(f"\n\tCAMPOS ENCONTRADOS: {columnas}")


#IMPRIMIMOS LOS PRIMEROS REGISTROS DEL DATAFRAME
#Y EL TIPO DE DATO DE CADA COLUMNA
tipDat = datos.dtypes
print("\n")
print(tipDat)
print(datos.head())
