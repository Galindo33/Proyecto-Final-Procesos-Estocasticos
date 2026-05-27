import pandas as pd     #LIBRERIA PARA MANIPULAR LOS DATOS
import numpy as np      #LIBRERIA PARA CALCULOS MATEMATICOS
from scipy.stats import poisson   
import matplotlib.pyplot as plt
import seaborn as sns

#FUNCION QUE CONTIENE EL ALGORITMO DE POISSON
def modelo_poisson(df, columna, umbral):

    # CREAR UNA COPIA DE LOS DATOS PARA NO MODIFICAR EL DF ORIGINAL
    datos = df.copy()

    # CALCULAR CAMBIOS
    datos["cambio"] = datos[columna].diff()

    # ELIMINAR NaN GENERADO POR diff()
    datos = datos.dropna(subset=["cambio"])

    # DEFINIR EVENTOS RESPECTO AL UMBRAL DE CAMBIO
    datos["evento"] = abs(datos["cambio"]) > umbral

    # CALCULAR LAMBDA "PROMEDIO DE EVENTOS POR UNIDAD DE TIEMPO" 
    lambda_poisson = datos["evento"].sum() / len(datos)

    print(f"\n\tLAMBDA ESTIMADO: {lambda_poisson}")

    return lambda_poisson, datos


#FUNCION QUE CONTIENE EL ALGORITMO DE MARKOV
def cadena_markov(df, columna):
    
    # CREAR UNA COPIA DE LOS DATOS PARA NO MODIFICAR EL DF ORIGINAL
    datos = df.copy()

    # CALCULAR DIFERENCIAS ENTRE REGISTROS CONSECUTIVOS
    datos["cambio"] = datos[columna].diff()

    # FUNCION PARA DEFINIR ESTADOS
    def obtener_estado(valor):
        if valor > 0:
            return "Sube"
        elif valor < 0:
            return "Baja"
        else:
            return "Igual"

    # APLICAR CLASIFICACION DE ESTADOS
    datos["estado"] = datos["cambio"].apply(obtener_estado)

    # CREAR COLUMNA DEL SIGUIENTE ESTADO
    datos["estado_siguiente"] = datos["estado"].shift(-1)

    # ELIMINAR FILAS CON NaN
    datos = datos.dropna(subset=["estado", "estado_siguiente"])

    # CONSTRUIR MATRIZ DE TRANSICION
    matriz = pd.crosstab(
        datos["estado"],
        datos["estado_siguiente"],
        normalize="index"
    )

    return matriz



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

#APLICACION DEL METODO 

#CADENAS DE MARKOV
#LOS RESULTADOS DE LA MATRIZ NOS DICEN QUE TAN PROBABLE ES LLEGAR A CIERTO ESTADO
#DEPENDIENDO DE EL ESTADO EN CUAL NOS ENCONTREMOS
matriz_markov = cadena_markov(datos, "tipo_cambio_fix")
print("\n\t MATRIZ DE TRANSICION")
print("\n\t", matriz_markov)

#POISSON 
#EL RESULTADO NOS DICE CUANTOS EVENTOS SIGNIFICATIVOS OCURREN AL DIA EN PROMEDIO
#UTILIZANDO COMO REFERENCIA UN UMBRAL DE 0.20
lambda_poisson, datos_con_eventos = modelo_poisson(datos, "tipo_cambio_fix", 0.20)

#EL RESULTADO NOS DICE QUE PROBABILIDAD HAY DE QUE OCURRAN X NUMERO DE 
#EVENTOS EN DETERMINADO INTERVALO DE TIEMPO
#PROBABILIDAD DE QUE OCURRAN 3 EVENTOS EN 10 DIAS, EN ESTE CASO.
probabilidad = poisson.pmf(3, mu=lambda_poisson * 10)
print("\n\t", probabilidad)


# =======================================================
# --- BLOQUE DE GENERACIÓN GRÁFICA DE LA SIMULACIÓN ---
# =======================================================
print("\n\tGenerando gráficos estocásticos... Por favor espera un momento.")

# Preparamos un lienzo con dos gráficas paralelas
plt.figure(figsize=(16, 7))

# --- GRÁFICA 1: HISTÓRICO Y EVENTOS POISSON ---
# Usamos un subplot (1 fila, 2 columnas, esta es la número 1)
plt.subplot(1, 2, 1)

# Dibujamos la línea de tiempo del tipo de cambio (azul)
plt.plot(datos.index, datos["tipo_cambio_fix"], label="TIEFIX Banxico", color="royalblue", alpha=0.6, linewidth=1.5)

# Filtramos los datos que sí fueron eventos Poisson (salto > 0.20)
eventos = datos_con_eventos[datos_con_eventos["evento"] == True]

# Marcamos los eventos con puntitos rojos (dispersión)
plt.scatter(eventos.index, eventos["tipo_cambio_fix"], color="red", label="Saltos Significativos (> 0.20 MXN)", s=20, zorder=5)

# Títulos y ejes
plt.title("Evolución del Tipo de Cambio y Eventos de Poisson Detectados")
plt.xlabel("Registros (Tiempo)")
plt.ylabel("Precio del Dólar (MXN)")
plt.legend(loc="upper left")
plt.grid(True, alpha=0.3)


# --- GRÁFICA 2: MAPA DE CALOR DE MARKOV ---
# Usamos el subplot número 2
plt.subplot(1, 2, 2)

# Usamos Seaborn para crear un mapa de calor (heatmap) estético de la matriz
# annot=True pone los números decimales, cmap='YlGnBu' es el estilo de color (amarillo-verde-azul)
sns.heatmap(matriz_markov, annot=True, cmap="YlGnBu", fmt=".4f", cbar=True, square=True)

# Títulos y ejes
plt.title("Mapa de Calor: Matriz de Transición de Estados (Cadenas de Markov)")
plt.ylabel("Estado Actual ($X_t$)")
plt.xlabel("Estado Siguiente ($X_{t+1}$)")


# Asegurar que se acomoden bien los elementos y títulos
plt.tight_layout()  

# !!! COMANDO MÁS IMPORTANTE !!! Muestra la ventana y pausa el programa para que no se cierre
print("\n\t[GRÁFICOS LISTOS] Se ha abierto una ventana con los gráficos estocásticos.")
plt.show(block=True)