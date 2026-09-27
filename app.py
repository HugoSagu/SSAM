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
    page_title="SSAM • Rentabilidad por Sucursal y Peer Comparison",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (IDENTIDAD SSAM)
# ---------------------------------------------------------
SSAM_CSS = """
<style>
    .stApp {
        background-color: #111111;
        color: #FAF6F0;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #1A1A1A;
        border-right: 1px solid #2D2D2D;
    }
    h1, h2, h3, h4 {
        color: #FAF6F0 !important;
        font-weight: 600 !important;
    }
    /* Estilo de Tarjetas KPI */
    [data-testid="stMetric"] {
        background-color: #1E1E1E;
        border: 1px solid #2D2D2D;
        border-top: 3px solid #C82A2A;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricLabel"] {
        color: #A0A0A0 !important;
        font-size: 0.80rem !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    [data-testid="stMetricValue"] {
        color: #FAF6F0 !important;
        font-weight: 700 !important;
    }
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1A1A1A;
        padding: 8px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        color: #A0A0A0;
        background-color: #1E1E1E;
        border-radius: 6px;
        padding: 0px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #C82A2A !important;
        color: #FFFFFF !important;
        font-weight: bold;
    }
    /* Dataframes */
    [data-testid="stDataFrame"] {
        background-color: #1E1E1E;
        border-radius: 8px;
        border: 1px solid #2D2D2D;
    }
</style>
"""
st.markdown(SSAM_CSS, unsafe_allow_html=True)

# Paleta de colores SSAM
COLOR_RED = "#C82A2A"
COLOR_GOLD = "#C5A059"
COLOR_GREEN = "#2E7D32"
COLOR_AMBER = "#D97706"
COLOR_DARK_CARD = "#1E1E1E"
PALETTE_SSAM = ["#C82A2A", "#C5A059", "#4E9F3D", "#D97706", "#2563EB", "#9333EA"]


# ---------------------------------------------------------
# DATOS OPERATIVOS DUMMIES
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
      "Ventas_Mensuales": [
          3161538,
          2687672,
          1592686,
          1370517,
          1217461,
          1403518,
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
      df_sucursales["Renta_Mensual"] / df_sucursales["Ventas_Mensuales"]
  ) * 100
  df_sucursales["Venta_M2"] = (
      df_sucursales["Ventas_Mensuales"] / df_sucursales["M2"]
  )
  df_sucursales["Venta_Asiento"] = (
      df_sucursales["Ventas_Mensuales"] / df_sucursales["Asientos"]
  )
  df_sucursales["EBITDA_Sucursal_$"] = df_sucursales["Ventas_Mensuales"] * (
      df_sucursales["EBITDA_Sucursal_%"] / 100
  )

  df_peer = pd.DataFrame({
      "Métrica": [
          "Costo de Materia Prima (Food Cost)",
          "Nómina Directa (Labor Cost)",
          "Prime Cost (Food + Labor)",
          "Ocupación / Renta",
          "Gastos de Operación y Admón (OPEX)",
          "Margen EBITDA Consolidado",
          "Ticket Promedio ($)",
      ],
      "SSAM (Consolidado 2026)": [24.2, 21.5, 45.7, 8.8, 37.8, 16.5, 532],
      "Alsea (Casual Dining MX)": [29.5, 22.5, 52.0, 9.5, 25.7, 21.8, 410],
      "Benchmark Casual Premium": [26.0, 22.0, 48.0, 9.0, 26.0, 20.0, 550],
  })

  return df_sucursales, df_peer


df_sucursales, df_peer = load_data()

# ---------------------------------------------------------
# BARRA LATERAL CON CARGA AUTOMÁTICA DEL LOGO
# ---------------------------------------------------------
# Búsqueda automática del logo PNG en el repositorio
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
      "<p style='text-align: center; color: #A0A0A0; font-size: 0.8rem;"
      " letter-spacing: 2px;'>RESTAURANTE COREANO</p>",
      unsafe_allow_html=True,
  )

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<h3 style='color:#C82A2A;'>Filtros Operativos</h3>", unsafe_allow_html=True
)
sucursales_sel = st.sidebar.multiselect(
    "Sucursales Visibles",
    options=df_sucursales["Sucursal"].tolist(),
    default=df_sucursales["Sucursal"].tolist(),
)

df_suc_filt = df_sucursales[df_sucursales["Sucursal"].isin(sucursales_sel)]

