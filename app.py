import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Generar datos de prueba
np.random.seed(42)  # Para reproducibilidad
n = 365  # Número de entradas (un año completo)

# Crear un DataFrame de prueba
data = {
    'Fecha': pd.date_range(start='2023-01-01', end='2023-12-31', freq='D'),
    'Repuesto': np.random.choice(['Filtro', 'Aceite', 'Bujía', 'Correa', 'Batería'], size=n),
    'Cantidad_Vendida': np.random.randint(1, 20, size=n),
    'Inventario': np.random.randint(20, 100, size=n)
}

df = pd.DataFrame(data)

# Configuración del ancho del dashboard
st.set_page_config(page_title='Dashboard de Repuestos', layout='wide')

# Crear un panel de navegación y filtros en la barra lateral
with st.sidebar:
    st.header("Navegación y Filtros")
    
    with st.expander("Menú de Navegación", expanded=False):
        st.markdown("### Tableros")
        option = st.selectbox("Selecciona un tablero:", ["Ventas", "Inventario", "Análisis"])
    
    st.markdown("### Filtros")
    
    # Filtro de fecha
    min_date = df['Fecha'].min().date()
    max_date = df['Fecha'].max().date()
    start_date = st.date_input("Fecha inicial", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("Fecha final", max_date, min_value=start_date, max_value=max_date)
    
    if start_date > end_date:
        st.error('La fecha final debe ser posterior a la fecha inicial.')
    
    # Filtro de categoría de repuesto
    categorias = ['Todos'] + list(df['Repuesto'].unique())
    categoria_seleccionada = st.multiselect('Categoría de Repuesto', categorias, default=['Todos'])
    
    if not categoria_seleccionada:
        st.warning('Por favor, selecciona al menos una categoría.')
        categoria_seleccionada = ['Todos']
    
    # Filtro de cantidad vendida
    min_venta, max_venta = int(df['Cantidad_Vendida'].min()), int(df['Cantidad_Vendida'].max())
    rango_ventas = st.slider('Rango de Cantidad Vendida', min_venta, max_venta, (min_venta, max_venta))
    
    # Filtro de inventario
    min_inv, max_inv = int(df['Inventario'].min()), int(df['Inventario'].max())
    rango_inventario = st.slider('Rango de Inventario', min_inv, max_inv, (min_inv, max_inv))

# Aplicar filtros
mask = (
    (df['Fecha'].dt.date >= start_date) &
    (df['Fecha'].dt.date <= end_date) &
    (df['Cantidad_Vendida'].between(rango_ventas[0], rango_ventas[1])) &
    (df['Inventario'].between(rango_inventario[0], rango_inventario[1]))
)

if 'Todos' not in categoria_seleccionada:
    mask &= df['Repuesto'].isin(categoria_seleccionada)

df_filtered = df[mask]

# Resto del código del dashboard (sin cambios)
# Agregar el logo y el título en la parte superior
col1, col2 = st.columns([1, 3])

with col1:
    st.image("logo.PNG", width=100)

with col2:
    st.title('Dashboard de Ventas AGROANCO')

# Calcular KPIs con datos filtrados
ventas_totales = df_filtered['Cantidad_Vendida'].sum()
categoria_mas_vendida = df_filtered.groupby('Repuesto')['Cantidad_Vendida'].sum().idxmax()
inventario_total = df_filtered['Inventario'].sum()
promedio_inventario = df_filtered['Inventario'].mean()

# Definir la meta de ventas del mes
meta_ventas = 7000

# Crear un gauge para medir el progreso de las ventas (estilo semáforo)
gauge_fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=ventas_totales,
    domain={'x': [0, 1], 'y': [0, 1]},
    delta={'reference': meta_ventas, 'position': "top"},
    number={'font': {'size': 20}},
    title={'text': "Plan de Ventas", 'font': {'size': 14}},
    gauge={
        'axis': {'range': [None, meta_ventas * 1.2], 'tickwidth': 1, 'tickcolor': "darkblue", 'tickfont': {'size': 10}},
        'bar': {'color': "darkblue"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, meta_ventas * 0.6], 'color': "red"},
            {'range': [meta_ventas * 0.6, meta_ventas * 0.8], 'color': "yellow"},
            {'range': [meta_ventas * 0.8, meta_ventas * 1.2], 'color': "green"}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': meta_ventas
        }
    }
))

