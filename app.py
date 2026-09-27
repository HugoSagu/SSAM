import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="SSAM • Dashboard Ejecutivo de Finanzas",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (IDENTIDAD SSAM.MX)
# ---------------------------------------------------------
SSAM_CSS = """
<style>
    /* Fondo principal y tipografía */
    .stApp {
        background-color: #111111;
        color: #FAF6F0;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A;
        border-right: 1px solid #2D2D2D;
    }
    
    /* Encabezados y títulos */
    h1, h2, h3, h4 {
        color: #FAF6F0 !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }
    
    /* Targetas de Métricas (KPI Cards) */
    [data-testid="stMetric"] {
        background-color: #1E1E1E;
        border: 1px solid #2D2D2D;
        border-top: 3px solid #C82A2A;
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    [data-testid="stMetricLabel"] {
        color: #A0A0A0 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    
    [data-testid="stMetricValue"] {
        color: #FAF6F0 !important;
        font-weight: 700 !important;
    }
    
    /* Botones y Sliders */
    .stButton>button {
        background-color: #C82A2A;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #A02020;
        color: #FFFFFF;
        box-shadow: 0 0 10px rgba(200, 42, 42, 0.5);
    }
    
    /* Subrayados y divisores */
    hr {
        border-color: #2D2D2D !important;
    }
    
    /* Dataframe y Tablas */
    [data-testid="stDataFrame"] {
        background-color: #1E1E1E;
        border-radius: 8px;
        border: 1px solid #2D2D2D;
    }
</style>
"""
st.markdown(SSAM_CSS, unsafe_allow_html=True)

# Configuración de Paleta Plotly SSAM
COLOR_RED = "#C82A2A"
COLOR_GOLD = "#C5A059"
COLOR_CREAM = "#FAF6F0"
COLOR_DARK_CARD = "#1E1E1E"
PALETTE_SSAM = ["#C82A2A", "#C5A059", "#4E9F3D", "#D97706", "#2563EB", "#9333EA"]

# ---------------------------------------------------------
# DATOS DUMMIES DE EJEMPLO
# ---------------------------------------------------------
@st.cache_data
def load_data():
    sucursales = ['La Perla', 'Morelos', 'Punto Sur', 'Américas', 'Santa Fe', 'Insurgentes']
    
    df_sucursales = pd.DataFrame({
        'Sucursal': sucursales,
        'Ventas_Mensuales': [3161538, 2687672, 1592686, 1370517, 1217461, 1403518],
        'Ticket_Promedio': [530, 580, 560, 490, 510, 525],
        'Comensales_Mes': [5965, 4633, 2844, 2796, 2387, 2673],
        'Costo_Insumos_%': [23.5, 24.1, 22.8, 25.0, 24.5, 23.9],
        'Renta_Mensual': [280000, 220000, 180000, 120000, 110000, 130000],
        'M2': [250, 220, 180, 140, 130, 150]
    })
    df_sucursales['Venta_M2'] = df_sucursales['Ventas_Mensuales'] / df_sucursales['M2']
    
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio']
    data_hist = []
    np.random.seed(42)
    for mes in meses:
        for suc in sucursales:
            base_val = df_sucursales[df_sucursales['Sucursal'] == suc]['Ventas_Mensuales'].values[0]
            factor = np.random.uniform(0.88, 1.12)
            ventas = base_val * factor
            costo = ventas * (df_sucursales[df_sucursales['Sucursal'] == suc]['Costo_Insumos_%'].values[0] / 100)
            gastos_op = ventas * 0.45
            data_hist.append({
                'Mes': mes,
                'Sucursal': suc,
                'Ventas': ventas,
                'Costo_Ventas': costo,
                'Margen_Bruto': ventas - costo,
                'EBITDA_Operativo': ventas - costo - gastos_op
            })
    df_historico = pd.DataFrame(data_hist)
    return df_sucursales, df_historico

df_sucursales, df_historico = load_data()

# ---------------------------------------------------------
# BARRA LATERAL / NAVEGACIÓN
# ---------------------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center; color: #C82A2A;'>SSAM</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #A0A0A0; font-size: 0.8rem;'>RESTAURANTE COREANO</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")

