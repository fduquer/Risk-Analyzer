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

    # INPUTS DE LA APLICACION
    proposito_credito = st.selectbox(
        "Finalidad del Préstamo",
        [
            "consolidar_deudas",
            "mejoras_vivienda",
            "pago_tarjeta_credito",
            "compras_mayores",
            "auto",
            "mejoras_casa",
            "gastos_medicos",
            "vacaciones",
            "mudanza",
            "negocio",
            "OTROS",
        ],
    )
    principal = st.number_input("Valor del Préstamo", 500, 50000)
    numero_cuotas = st.number_input("Número de Cuotas", 6, 60)
    ingreso_mes = st.slider("Ingresos mensuales", 0, 15000)
    antiguedad_empleo = st.selectbox(
        "Antiguedad del empleo",
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
    score_credito = st.number_input("Score de Crédito", 1, 999)
    deuda = st.number_input("Valor de deudas", 0, 10000)

    # DATOS CONOCIDOS (fijadas como datos estaticos por simplicidad)
    verificado = 1
    num_lineas_credito = 1
    porc_uso_revolving = 0
    interes = 13.5
    cuota = principal / numero_cuotas + (principal / numero_cuotas) * (
        (interes / 12) * numero_cuotas * 1.75
    )
    num_derogatorios = 0
    num_hipotecas = 0
    num_lineas_credito = 0
    porc_tarjetas_75p = 10
    num_cancelaciones_12meses = 0

# MAIN
st.title("RISK SCORE ANALYZER")


# CALCULAR

# Crear el registro
registro = pd.DataFrame(
    {
        "ingreso_mes": ingreso_mes,
        "vivienda": vivienda,
        "proposito_credito": proposito_credito,
        "antiguedad_empleo": antiguedad_empleo,
        "score_credito": score_credito,
        "deuda": deuda,
        "num_hipotecas": num_hipotecas,
        "num_lineas_credito": num_lineas_credito,
        "porc_uso_revolving": porc_uso_revolving,
        "porc_tarjetas_75p": porc_tarjetas_75p,
        "num_cancelaciones_12meses": num_cancelaciones_12meses,
        "principal": principal,
        "interes": interes,
        "numero_cuotas": numero_cuotas,
        "cuota": cuota,
        "num_derogatorios": num_derogatorios,
        "verificado": verificado,
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
        st.write("La pérdida esperada es de (Dólares):")
        st.metric(label="PÉRDIDA ESPERADA", value=kpi_el)
    with col2:
        st.write("Se recomienda un extratipo de (Dólares):")
        st.metric(
            label="COMISIÓN A APLICAR", value=kpi_el * 3
        )  # Metido en estático por simplicidad

else:
    st.write("DEFINE LOS PARÁMETROS DEL PRÉSTAMO Y HAZ CLICK EN CALCULAR RIESGO")
