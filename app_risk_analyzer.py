import codigo_de_ejecucion
import numpy as np
import numpy_financial as npf
import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

# CONFIGURACION DE LA PÁGINA
st.set_page_config(
    page_title="Risk Analyzer", page_icon="media/FDuque_DSFB_logo_500px.jpg")

# Ingreso a la pagina con usuario autenticado

#archivo = __file__.split("\\")[-1]
#login.generarLogin(archivo)
#if "usuario" in st.session_state:

# Genera Barra lateral
with st.sidebar:
     st.image("media/FDuque_DSFB_logo_500px.jpg")
     st.subheader("Data Science for Bussiness")
     st.write("Bussiness Analytics")
     st.write("Machine Learning")
     st.write("Data Products")

st.title("RISK SCORE :red[ANALYZER] ")

# INPUTS DE LA APLICACION

# Parametro
umbral_corte_pd = 0.3
col1, col2, col3 = st.columns(
        3, gap="medium", vertical_alignment="top", border=True
    )
with col1:
        proposito_credito = st.selectbox(
            "Finalidad del Préstamo",
            [
                "consolidar_deudas",
                "pago_tarjeta_credito",
                "mejoras_vivienda",
                "compras_mayores",
                "gastos_medicos",
                "negocio",
                "otros",
            ],
        )
        principal = st.number_input("Importe Solicitado", 500, 40000)
        num_cuotas = st.number_input("Número de Cuotas", 6, 60)

with col2:
        ingreso_mes = st.number_input(
            label="Ingresos Mes", min_value=1, max_value=50000
        )
        gasto_mes = st.number_input(label="Gastos Mes", min_value=1, max_value=50000)
        activos = st.number_input(label="Activos", min_value=1, max_value=500000)
        pasivos = st.number_input(label="Pasivos", min_value=1, max_value=500000)

with col3:
        antiguedad_empleo = st.selectbox(
            "Antiguedad del Empleo",
            [
                "< 1 año",
                "1 año",
                "2 años",
                "3 años",
                "4 años",
                "5 años",
                "6 años",
                "7 años",
                "8 años",
                "9 años",
                "10+ años",
            ],
        )
        vivienda = st.selectbox(
            "Vivienda", ["HIPOTECADA", "ARRENDADA", "PROPIA NO HIPOTECADA", "OTRO"]
        )
        score_credito = st.number_input(
            label="Score de Crédito", min_value=0, max_value=999
        )

        # DATOS CONOCIDOS (fijadas como datos estaticos por simplicidad)
        if vivienda == "HIPOTECADA":
            num_hipotecas = 1
        else:
            num_hipotecas = 0
        porc_tarjetas_75p = 0.3
        interes = 15
        # cuota = principal / num_cuotas + (principal * interes / 100 / 12 * 0.57)
        cuota = np.round(
            npf.pmt(interes / 12 / 100, num_cuotas, principal, fv=0) * -1, 2
        )

    # CALCULAR

    # Crear el registro
registro = pd.DataFrame(
        {
            "ingreso_mes": ingreso_mes,
            "gasto_mes": gasto_mes,
            "activos": activos,
            "pasivos": pasivos,
            "antiguedad_empleo": antiguedad_empleo,
            "vivienda": vivienda,
            "num_hipotecas": num_hipotecas,
            "porc_tarjetas_75p": porc_tarjetas_75p,
            "score_credito": score_credito,
            "proposito_credito": proposito_credito,
            "principal": principal,
            "numero_cuotas": num_cuotas,
            "interes": interes,
            "cuota": cuota,
        },
        index=[0],
    )

    # MAIN

    # CALCULAR RIESGO
if st.button("CALCULAR RIESGO", type="primary"):
        # Ejecutar el scoring
        EL = codigo_de_ejecucion.ejecutar_modelos(registro)

        # Calcular los kpis
        kpi_pd = int(EL.pd * 100)
        kpi_ead = int(EL.ead * 100)
        kpi_lgd = int(EL.lgd * 100)
        kpi_el = int(EL.principal * EL.pd * EL.ead * EL.lgd)
        capacidad_pago = ingreso_mes - gasto_mes
        r_gasto_ingreso = gasto_mes / ingreso_mes
        r_activos_pasivos = activos / pasivos
        r_cuota_capacidad_pago = cuota / capacidad_pago

        if (
            (kpi_pd / 100 <= umbral_corte_pd)
            & (capacidad_pago > cuota)
            & (r_activos_pasivos > 1)
        ):
            recomendacion = "APROBADO"
        elif (kpi_pd / 100 <= umbral_corte_pd) & (capacidad_pago > cuota):
            recomendacion = "ZONA GRIS, REVISAR SITUACION FINANCIERA DEL CLIENTE"
        else:
            recomendacion = "NEGADO"
        if recomendacion == "APROBADO":
            color = "green"
        else:
            color = "red"

        # Prescripcion
        col1, col2, col3 = st.columns(3)
        with col1:
            st.header("INDICADORES", divider="gray")
            st.metric(label="Cuota", value=round(number=cuota, ndigits=2))
            st.metric(label="Capacidad de Pago", value=round(capacidad_pago, 2))
            st.metric(label="Activos/Pasivos", value=round(r_activos_pasivos, 4))
        with col2:
            st.header(" ", divider="gray")
            st.metric(
                label="Cuota/Capacidad de Pago", value=round(r_cuota_capacidad_pago, 4)
            )
            st.metric("Perdida Esperada $", value=round(kpi_el, 2))

        with col3:
            st.header("RESULTADO", divider="gray")
            st.title(f"**:{color}[{recomendacion}]**")

        # Velocimetros
        # Codigo de velocimetros tomado de https://towardsdatascience.com/5-streamlit-components-to-build-better-applications-71e0195c82d4
        pd_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "PD",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": kpi_pd, "name": "PD"}],
                }
            ],
        }

        # Velocimetro para ead
        ead_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "EAD",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": kpi_ead, "name": "EAD"}],
                }
            ],
        }

        # Velocimetro para lgd
        lgd_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "LGD",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {
                        "show": "true",
                        "width": 10,
                    },
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": kpi_lgd, "name": "LGD"}],
                }
            ],
        }
        # Representarlos en la app
        col1, col2, col3 = st.columns(3)
        with col1:
            st_echarts(options=pd_options, width="110%", key="0")
        with col2:
            st_echarts(options=ead_options, width="110%", key="1")
        with col3:
            st_echarts(options=lgd_options, width="110%", key="2")

