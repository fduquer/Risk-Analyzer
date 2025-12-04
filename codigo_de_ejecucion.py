# 1.LIBRERIAS
import pickle

import pandas as pd

# 4.FUNCIONES DE SOPORTE


def calidad_datos(temp):
    for column in temp.select_dtypes("number").columns:
        temp[column] = temp[column].fillna(0)
    return temp


def creacion_variables(df):
    temp = df.copy()
    return temp


def ejecutar_modelos(df):
    # 5.CALIDAD Y CREACION DE VARIABLES
    x_pd = creacion_variables(calidad_datos(df))
    x_ead = creacion_variables(calidad_datos(df))
    x_lgd = creacion_variables(calidad_datos(df))

    # 5.CARGA PIPES DE EJECUCION

    with open("pipe_ejecucion_pd.pickle", mode="rb") as file:
        pipe_ejecucion_pd = pickle.load(file)

    with open("pipe_ejecucion_ead.pickle", mode="rb") as file:
        pipe_ejecucion_ead = pickle.load(file)

    with open("pipe_ejecucion_lgd.pickle", mode="rb") as file:
        pipe_ejecucion_lgd = pickle.load(file)

    # 6.EJECUCION
    scoring_pd = pipe_ejecucion_pd.predict_proba(x_pd)[:, 1]
    ead = pipe_ejecucion_ead.predict(x_ead)
    lgd = pipe_ejecucion_lgd.predict(x_lgd)

    # 7.RESULTADO
    principal = x_pd.principal
    EL = pd.DataFrame(
        {"principal": principal, "pd": scoring_pd, "ead": ead, "lgd": lgd}
    )
    EL["perdida_esperada"] = round(EL.pd * EL.principal * EL.ead * EL.lgd, 2)

    return EL
