# 1.LIBRERIAS
import pickle

import pandas as pd

# 1.CARGA DATOS
ruta_proyecto = "C:/Users/Francisco/OneDrive/DATA_SCIENCE_MASTERY/03_MACHINE_LEARNING/08_CASOS/07_PERDIDA_ESPERADA"
nombre_fichero_datos = "validacion.csv"
ruta_completa = ruta_proyecto + "/02_Datos/02_Validacion/" + nombre_fichero_datos
df = pd.read_csv(ruta_completa, index_col=0)


# 3.VARIABLES Y REGISTROS FINALES
variables_finales = [
    "ingreso_mes",
    "gasto_mes",
    "activos",
    "pasivos",
    "antiguedad_empleo",
    "vivienda",
    "num_hipotecas",
    "porc_tarjetas_75p",
    "score_credito",
    "proposito_credito",
    "principal",
    "numero_cuotas",
    "interes",
    "cuota",
    "impago",
    "amortizado",
    "recuperada",
]

df.drop_duplicates(inplace=True)

df = df[variables_finales]

df = df.fillna(0)

# 4.FUNCIONES DE SOPORTE


def calidad_datos(temp):
    for column in temp.select_dtypes("number").columns:
        temp[column] = temp[column].fillna(0)
    return temp


def creacion_variables(df):
    temp = df.copy()
    return temp


# 4.CALIDAD Y CREACION DE VARIABLES
x_pd = creacion_variables(calidad_datos(df))
x_ead = creacion_variables(calidad_datos(df))
x_lgd = creacion_variables(calidad_datos(df))


# 5.CARGA PIPES DE EJECUCION
ruta_pipe_ejecucion_pd = ruta_proyecto + "/04_Modelos/pipe_ejecucion_pd.pickle"
ruta_pipe_ejecucion_ead = ruta_proyecto + "/04_Modelos/pipe_ejecucion_ead.pickle"
ruta_pipe_ejecucion_lgd = ruta_proyecto + "/04_Modelos/pipe_ejecucion_lgd.pickle"

with open(ruta_pipe_ejecucion_pd, mode="rb") as file:
    pipe_ejecucion_pd = pickle.load(file)

with open(ruta_pipe_ejecucion_ead, mode="rb") as file:
    pipe_ejecucion_ead = pickle.load(file)

with open(ruta_pipe_ejecucion_lgd, mode="rb") as file:
    pipe_ejecucion_lgd = pickle.load(file)


# 6.EJECUCION
scoring_pd = pipe_ejecucion_pd.predict_proba(x_pd)[:, 1]
ead = pipe_ejecucion_ead.predict(x_ead)
lgd = pipe_ejecucion_lgd.predict(x_lgd)


# 7.RESULTADO
principal = x_pd.principal
EL = pd.DataFrame({"principal": principal, "pd": scoring_pd, "ead": ead, "lgd": lgd})
EL["perdida_esperada"] = round(EL.pd * EL.principal * EL.ead * EL.lgd, 2)

# EL.head(50)
