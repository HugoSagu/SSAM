import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="SSAM • Executive Performance Dashboard",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (FONDO BLANCO & ESTILO DASHBOARD EJECUTIVO)
# ---------------------------------------------------------
SSAM_LIGHT_CSS = """
<style>
    /* Fondo principal blanco estilo reporte/slide */
    .stApp {
        background-color: #FFFFFF;
        color: #1F2937;
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Barra lateral en tono gris muy claro para contraste tenue */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Encabezados y Títulos */
    h1, h2, h3, h4 {
        color: #0F172A !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }
    
    /* Tarjetas de Métricas KPI estilo Dashboard Blanco */
    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #C82A2A;
        border-radius: 6px;
        padding: 12px 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    
    /* Pestañas (Tabs) Estilo Corporativo Limpio */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        color: #475569;
        background-color: transparent;
        border-radius: 6px;
        padding: 0px 18px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #C82A2A !important;
        color: #FFFFFF !important;
    }
    
    /* Tarjeta Contenedora de Gráficos (Estilo Módulo) */
    .chart-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .chart-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 8px;
        text-align: center;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 6px;
    }

    /* Tabla de Datos */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
    }
</style>
"""
st.markdown(SSAM_LIGHT_CSS, unsafe_allow_html=True)

# Paleta de Colores
COLOR_RED = "#C82A2A"
COLOR_GOLD = "#D97706"
COLOR_BLUE = "#2563EB"
COLOR_GREEN = "#16A34A"
COLOR_CYAN = "#0891B2"
PALETTE_LIGHT = [
    "#C82A2A",
    "#D97706",
    "#2563EB",
    "#16A34A",
    "#9333EA",
    "#0891B2",
]


# ---------------------------------------------------------
# DATOS OPERATIVOS Y COMPARATIVOS
# ---------------------------------------------------------
@st.cache_data
def load_data():
  df_sucursales = pd.DataFrame({
      "Sucursal": [
          "La Perla",
          "Morelos",
          "Punto Sur",
          "Américas",
          "Santa Fe",
          "Insurgentes",
      ],
      "Ventas_Real": [
          3161538,
          2687672,
          1592686,
          1370517,
          1217461,
          1403518,
      ],
      "Ventas_Presupuesto": [
          3000000,
          2500000,
          1600000,
          1300000,
          1200000,
          1350000,
      ],
      "Comensales_Mes": [5965, 4633, 2844, 2796, 2387, 2673],
      "Ticket_Promedio": [530, 580, 560, 490, 510, 525],
      "M2": [250, 220, 180, 140, 130, 150],
      "Asientos": [110, 95, 75, 60, 55, 65],
      "Food_Cost_%": [23.5, 24.1, 22.8, 25.0, 24.5, 23.9],
      "Labor_Cost_%": [18.2, 19.5, 21.0, 22.4, 21.8, 20.6],
      "Renta_Mensual": [280000, 220000, 180000, 120000, 110000, 130000],
      "EBITDA_Sucursal_%": [24.8, 22.4, 20.1, 17.5, 18.2, 19.0],
  })

  df_sucursales["Prime_Cost_%"] = (
      df_sucursales["Food_Cost_%"] + df_sucursales["Labor_Cost_%"]
  )
  df_sucursales["Rent_Cost_%"] = (
      df_sucursales["Renta_Mensual"] / df_sucursales["Ventas_Real"]
  ) * 100
  df_sucursales["Venta_M2"] = (
      df_sucursales["Ventas_Real"] / df_sucursales["M2"]
  )
  df_sucursales["Venta_Asiento"] = (
      df_sucursales["Ventas_Real"] / df_sucursales["Asientos"]
  )
  df_sucursales["EBITDA_Sucursal_$"] = df_sucursales["Ventas_Real"] * (
      df_sucursales["EBITDA_Sucursal_%"] / 100
  )

  # Datos mensuales para la tendencia (Enero - Junio 2026)
  meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"]
  trend_data = []
  np.random.seed(10)
  for m in meses:
    for suc in df_sucursales["Sucursal"]:
      base = df_sucursales[df_sucursales["Sucursal"] == suc][
          "Ventas_Real"
      ].values[0]
      v_actual = base * np.random.uniform(0.90, 1.10)
      v_budget = base * 0.98
      c_actual = v_actual * 0.45
      p_actual = v_actual * 0.20
      trend_data.append({
          "Mes": m,
          "Sucursal": suc,
          "Ventas_Actual": v_actual,
          "Ventas_Budget": v_budget,
          "Costos_Actual": c_actual,
          "EBITDA_Actual": p_actual,
      })
  df_trend = pd.DataFrame(trend_data)

  # Peer Comparison Data
  df_peer = pd.DataFrame({
      "Métrica": [
          "Costo Materia Prima (Food Cost %)",
          "Nómina Directa (Labor Cost %)",
          "Prime Cost (Food + Labor %)",
          "Costo Ocupación / Renta %",
          "Gastos Operativos & Admón %",
          "Margen EBITDA Consolidado %",
          "Ticket Promedio ($ MXN)",
      ],
      "SSAM (Consolidado 2026)": [24.2, 21.5, 45.7, 8.8, 37.8, 16.5, 532],
      "Alsea (Casual Dining MX)": [29.5, 22.5, 52.0, 9.5, 25.7, 21.8, 410],
      "Benchmark Casual Premium": [26.0, 22.0, 48.0, 9.0, 26.0, 20.0, 550],
  })

  return df_sucursales, df_trend, df_peer