# ---------------------------------------------------------
# ENCABEZADO Y PESTAÑAS PRINCIPALES
# ---------------------------------------------------------
st.markdown(
    "<h2 style='color:#C82A2A; margin-bottom:0;'>SSAM • GASTRONÓMICA"
    " COREANA</h2>",
    unsafe_allow_html=True,
)
st.caption(
    "Dashboard de Rentabilidad por Unidad de Negocio y Competitividad vs"
    " Sector"
)
st.markdown("---")

tab1, tab2 = st.tabs([
    "🏪 1. Rentabilidad por Sucursal (KPIs Clave)",
    "🏢 2. Peer Comparison (SSAM vs Alsea & Sector)",
])

# =========================================================
# PESTAÑA 1: RENTABILIDAD POR SUCURSAL
# =========================================================
with tab1:
  st.subheader("Indicadores Clave de Desempeño Restaurantero por Sucursal")

  c1, c2, c3, c4, c5 = st.columns(5)
  total_ventas = df_suc_filt["Ventas_Mensuales"].sum()
  prime_cost_prom = df_suc_filt["Prime_Cost_%"].mean()
  ebitda_suc_prom = (
      (df_suc_filt["EBITDA_Sucursal_$"].sum() / total_ventas) * 100
      if total_ventas > 0
      else 0
  )
  ticket_prom_gen = df_suc_filt["Ticket_Promedio"].mean()
  venta_m2_prom = df_suc_filt["Venta_M2"].mean()

  c1.metric("Ventas Totales Mes", f"${total_ventas:,.0f}")
  c2.metric(
      "Prime Cost Promedio",
      f"{prime_cost_prom:.1f}%",
      delta="-3.3% vs Meta (55%)",
  )
  c3.metric(
      "EBITDA Sucursales %", f"{ebitda_suc_prom:.1f}%", delta="+2.1% vs 2025"
  )
  c4.metric("Ticket Promedio", f"${ticket_prom_gen:.0f}")
  c5.metric("Venta / m² Promedio", f"${venta_m2_prom:,.0f}")

  st.markdown("---")

  g1, g2 = st.columns(2)

  with g1:
    st.markdown("**Estructura de Prime Cost (Food Cost % + Labor Cost %)**")
    fig_prime = go.Figure()
    fig_prime.add_trace(
        go.Bar(
            x=df_suc_filt["Sucursal"],
            y=df_suc_filt["Food_Cost_%"],
            name="Food Cost % (Materia Prima)",
            marker_color=COLOR_RED,
        )
    )
    fig_prime.add_trace(
        go.Bar(
            x=df_suc_filt["Sucursal"],
            y=df_suc_filt["Labor_Cost_%"],
            name="Labor Cost % (Nómina Directa)",
            marker_color=COLOR_GOLD,
        )
    )
    fig_prime.update_layout(
        barmode="stack",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        yaxis_title="Porcentaje de Ventas (%)",
    )
    st.plotly_chart(fig_prime, use_container_width=True)

  with g2:
    st.markdown("**EBITDA Operativo por Sucursal ($ MXN y %)**")
    fig_ebitda = px.bar(
        df_suc_filt,
        x="Sucursal",
        y="EBITDA_Sucursal_$",
        text=df_suc_filt["EBITDA_Sucursal_%"].apply(lambda x: f"{x:.1f}%"),
        template="plotly_dark",
        color="EBITDA_Sucursal_%",
        color_continuous_scale=["#D97706", "#C5A059", "#4E9F3D"],
    )
    fig_ebitda.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="EBITDA Mensual ($)",
    )
    st.plotly_chart(fig_ebitda, use_container_width=True)

  g3, g4 = st.columns(2)

  with g3:
    st.markdown(
        "**Productividad Comercial: Venta por m² vs Venta por Asiento**"
    )
    fig_m2 = go.Figure()
    fig_m2.add_trace(
        go.Bar(
            x=df_suc_filt["Sucursal"],
            y=df_suc_filt["Venta_M2"],
            name="$/m²",
            marker_color="#2563EB",
        )
    )
    fig_m2.add_trace(
        go.Bar(
            x=df_suc_filt["Sucursal"],
            y=df_suc_filt["Venta_Asiento"],
            name="$/Silla",
            marker_color="#9333EA",
        )
    )
    fig_m2.update_layout(
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )
    st.plotly_chart(fig_m2, use_container_width=True)

  with g4:
    st.markdown("**Costo de Ocupación / Renta (% sobre Ventas)**")
    fig_rent = px.bar(
        df_suc_filt,
        x="Sucursal",
        y="Rent_Cost_%",
        text_auto=".1f",
        template="plotly_dark",
        color_discrete_sequence=[COLOR_GOLD],
    )
    fig_rent.add_hline(
        y=10.0,
        line_dash="dash",
        line_color=COLOR_RED,
        annotation_text="Límite Recomendado (10%)",
    )
    fig_rent.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Renta / Ventas (%)",
    )
    st.plotly_chart(fig_rent, use_container_width=True)

  st.subheader("Cuadro de Mando Comparativo por Punto de Venta")
  df_display = df_suc_filt[[
      "Sucursal",
      "Ventas_Mensuales",
      "Ticket_Promedio",
      "Venta_M2",
      "Food_Cost_%",
      "Labor_Cost_%",
      "Prime_Cost_%",
      "Rent_Cost_%",
      "EBITDA_Sucursal_%",
  ]].copy()

  st.dataframe(
      df_display.style.format({
          "Ventas_Mensuales": "${:,.0f}",
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
# PESTAÑA 2: PEER COMPARISON (SSAM VS ALSEA Y SECTOR)
# =========================================================
with tab2:
  st.subheader(
      "Benchmarking Consolidado: SSAM vs Alsea (Casual Dining) y Sector Premium"
  )
  st.caption(
      "Comparativo de eficiencia operativa consolidada frente a estándares de"
      " la industria pública y privada en México."
  )

  m1, m2, m3, m4 = st.columns(4)
  m1.metric(
      "Food Cost SSAM",
      "24.2%",
      delta="-5.3% vs Alsea (29.5%)",
      delta_color="normal",
  )
  m2.metric(
      "Prime Cost SSAM",
      "45.7%",
      delta="-6.3% vs Alsea (52.0%)",
      delta_color="normal",
  )
  m3.metric(
      "Gastos OPEX / Admón",
      "37.8%",
      delta="+12.1% vs Alsea (25.7%)",
      delta_color="inverse",
  )
  m4.metric(
      "Margen EBITDA Consolidado",
      "16.5%",
      delta="-5.3% vs Alsea (21.8%)",
      delta_color="inverse",
  )

  st.markdown("---")

  p1, p2 = st.columns([1.2, 1])

  with p1:
    st.markdown("**Comparativa de Perfil Operativo (Spider / Radar Chart)**")
    categories = [
        "Eficiencia Food Cost",
        "Eficiencia Labor Cost",
        "Control OPEX Corporativo",
        "Margen EBITDA %",
        "Ticket Promedio",
    ]
    values_ssam = [85, 80, 45, 70, 88]
    values_alsea = [65, 75, 85, 88, 70]
    values_bench = [75, 78, 80, 80, 85]

    fig_radar = go.Figure()
    fig_radar.add_trace(
        go.Scatterpolar(
            r=values_ssam,
            theta=categories,
            fill="toself",
            name="SSAM",
            line_color=COLOR_RED,
        )
    )
    fig_radar.add_trace(
        go.Scatterpolar(
            r=values_alsea,
            theta=categories,
            fill="toself",
            name="Alsea (Casual Dining)",
            line_color=COLOR_GOLD,
        )
    )
    fig_radar.add_trace(
        go.Scatterpolar(
            r=values_bench,
            theta=categories,
            fill="toself",
            name="Benchmark Sector",
            line_color="#2563EB",
        )
    )

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5
        ),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

  with p2:
    st.markdown("**Estructura de Cascada P&L (% sobre Ventas): SSAM**")
    fig_waterfall = go.Figure(
        go.Waterfall(
            name="SSAM 2026",
            orientation="v",
            measure=[
                "relative",
                "relative",
                "relative",
                "relative",
                "relative",
                "total",
            ],
            x=[
                "Ventas",
                "Costo Materia Prima",
                "Nómina Directa",
                "Renta",
                "Otros Gastos Op.",
                "EBITDA",
            ],
            textposition="outside",
            text=["100%", "-24.2%", "-21.5%", "-8.8%", "-29.0%", "16.5%"],
            y=[100, -24.2, -21.5, -8.8, -29.0, 16.5],
            connector={"line": {"color": COLOR_GOLD}},
            decreasing={"marker": {"color": COLOR_RED}},
            totals={"marker": {"color": COLOR_GOLD}},
        )
    )
    fig_waterfall.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

  st.subheader("Tabla Comparativa Consolidada vs Peer Group")
  st.dataframe(df_peer, use_container_width=True)