gauge_fig.update_layout(
    height=150, 
    width=200,
    margin=dict(t=30, b=0, l=0, r=0),
    autosize=False
)

# Crear una fila con cinco columnas
cols = st.columns(5)

# Estilo CSS para las tarjetas
card_style = """
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    margin: 10px 0;
    background-color: white;
    height: 150px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
"""

# Mostrar el gauge en la primera columna
with cols[0]:
    #st.plotly_chart(gauge_fig, use_container_width=True)
    st.plotly_chart(gauge_fig, use_container_width=False, config={'displayModeBar': False})

# Datos para las tarjetas
card_data = [
    {"title": "Ventas Totales", "value": f"{ventas_totales:,}"},
    {"title": "Categoría Más Vendida", "value": categoria_mas_vendida},
    {"title": "Inventario Total", "value": f"{inventario_total:,}"},
    {"title": "Promedio de Inventario", "value": f"{promedio_inventario:.2f}"}
]

# Agregar 4 tarjetas en las columnas restantes
for i, data in enumerate(card_data, start=1):
    with cols[i]:
        st.markdown(f"""
        <div style="{card_style}">
            <p style="font-size: 14px; margin-bottom: 5px; color: #666;">{data['title']}</p>
            <p style="font-size: 24px; font-weight: bold; margin: 0;">{data['value']}</p>
        </div>
        """, unsafe_allow_html=True)

# Crear cuatro gráficas adicionales
st.markdown("### Análisis Detallado")

# Primera fila de gráficas
col1, col2 = st.columns(2)


with col1:
    ventas_por_categoria = df_filtered.groupby('Repuesto')['Cantidad_Vendida'].sum().sort_values(ascending=False).reset_index()
    fig1 = px.bar(ventas_por_categoria, x='Repuesto', y='Cantidad_Vendida', 
                  title='Ventas por Categoría de Repuesto',
                  color='Cantidad_Vendida', color_continuous_scale='Viridis')
    fig1.update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    ventas_mensuales = df_filtered.groupby(df_filtered['Fecha'].dt.to_period('M'))['Cantidad_Vendida'].sum().reset_index()
    ventas_mensuales['Fecha'] = ventas_mensuales['Fecha'].dt.to_timestamp()
    fig2 = px.line(ventas_mensuales, x='Fecha', y='Cantidad_Vendida', 
                   title='Ventas Mensuales',
                   line_shape='linear')  # Cambiado a 'linear' para líneas rectas
    fig2.update_traces(line_color='#FF4136', line_width=2)
    fig2.update_layout(xaxis_title='Mes', yaxis_title='Cantidad Vendida')
    st.plotly_chart(fig2, use_container_width=True)

# Segunda fila de gráficas
col3, col4 = st.columns(2)

with col3:
    inventario_por_categoria = df_filtered.groupby('Repuesto')['Inventario'].sum().reset_index()
    fig3 = px.pie(inventario_por_categoria, values='Inventario', names='Repuesto', 
                  title='Distribución del Inventario por Categoría',
                  color_discrete_sequence=px.colors.qualitative.Set3)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    top_5_dias = df_filtered.groupby('Fecha')['Cantidad_Vendida'].sum().nlargest(5).reset_index()
    fig4 = px.bar(top_5_dias, x='Fecha', y='Cantidad_Vendida',
                  title='Top 5 Días con Mayores Ventas',
                  color='Cantidad_Vendida', color_continuous_scale='YlOrRd')
    st.plotly_chart(fig4, use_container_width=True)

# Datos de Prueba
st.subheader('Datos Filtrados')
st.dataframe(df_filtered)