df_sucursales, df_trend, df_peer = load_data()

# ---------------------------------------------------------
# BARRA LATERAL (LOGO MANTENIDO & FILTROS)
# ---------------------------------------------------------
logo_candidates = ["logo.png", "assets/logo.png", "ssam_logo.png", "logo_ssam.png"]
logo_path = next((path for path in logo_candidates if os.path.exists(path)), None)

if logo_path:
  st.sidebar.image(logo_path, use_container_width=True)
else:
  st.sidebar.markdown(
      "<h2 style='text-align: center; color: #C82A2A; margin-bottom: 0;'>SSAM</h2>",
      unsafe_allow_html=True,
  )
  st.sidebar.markdown(
      "<p style='text-align: center; color: #64748B; font-size: 0.75rem;"
      " letter-spacing: 2px;'>RESTAURANTE COREANO</p>",
      unsafe_allow_html=True,
  )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<h3 style='color:#0F172A; font-size: 1rem;'>Filtros de Sucursal</h3>",
    unsafe_allow_html=True,
)
sucursales_sel = st.sidebar.multiselect(
    "Seleccionar Unidades",
    options=df_sucursales["Sucursal"].tolist(),
    default=df_sucursales["Sucursal"].tolist(),
)

df_suc_filt = df_sucursales[df_sucursales["Sucursal"].isin(sucursales_sel)]
df_trend_filt = df_trend[df_trend["Sucursal"].isin(sucursales_sel)]

# ---------------------------------------------------------
# ENCABEZADO DE LA SLIDE / DASHBOARD
# ---------------------------------------------------------
st.markdown(
    "<h2 style='color:#0F172A; margin-bottom:0px;'>Branch Performance"
    " Dashboard for Executive Leadership</h2>",
    unsafe_allow_html=True,
)
st.caption(
    "Análisis de ingresos, costos operativos y rentabilidad por sucursal"
    " alineado a estándares de la industria restaurantera."
)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    "📊 1. Matriz Operativa por Sucursal",
    "🏢 2. Benchmarking Consolidado vs Alsea",
])