modulo = st.sidebar.radio(
    "Módulos del Sistema",
    ["1. Diagnóstico por Sucursal", "2. Proyección Bottom-Up", "3. Evaluación Nuevas Aperturas"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filtro de Sucursales")
sucursal_sel = st.sidebar.multiselect("Seleccionar Ubicación", df_sucursales['Sucursal'].tolist(), default=df_sucursales['Sucursal'].tolist())

# ---------------------------------------------------------
# ENTREGABLE 1: DIAGNÓSTICO HISTÓRICO
# ---------------------------------------------------------
if modulo == "1. Diagnóstico por Sucursal":
    st.title("📊 Diagnóstico de Rentabilidad Operativa")
    st.caption("Estructura de ingresos, márgenes de contribución y métricas por m² de SSAM.")
    
    df_filt = df_historico[df_historico['Sucursal'].isin(sucursal_sel)]
    df_suc_filt = df_sucursales[df_sucursales['Sucursal'].isin(sucursal_sel)]
    
    # KPIs Principales
    col1, col2, col3, col4 = st.columns(4)
    total_ventas = df_filt['Ventas'].sum()
    mb_prom = (df_filt['Margen_Bruto'].sum() / total_ventas) * 100 if total_ventas > 0 else 0
    ebitda_tot = df_filt['EBITDA_Operativo'].sum()
    ticket_prom = df_suc_filt['Ticket_Promedio'].mean() if len(df_suc_filt) > 0 else 0
    
    col1.metric("Ventas Acumuladas", f"${total_ventas:,.0f}", delta="+6.5% vs 2025")
    col2.metric("Margen Bruto Promedio", f"{mb_prom:.1f}%", delta="+1.2%")
    col3.metric("EBITDA Operativo", f"${ebitda_tot:,.0f}", delta="+4.8%")
    col4.metric("Ticket Promedio Global", f"${ticket_prom:.0f}")
    
    st.markdown("---")
    
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Ingresos Mensuales por Sucursal")
        fig_ventas = px.bar(
            df_filt, x='Mes', y='Ventas', color='Sucursal',
            barmode='group', template='plotly_dark',
            color_discrete_sequence=PALETTE_SSAM
        )
        fig_ventas.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_ventas, use_container_width=True)
        
    with g2:
        st.subheader("Ventas por Metro Cuadrado ($/m²)")
        fig_m2 = px.bar(
            df_suc_filt, x='Sucursal', y='Venta_M2',
            text_auto='.2s', template='plotly_dark',
            color_discrete_sequence=[COLOR_GOLD]
        )
        fig_m2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_m2, use_container_width=True)
        
    st.subheader("Resumen Operativo por Sucursal")
    st.dataframe(
        df_suc_filt.style.format({
            'Ventas_Mensuales': '${:,.2f}',
            'Ticket_Promedio': '${:,.2f}',
            'Costo_Insumos_%': '{:.1f}%',
            'Renta_Mensual': '${:,.2f}',
            'Venta_M2': '${:,.2f}'
        }), use_container_width=True
    )

# ---------------------------------------------------------
# ENTREGABLE 2: PROYECCIÓN BOTTOM-UP
# ---------------------------------------------------------
elif modulo == "2. Proyección Bottom-Up":
    st.title("📈 Proyección Financiera Corporativa SSAM")
    st.caption("Simulación de escenarios estratégicos a 5 años.")
    
    st.subheader("Parámetros de Sensibilidad")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        crec_aforo = st.slider("Crecimiento Anual en Aforo (%)", 0.0, 15.0, 5.0, step=0.5)
    with c2:
        var_costo = st.slider("Ajuste Costo de Insumos (%)", -5.0, 10.0, 0.0, step=0.5)
    with c3:
        inc_ticket = st.slider("Incremento en Ticket Promedio (%)", 0.0, 12.0, 4.5, step=0.5)
        
    st.markdown("---")
    
    anios = [2026, 2027, 2028, 2029, 2030]
    base_rev = 105969033  # Cierre 2025 real SSAM
    base_cost = 0.2349
    
    proyecciones = []
    rev_actual = base_rev
    cost_actual = base_cost + (var_costo / 100)
    
    for anio in anios:
        rev_actual = rev_actual * (1 + (crec_aforo/100) + (inc_ticket/100))
        costo_total = rev_actual * cost_actual
        gastos_op = rev_actual * 0.55
        ebitda = rev_actual - costo_total - gastos_op
        proyecciones.append({
            'Año': anio,
            'Ingresos Proyectados': rev_actual,
            'Costo Insumos': costo_total,
            'EBITDA': ebitda,
            'Margen EBITDA %': (ebitda / rev_actual) * 100
        })
        
    df_proj = pd.DataFrame(proyecciones)
    
    p1, p2 = st.columns([2, 1])
    
    with p1:
        st.subheader("Evolución Proyectada de Ingresos vs EBITDA")
        fig_proj = go.Figure()
        fig_proj.add_trace(go.Bar(x=df_proj['Año'], y=df_proj['Ingresos Proyectados'], name='Ingresos', marker_color=COLOR_RED))
        fig_proj.add_trace(go.Scatter(x=df_proj['Año'], y=df_proj['EBITDA'], name='EBITDA', line=dict(color=COLOR_GOLD, width=3)))
        fig_proj.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_proj, use_container_width=True)
        
    with p2:
        st.subheader("Tabla de Proyección")
        st.dataframe(df_proj.style.format({
            'Ingresos Proyectados': '${:,.0f}',
            'Costo Insumos': '${:,.0f}',
            'EBITDA': '${:,.0f}',
            'Margen EBITDA %': '{:.1f}%'
        }), height=260)