else:
        st.write("DEFINE LOS PARÁMETROS DEL PRÉSTAMO Y HAZ CLICK EN CALCULAR RIESGO")

st.title("1. Descripción general")
with st.expander("Muestra el detalle"):
        col1, col2 = st.columns([0.65, 0.35], vertical_alignment="bottom")

        with col1:
            st.header("Risk Analyzer :key:")

            st.subheader(
                "permite evaluar el riesgo para otorgar un préstamo de adquisición"
            )

            st.subheader("""
                         Objetivos de la herramienta:

                         Incrementar los rendimientos financieros de las operaciones de credito  
                         
                         Controlar el riesgo asociado a los préstamos concedidos

                         Incrementar o disminuir la colocación en función de:
                         - las políticas de crédito vigentes,  
                         - la situación de oferta y demanda del mercado,  
                         - o la liquidez de la institución
                         """)

            st.markdown(
                """Tiene como motor de procesamiento 3 modelos de machine learning, 
                basados en el concepto de Perdida Esperada y reglas de aprobación en 
                función de indicadores financieros del cliente y de la operación de crédito.

                Usos:  
                * Bancos y Cooperativas  
                * Almacenes comerciales  
                * Concesionarios de vehículos

                Procesamiento:  
                - On demand para análisis de préstamos en línea,  
                - Análisis en lotes para operaciones de crédito solicitadas                  
                
                Características:
                * Flexibilidad para ajustar el volumen de crédito a conceder.  
                * Actualización permanente mediante el re-entrenamiento del modelo.  
                * Conectividad e integración con cualquier tipo de aplicación"""
            )
        with col2:
            st.markdown("""La customización de la herramienta permitirá manejar  
                        cualquier tipo de crédito (consumo, micro, productivo, etc)""")
            st.image("media/perdida_esperada_texto.png")

st.title("2. Ajuste del volumen de crédito")

with st.expander("Muestra el detalle"):
        st.metric("Límite de corte de la probabilidad de impago", umbral_corte_pd)

        col1, col2 = st.columns([0.6, 0.4], vertical_alignment="center")

        with col2:
            st.header("Ajuste del volumen de crédito a otorgar  :material/money_range:")

            st.subheader("Permite abrir o cerrar la 'llave' de los préstamos")
            st.subheader("Ajustando el límite de corte de la Probabilidad de Impago PD")
            st.subheader(
                "se puede otorgar más o menos credito, manteniendo el control del riesgo"
            )

        with col1:
            st.image("media/ajuste_pe.png")

st.title("3. Información técnica")

with st.expander("Muestra el detalle"):
        col1, col2 = st.columns([0.7, 0.3], vertical_alignment="center")
        with col1:
            st.header("Datos para el modelamiento")
            st.markdown(
                """Data con 200.000 registros de credito de consumo, 
                 3 años de historia crediticia. Las variables predictoras 
                 incluyen situación laboral y financiera del cliente, 
                 información de la operación de credito otorgada asi como su estado
                 """
            )
            st.header("Modelos de Machine Learning")
            st.markdown(
                """Generación de 3 modelos de ML supervisado:  
                1. Perdida Esperada PD, algoritmo utilizado Regresión Logistica  
                2. Exposición al momento del impago EAD, algoritmo utilizado XGBoost  
                3. Perdida luego del impago LGD, algoritmo utilizado XGBoost  

                El desarrollo de los modelos se realizó principalmente
                con las siguientes herramientas:
                * IDE VS code
                * Python
                * Matplot lib
                * Seaborn
                * Pandas
                * Numpy
                * Scikit learn
                 """
            )
st.title("4. Modelo PD")
roc_auc_score = 0.82322959

with st.expander("Muestra el detalle"):
        st.subheader("ROC AUC SCORE: 0.82322959")
        st.subheader("ROC Curves")
        st.image("media/pd_roc_auc.png")
        st.subheader("Precission -Recall Curves")
        st.image("media/pd_prec_rec.png")

st.title("5. Modelo EAD")
with st.expander("Muestra el detalle"):
        st.subheader("Mean Absolute Error = 0.062805")
        st.subheader("Check Validation Curves")
        st.image("media/ead_chek_val.png")

st.title("6. Modelo LGD")
with st.expander("Muestra el detalle"):
        st.subheader("Mean Absolute Error = 0.080804")
        st.subheader("Check Validation Curves")
        st.image("media/lgd_chek_val.png")