# =========================================================
# PESTAÑA 1: LAYOUT MATRICIAL DE 3 COLUMNAS X 3 FILAS
# =========================================================
with tab1:
  # KPI Top Bar
  k1, k2, k3, k4, k5 = st.columns(5)
  total_v = df_suc_filt["Ventas_Real"].sum()
  food_cost_avg = df_suc_filt["Food_Cost_%"].mean()
  labor_cost_avg = df_suc_filt["Labor_Cost_%"].mean()
  ebitda_avg = (
      (df_suc_filt["EBITDA_Sucursal_$"].sum() / total_v) * 100
      if total_v > 0
      else 0
  )
  ticket_avg = df_suc_filt["Ticket_Promedio"].mean()

  k1.metric("Ventas Totales", f"${total_v:,.0f}")
  k2.metric("Food Cost %", f"{food_cost_avg:.1f}%", delta="-5.3% vs Alsea")
  k3.metric("Labor Cost %", f"{labor_cost_avg:.1f}%", delta="-1.0% vs Sector")
  k4.metric("Margen EBITDA %", f"{ebitda_avg:.1f}%", delta="+2.1% vs 2025")
  k5.metric("Ticket Promedio", f"${ticket_avg:.0f}")

  st.markdown("<br>", unsafe_allow_html=True)

  # MATRIZ 3 COLUMNAS (REVENUE | COSTS / EXPENSES | PROFIT / EBITDA)
  col_rev, col_exp, col_prof = st.columns(3)

  # -------------------------------------------------------
  # COLUMNA 1: REVENUE (INGRESOS)
  # -------------------------------------------------------
  with col_rev:
    # Row 1: Annual / Monthly Revenue By Branch
    st.markdown(
        "<div class='chart-header'>Revenue By Branch (Actual vs"
        " Budget)</div>",
        unsafe_allow_html=True,
    )
    fig_r1 = go.Figure()
    fig_r1.add_trace(
        go.Bar(
            x=df_suc_filt["Sucursal"],
            y=df_suc_filt["Ventas_Real"],
            name="Actual",
            marker_color=COLOR_RED,
        )
    )
    fig_r1.add_trace(
        go.Bar(
            x=df_suc_filt["Sucursal"],
            y=df_suc_filt["Ventas_Presupuesto"],
            name="Budget",
            marker_color=COLOR_BLUE,
        )
    )
    fig_r1.update_layout(
        barmode="group",
        template="plotly_white",
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )
    st.plotly_chart(fig_r1, use_container_width=True)

    # Row 2: Revenue Trend
    st.markdown(
        "<div class='chart-header'>Revenue Trend (Monthly)</div>",
        unsafe_allow_html=True,
    )
    df_m_rev = (
        df_trend_filt.groupby("Mes")[["Ventas_Actual", "Ventas_Budget"]]
        .sum()
        .reset_index()
    )
    fig_r2 = go.Figure()
    fig_r2.add_trace(
        go.Bar(
            x=df_m_rev["Mes"],
            y=df_m_rev["Ventas_Actual"],
            name="Actual",
            marker_color=COLOR_RED,
        )
    )
    fig_r2.add_trace(
        go.Bar(
            x=df_m_rev["Mes"],
            y=df_m_rev["Ventas_Budget"],
            name="Budget",
            marker_color=COLOR_BLUE,
        )
    )
    fig_r2.update_layout(
        barmode="group",
        template="plotly_white",
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
    )
    st.plotly_chart(fig_r2, use_container_width=True)

    # Row 3: Top Branches By Revenue
    st.markdown(
        "<div class='chart-header'>Top Branches By Revenue Share</div>",
        unsafe_allow_html=True,
    )
    fig_r3 = px.pie(
        df_suc_filt,
        values="Ventas_Real",
        names="Sucursal",
        hole=0.5,
        template="plotly_white",
        color_discrete_sequence=PALETTE_LIGHT,
    )
    fig_r3.update_layout(
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(font=dict(size=10)),
    )
    st.plotly_chart(fig_r3, use_container_width=True)

  # -------------------------------------------------------
  # COLUMNA 2: EXPENSES & PRIME COST (GASTOS Y COSTOS)
  # -------------------------------------------------------
  with col_exp:
    # Row 1: Prime Cost Structure By Branch
    st.markdown(
        "<div class='chart-header'>Expenses By Branch (Food vs Labor"
        " Cost)</div>",
        unsafe_allow_html=True,
    )
    fig_e1 = go.Figure()
    fig_e1.add_trace(
        go.Bar(
            x=df_suc_filt["Sucursal"],
            y=df_suc_filt["Food_Cost_%"],
            name="Food Cost %",
            marker_color=COLOR_GOLD,
        )
    )
    fig_e1.add_trace(
        go.Bar(
            x=df_suc_filt["Sucursal"],
            y=df_suc_filt["Labor_Cost_%"],
            name="Labor Cost %",
            marker_color=COLOR_CYAN,
        )
    )
    fig_e1.update_layout(
        barmode="stack",
        template="plotly_white",
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )
    st.plotly_chart(fig_e1, use_container_width=True)

    # Row 2: Expense Trend
    st.markdown(
        "<div class='chart-header'>Expense Trend (Monthly Direct"
        " Costs)</div>",
        unsafe_allow_html=True,
    )
    df_m_exp = df_trend_filt.groupby("Mes")["Costos_Actual"].sum().reset_index()
    fig_e2 = px.bar(
        df_m_exp,
        x="Mes",
        y="Costos_Actual",
        template="plotly_white",
        color_discrete_sequence=[COLOR_GOLD],
    )
    fig_e2.update_layout(
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        yaxis_title="Costos ($)",
    )
    st.plotly_chart(fig_e2, use_container_width=True)

    # Row 3: Top Branches By Rent % (Cost of Occupancy)
    st.markdown(
        "<div class='chart-header'>Top Branches By Rent Expense %</div>",
        unsafe_allow_html=True,
    )
    fig_e3 = px.pie(
        df_suc_filt,
        values="Renta_Mensual",
        names="Sucursal",
        hole=0.5,
        template="plotly_white",
        color_discrete_sequence=PALETTE_LIGHT,
    )
    fig_e3.update_layout(
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(font=dict(size=10)),
    )
    st.plotly_chart(fig_e3, use_container_width=True)

  # -------------------------------------------------------
  # COLUMNA 3: PROFIT & EBITDA (RENTABILIDAD)
  # -------------------------------------------------------
  with col_prof:
    # Row 1: Profit / EBITDA By Branch
    st.markdown(
        "<div class='chart-header'>EBITDA By Branch ($ & %)</div>",
        unsafe_allow_html=True,
    )
    fig_p1 = px.bar(
        df_suc_filt,
        x="Sucursal",
        y="EBITDA_Sucursal_$",
        text=df_suc_filt["EBITDA_Sucursal_%"].apply(lambda x: f"{x:.1f}%"),
        template="plotly_white",
        color_discrete_sequence=[COLOR_GREEN],
    )
    fig_p1.update_layout(
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        yaxis_title="EBITDA ($)",
    )
    st.plotly_chart(fig_p1, use_container_width=True)

    # Row 2: Profit Trend
    st.markdown(
        "<div class='chart-header'>Profit Trend (Monthly EBITDA)</div>",
        unsafe_allow_html=True,
    )
    df_m_prof = (
        df_trend_filt.groupby("Mes")["EBITDA_Actual"].sum().reset_index()
    )
    fig_p2 = px.bar(
        df_m_prof,
        x="Mes",
        y="EBITDA_Actual",
        template="plotly_white",
        color_discrete_sequence=[COLOR_GREEN],
    )
    fig_p2.update_layout(
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        yaxis_title="EBITDA ($)",
    )
    st.plotly_chart(fig_p2, use_container_width=True)

    # Row 3: Top Branches By Profit Share
    st.markdown(
        "<div class='chart-header'>Top Branches By EBITDA Contribution</div>",
        unsafe_allow_html=True,
    )
    fig_p3 = px.pie(
        df_suc_filt,
        values="EBITDA_Sucursal_$",
        names="Sucursal",
        hole=0.5,
        template="plotly_white",
        color_discrete_sequence=PALETTE_LIGHT,
    )
    fig_p3.update_layout(
        height=220,
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(font=dict(size=10)),
    )
    st.plotly_chart(fig_p3, use_container_width=True)

  st.markdown("---")
  st.subheader("Cuadro Resumen de Indicadores por Sucursal")
  st.dataframe(
      df_suc_filt[[
          "Sucursal",
          "Ventas_Real",
          "Ticket_Promedio",
          "Venta_M2",
          "Food_Cost_%",
          "Labor_Cost_%",
          "Prime_Cost_%",
          "Rent_Cost_%",
          "EBITDA_Sucursal_%",
      ]].style.format({
          "Ventas_Real": "${:,.0f}",
          "Ticket_Promedio": "${:,.0f}",
          "Venta_M2": "${:,.0f}",
          "Food_Cost_%": "{:.1f}%",
          "Labor_Cost_%": "{:.1f}%",
          "Prime_Cost_%": "{:.1f}%",
          "Rent_Cost_%": "{:.1f}%",
          "EBITDA_Sucursal_%": "{:.1f}%",
      }),
      use_container_width=True,
  )