# ---------------------------------------------------------
# ENTREGABLE 3: EVALUADOR DE NUEVAS APERTURAS (GO / NO-GO)
# ---------------------------------------------------------
elif modulo == "3. Evaluación Nuevas Aperturas":
    st.title("🎯 Modelo Evaluador de Nuevas Sucursales")
    st.caption("Análisis de Unit Economics y matriz de viabilidad Go / No-Go para expansión.")
    
    col_input, col_results = st.columns([1, 1.2])
    
    with col_input:
        st.subheader("Parámetros del Proyecto")
        nombre_nueva = st.text_input("Ubicación Propuesta", "SSAM - Centro Comercial San Javier")
        m2_nuevo = st.number_input("Superficie Local (m²)", min_value=50, max_value=500, value=220)
        asientos_nuevos = st.number_input("Capacidad de Asientos", min_value=20, max_value=200, value=90)
        ticket_est = st.number_input("Ticket Promedio Estimado ($)", value=560)
        comensales_dia = st.number_input("Comensales Estimados / Día", value=160)
        
        st.markdown("**Estructura de Inversión (CAPEX)**")
        capex_obra = st.number_input("Adecuaciones & Decoración SSAM ($)", value=3800000)
        capex_equipo = st.number_input("Equipamiento de Cocina & Parrillas ($)", value=2100000)
        working_cap = st.number_input("Capital de Trabajo Inicial ($)", value=800000)
        
        capex_total = capex_obra + capex_equipo + working_cap
        st.markdown(f"<h4 style='color:{COLOR_GOLD};'>Inversión Inicial Total: ${capex_total:,.0f}</h4>", unsafe_allow_html=True)

    with col_results:
        st.subheader("Indicadores de Retorno y Viabilidad")
        
        ventas_mes_est = comensales_dia * 30 * ticket_est
        costo_est = ventas_mes_est * 0.24
        renta_est = ventas_mes_est * 0.10
        nomina_est = ventas_mes_est * 0.18
        otros_gastos = ventas_mes_est * 0.12
        
        ebitda_mes_est = ventas_mes_est - costo_est - renta_est - nomina_est - otros_gastos
        ebitda_anual_est = ebitda_mes_est * 12
        
        payback_meses = capex_total / ebitda_mes_est if ebitda_mes_est > 0 else 0
        tir_estimada = (ebitda_anual_est / capex_total) * 100 if capex_total > 0 else 0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Venta Mensual Est.", f"${ventas_mes_est:,.0f}")
        m2.metric("EBITDA Mensual Est.", f"${ebitda_mes_est:,.0f}")
        m3.metric("Payback Estimado", f"{payback_meses:.1f} meses")
        
        st.markdown("---")
        st.subheader("Matriz de Decisión (Scorecard)")
        
        criterio_payback = payback_meses <= 36
        criterio_margin = (ebitda_mes_est / ventas_mes_est) >= 0.20 if ventas_mes_est > 0 else False
        criterio_tir = tir_estimada >= 25.0
        
        puntos = sum([criterio_payback, criterio_margin, criterio_tir])
        
        if puntos == 3:
            st.success("🟢 **DICTAMEN: GO (APROBADO)** — Proyecto altamente rentable alineado con los estándares de la marca SSAM.")
        elif puntos == 2:
            st.warning("🟡 **DICTAMEN: REVISIÓN** — Proyecto viable pero requiere optimizar renta o reducción en CAPEX.")
        else:
            st.error("🔴 **DICTAMEN: NO-GO (RECHAZADO)** — Las métricas de retorno no cumplen los parámetros mínimos.")
            
        st.markdown(f"""
        * **Periodo de Recuperación (Payback):** {payback_meses:.1f} meses *(Meta: ≤ 36 meses)* {'✅' if criterio_payback else '❌'}
        * **Margen EBITDA Operativo:** {(ebitda_mes_est/ventas_mes_est)*100:.1f}% *(Meta: ≥ 20%)* {'✅' if criterio_margin else '❌'}
        * **Rendimiento Anual sobre Inversión (TIR):** {tir_estimada:.1f}% *(Meta: ≥ 25%)* {'✅' if criterio_tir else '❌'}
        """)
