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
    page_title="SSAM • Performance & POS Operations Dashboard",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# ESTILOS CSS PERSONALIZADOS (DISEÑO BLANCO EJECUTIVO)
# ---------------------------------------------------------
SSAM_LIGHT_CSS = """
<style>
    .stApp {
        background-color: #FFFFFF;
        color: #1F2937;
        font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    h1, h2, h3, h4 {
        color: #0F172A !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }
    /* Estilo de Tarjetas KPI */
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
        font-size: 1.4rem !important;
        font-weight: 700 !important;
    }
    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        color: #475569;
        background-color: transparent;
        border-radius: 6px;
        padding: 0px 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #C82A2A !important;
        color: #FFFFFF !important;
    }
    /* Tarjeta Contenedora de Gráficos */
    .chart-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .chart-header {
        font-size: 0.90rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 8px;
        text-align: center;
        border-bottom: 1px solid #F1F5F9;
        padding-bottom: 6px;
    }
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 6px;
        border: 1px solid #E2E8F0;
    }
</style>
"""
st.markdown(SSAM_LIGHT_CSS, unsafe_allow_html=True)

# Paleta de Colores SSAM
COLOR_RED = "#C82A2A"
COLOR_GOLD = "#D97706"
COLOR_BLUE = "#2563EB"
COLOR_GREEN = "#16A34A"
COLOR_CYAN = "#0891B2"
COLOR_PURPLE = "#9333EA"
PALETTE_LIGHT = [
    "#C82A2A",
    "#D97706",
    "#2563EB",
    "#16A34A",
    "#9333EA",
    "#0891B2",
]


# ---------------------------------------------------------
# CARGA DE DATOS (FINANCIEROS + PUNTO DE VENTA POS)
# ---------------------------------------------------------
@st.cache_data
def load_data():
  # 1. Datos Financieros por Sucursal
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
  df_sucursales["EBITDA_Sucursal_$"] = df_sucursales["Ventas_Real"] * (
      df_sucursales["EBITDA_Sucursal_%"] / 100
  )

  # 2. Datos de Punto de Venta (POS) y Operaciones
  df_pos = pd.DataFrame({
      "Sucursal": [
          "La Perla",
          "Morelos",
          "Punto Sur",
          "Américas",
          "Santa Fe",
          "Insurgentes",
      ],
      "Ventas_Brutas": [3280000, 2790000, 1650000, 1420000, 1260000, 1450000],
      "Descuentos_Cortesias_%": [3.6, 3.7, 3.5, 3.5, 3.4, 3.2],
      "Comision_TPV_Delivery_%": [4.8, 5.2, 6.1, 6.8, 6.5, 5.9],
      "Canal_Comedor_%": [75, 80, 65, 55, 60, 70],
      "Canal_Takeout_%": [10, 8, 12, 15, 12, 10],
      "Canal_Delivery_%": [15, 12, 23, 30, 28, 20],
      "Cat_Alimentos_%": [72, 70, 74, 76, 75, 73],
      "Cat_Bebidas_NoAlc_%": [12, 13, 11, 10, 11, 12],
      "Cat_Bebidas_Alc_%": [12, 13, 11, 10, 10, 11],
      "Cat_Postres_%": [4, 4, 4, 4, 4, 4],
      "Asientos": [110, 95, 75, 60, 55, 65],
      "Comensales_Mes": [5965, 4633, 2844, 2796, 2387, 2673],
      "Tickets_Mes": [2386, 1853, 1138, 1118, 955, 1069],
      "Headcount": [18, 15, 11, 9, 8, 9],
  })

  df_pos["Ventas_Netas"] = df_pos["Ventas_Brutas"] * (
      1 - df_pos["Descuentos_Cortesias_%"] / 100
  )
  df_pos["Monto_Descuentos"] = (
      df_pos["Ventas_Brutas"] - df_pos["Ventas_Netas"]
  )
  df_pos["Ticket_Promedio"] = df_pos["Ventas_Netas"] / df_pos["Tickets_Mes"]
  df_pos["Vueltas_Mesa_Dia"] = (df_pos["Comensales_Mes"] / 30) / df_pos[
      "Asientos"
  ]
  df_pos["Pax_por_Ticket"] = df_pos["Comensales_Mes"] / df_pos["Tickets_Mes"]
  df_pos["Venta_por_Empleado"] = df_pos["Ventas_Netas"] / df_pos["Headcount"]

  # 3. Tendencia Mensual
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

  # 4. Peer Comparison
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

  return df_sucursales, df_pos, df_trend, df_peer


df_sucursales, df_pos, df_trend, df_peer = load_data()

# ---------------------------------------------------------
# BARRA LATERAL (LOGO MANTENIDO)
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
df_pos_filt = df_pos[df_pos["Sucursal"].isin(sucursales_sel)]
df_trend_filt = df_trend[df_trend["Sucursal"].isin(sucursales_sel)]

# ---------------------------------------------------------
# ENCABEZADO PRINCIPAL
# ---------------------------------------------------------
st.markdown(
    "<h2 style='color:#0F172A; margin-bottom:0px;'>SSAM • Executive Performance"
    " & Operations Dashboard</h2>",
    unsafe_allow_html=True,
)
st.caption(
    "Métricas financieras, indicadores de Punto de Venta (POS) y"
    " competitividad de mercado."
)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📊 1. Matriz Financiera & P&L",
    "🛍️ 2. Indicadores Punto de Venta (POS) & Operaciones",
    "🏢 3. Benchmarking Consolidado vs Alsea",
])