# =========================================================
# PESTAÑA 2: PEER COMPARISON VS ALSEA & SECTOR
# =========================================================
with tab2:
  st.subheader("Benchmarking Consolidado: SSAM vs Alsea & Sector Premium")
  st.caption("Fondo blanco corporativo para reporte de comparabilidad.")

  cp1, cp2, cp3 = st.columns(3)

  with cp1:
    st.markdown(
        "<div class='chart-header'>Costo Materia Prima vs Peer Group</div>",
        unsafe_allow_html=True,
    )
    fig_peer_food = px.bar(
        df_peer[df_peer["Métrica"].str.contains("Food Cost")],
        x="Métrica",
        y=[
            "SSAM (Consolidado 2026)",
            "Alsea (Casual Dining MX)",
            "Benchmark Casual Premium",
        ],
        barmode="group",
        template="plotly_white",
        color_discrete_sequence=[COLOR_RED, COLOR_GOLD, COLOR_BLUE],
    )
    fig_peer_food.update_layout(
        height=280,
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )
    st.plotly_chart(fig_peer_food, use_container_width=True)

  with cp2:
    st.markdown(
        "<div class='chart-header'>Prime Cost (Food + Labor %)</div>",
        unsafe_allow_html=True,
    )
    fig_peer_prime = px.bar(
        df_peer[df_peer["Métrica"].str.contains("Prime Cost")],
        x="Métrica",
        y=[
            "SSAM (Consolidado 2026)",
            "Alsea (Casual Dining MX)",
            "Benchmark Casual Premium",
        ],
        barmode="group",
        template="plotly_white",
        color_discrete_sequence=[COLOR_RED, COLOR_GOLD, COLOR_BLUE],
    )
    fig_peer_prime.update_layout(
        height=280,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
    )
    st.plotly_chart(fig_peer_prime, use_container_width=True)

  with cp3:
    st.markdown(
        "<div class='chart-header'>Margen EBITDA Consolidado %</div>",
        unsafe_allow_html=True,
    )
    fig_peer_ebitda = px.bar(
        df_peer[df_peer["Métrica"].str.contains("Margen EBITDA")],
        x="Métrica",
        y=[
            "SSAM (Consolidado 2026)",
            "Alsea (Casual Dining MX)",
            "Benchmark Casual Premium",
        ],
        barmode="group",
        template="plotly_white",
        color_discrete_sequence=[COLOR_RED, COLOR_GOLD, COLOR_BLUE],
    )
    fig_peer_ebitda.update_layout(
        height=280,
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
    )
    st.plotly_chart(fig_peer_ebitda, use_container_width=True)

  st.markdown("---")
  st.subheader("Tabla Comparativa General")
  st.dataframe(df_peer, use_container_width=True)
