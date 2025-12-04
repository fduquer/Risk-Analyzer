import streamlit as st
from codigo_de_ejecucion import *
from streamlit_echarts import st_echarts

# CONFIGURACION DE LA PÁGINA
st.set_page_config(
    page_title="Risk Score", page_icon="F.Duque_DSFB_logo_500px.jpg", layout="wide"
)

# SIDEBAR
with st.sidebar:
    st.image("F.Duque_DSFB_logo_500px.jpg")

    # INPUTS DE LA APP
    ingreso_mes = st.number_input(label="Ingresos Mes", min_value=0, max_value=50000)
    gasto_mes = st.number_input(label="Gastos Mes", min_value=0, max_value=50000)
    activos = st.number_input(label="Activos", min_value=0, max_value=500000)
    pasivos = st.number_input(label="Pasivos", min_value=0, max_value=500000)
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

    # DATOS CONOCIDOS (fijadas como datos estaticos por simplicidad)
    if vivienda == "HIPOTECADA":
        num_hipotecas = 1
    else:
        num_hipotecas = 0
    porc_tarjetas_75p = 0.3
    interes = 15
    cuota = principal / num_cuotas + (principal * interes / 100 / 12 * 0.57)


# MAIN
st.title("RISK SCORE ANALYZER")


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


# CALCULAR RIESGO
if st.sidebar.button("CALCULAR RIESGO"):
    # Ejecutar el scoring
    EL = ejecutar_modelos(registro)

    # Calcular los kpis
    kpi_pd = int(EL.pd * 100)
    kpi_ead = int(EL.ead * 100)
    kpi_lgd = int(EL.lgd * 100)
    kpi_el = int(EL.principal * EL.pd * EL.ead * EL.lgd)

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

    # Prescripcion
    col1, col2 = st.columns(2)
    with col1:
        st.write("La pérdida esperada es de (Euros):")
        st.metric(label="PÉRDIDA ESPERADA", value=kpi_el)
    with col2:
        st.write("Se recomienda un extratipo de (Euros):")
        st.metric(
            label="COMISIÓN A APLICAR", value=kpi_el * 3
        )  # Metido en estático por simplicidad

else:
    st.write("DEFINE LOS PARÁMETROS DEL PRÉSTAMO Y HAZ CLICK EN CALCULAR RIESGO")