# =========================================================
# PESTAÑA 1: MATRIZ FINANCIERA & P&L
# =========================================================
with tab1:
  k1, k2, k3, k4, k5 = st.columns(5)
  total_v = df_suc_filt["Ventas_Real"].sum()
  food_cost_avg = df_suc_filt["Food_Cost_%"].mean()
  labor_cost_avg = df_suc_filt["Labor_Cost_%"].mean()
  ebitda_avg = (
      (df_suc_filt["EBITDA_Sucursal_$"].sum() / total_v) * 100
      if total_v > 0
      else 0
  )
  ticket_avg = df_pos_filt["Ticket_Promedio"].mean()

  k1.metric("Ventas Totales", f"${total_v:,.0f}")
  k2.metric("Food Cost %", f"{food_cost_avg:.1f}%", delta="-5.3% vs Alsea")
  k3.metric("Labor Cost %", f"{labor_cost_avg:.1f}%", delta="-1.0% vs Sector")
  k4.metric("Margen EBITDA %", f"{ebitda_avg:.1f}%", delta="+2.1% vs 2025")
  k5.metric("Ticket Promedio", f"${ticket_avg:.0f}")

  st.markdown("<br>", unsafe_allow_html=True)

  col_rev, col_exp, col_prof = st.columns(3)

  with col_rev:
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

  with col_exp:
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

  with col_prof:
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

# =========================================================
# PESTAÑA 2: REQUERIMIENTOS DE PUNTO DE VENTA (POS) & OPERACIONES
# =========================================================
with tab2:
  st.subheader("Indicadores Operativos & Punto de Venta (POS)")
  st.caption(
      "Métricas extraídas directamente del sistema de caja, terminales TPV y"
      " plantilla de personal."
  )

  # KPIs de Control Operativo
  p_k1, p_k2, p_k3, p_k4, p_k5 = st.columns(5)
  total_bruto = df_pos_filt["Ventas_Brutas"].sum()
  desc_total = df_pos_filt["Monto_Descuentos"].sum()
  desc_pct_avg = (desc_total / total_bruto) * 100
  comis_tpv_avg = df_pos_filt["Comision_TPV_Delivery_%"].mean()
  vueltas_avg = df_pos_filt["Vueltas_Mesa_Dia"].mean()
  venta_emp_avg = df_pos_filt["Venta_por_Empleado"].mean()

  p_k1.metric("Venta Bruta Total", f"${total_bruto:,.0f}")
  p_k2.metric(
      "Descuentos & Cortesías",
      f"{desc_pct_avg:.1f}%",
      delta=f"-${desc_total:,.0f}",
  )
  p_k3.metric("Comisiones TPV / Apps %", f"{comis_tpv_avg:.1f}%")
  p_k4.metric("Rotación de Mesa (Vueltas/día)", f"{vueltas_avg:.2f} pax/asiento")
  p_k5.metric("Venta Mensual / Empleado", f"${venta_emp_avg:,.0f}")

  st.markdown("<br>", unsafe_allow_html=True)

  pos_col1, pos_col2 = st.columns(2)

  with pos_col1:
    st.markdown(
        "<div class='chart-header'>Mezcla de Canales de Venta (% por"
        " Sucursal)</div>",
        unsafe_allow_html=True,
    )
    fig_chan = px.bar(
        df_pos_filt,
        x="Sucursal",
        y=["Canal_Comedor_%", "Canal_Takeout_%", "Canal_Delivery_%"],
        labels={"value": "Porcentaje %", "variable": "Canal"},
        template="plotly_white",
        color_discrete_sequence=[COLOR_RED, COLOR_GOLD, COLOR_BLUE],
    )
    fig_chan.update_layout(
        barmode="stack",
        height=260,
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )
    st.plotly_chart(fig_chan, use_container_width=True)

    st.markdown(
        "<div class='chart-header'>Controles POS: Descuentos/Cortesías vs"
        " Comisiones TPV & Delivery (%)</div>",
        unsafe_allow_html=True,
    )
    fig_ctrl = go.Figure()
    fig_ctrl.add_trace(
        go.Bar(
            x=df_pos_filt["Sucursal"],
            y=df_pos_filt["Descuentos_Cortesias_%"],
            name="Descuentos & Cortesías %",
            marker_color=COLOR_PURPLE,
        )
    )
    fig_ctrl.add_trace(
        go.Bar(
            x=df_pos_filt["Sucursal"],
            y=df_pos_filt["Comision_TPV_Delivery_%"],
            name="Comisiones TPV & Delivery %",
            marker_color=COLOR_CYAN,
        )
    )
    fig_ctrl.update_layout(
        barmode="group",
        template="plotly_white",
        height=260,
        margin=dict(t=10, b=10, l=10, r=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )
    st.plotly_chart(fig_ctrl, use_container_width=True)

  with pos_col2:
    st.markdown(
        "<div class='chart-header'>Mix de Producto por Categoría (%)</div>",
        unsafe_allow_html=True,
    )
    fig_cat = px.bar(
        df_pos_filt,
        x="Sucursal",
        y=[
            "Cat_Alimentos_%",
            "Cat_Bebidas_NoAlc_%",
            "Cat_Bebidas_Alc_%",
            "Cat_Postres_%",
        ],
        labels={"value": "Porcentaje %", "variable": "Categoría"},
        template="plotly_white",
        color_discrete_sequence=[COLOR_GREEN, COLOR_CYAN, COLOR_GOLD, COLOR_PURPLE],
    )
    fig_cat.upda
