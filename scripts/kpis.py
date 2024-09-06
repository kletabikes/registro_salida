import streamlit as st
import pandas as pd
import plotly.express as px
from fetch_data.fetch_subscriptions import fetch_subscriptions_data

def main():
    st.title("Registro de salidas")

    try:
        df = fetch_subscriptions_data()
        if df.empty:
            st.warning("No se encontraron datos.")
        else:
            st.sidebar.title("Filtros")

            # Definir el rango máximo de fechas disponible en los datos
            min_date = df['fecha_de_inicio'].min().date()
            max_date = df['fecha_de_inicio'].max().date()

            # Filtro de rango de fechas hasta la última fecha disponible
            start_date, end_date = st.sidebar.slider(
                "Selecciona un rango de fechas",
                min_value=min_date,
                max_value=max_date,
                value=(min_date, max_date),
                format="YYYY-MM-DD"
            )

            # Filtro de ciudad
            ciudades = df['ciudad'].unique().tolist()
            ciudad_seleccionada = st.sidebar.multiselect(
                "Ciudad", ciudades, default=ciudades
            )

            # Filtro de tipo de bicicleta, mostrando solo 'Mecanica' por defecto
            tipos_bicis = df['tipo'].unique().tolist()
            tipo_seleccionado = st.sidebar.multiselect(
                "Selecciona uno o más tipos de bicicletas", tipos_bicis, default=["MECANICA"]
            )

            # Filtro de tipo de plan (ya no incluye "Todos")
            planes = df['plan'].unique().tolist()
            plan_seleccionado = st.sidebar.multiselect(
                "Selecciona uno o más tipos de plan", planes
            )

            # Filtro de granularidad de tiempo (día, semana, mes, trimestre)
            granularidad = st.sidebar.selectbox(
                "Selecciona la granularidad de los datos", 
                ["Día", "Semana", "Mes", "Trimestre"]
            )

            # Si no se ha seleccionado ningún plan, no mostrar gráficos
            if plan_seleccionado:
                # Filtrar los datos según el rango de fechas, ciudad, tipo de bici y plan
                df_filtered = df[
                    (df['fecha_de_inicio'].dt.date >= start_date) &
                    (df['fecha_de_inicio'].dt.date <= end_date) &
                    (df['ciudad'].isin(ciudad_seleccionada)) &
                    (df['tipo'].isin(tipo_seleccionado)) &
                    (df['plan'].isin(plan_seleccionado))
                ]

                # Función para aplicar la granularidad
                def aplicar_granularidad(df, granularidad):
                    if granularidad == "Día":
                        return df['fecha_de_inicio'].dt.date
                    elif granularidad == "Semana":
                        return df['fecha_de_inicio'].dt.to_period('W').apply(lambda r: r.start_time)
                    elif granularidad == "Mes":
                        return df['fecha_de_inicio'].dt.to_period('M').apply(lambda r: r.start_time)
                    elif granularidad == "Trimestre":
                        return df['fecha_de_inicio'].dt.to_period('Q').apply(lambda r: r.start_time)

                # Separar los gráficos por cada plan seleccionado
                for plan in plan_seleccionado:
                    st.subheader(f"Registro de salidas de bicicletas para el plan: {plan}")

                    # Filtrar datos por el plan actual
                    plan_filtered = df_filtered[df_filtered['plan'] == plan]

                    # Aplicar la granularidad
                    plan_filtered['fecha_agrupada'] = aplicar_granularidad(plan_filtered, granularidad)

                    # Agrupar por la fecha agrupada y contar cuántas bicicletas salieron por intervalo
                    bikes_per_day = plan_filtered.groupby('fecha_agrupada').size().reset_index(name='count')

                    # Crear el gráfico dinámico con Plotly para este plan
                    fig = px.line(bikes_per_day, x='fecha_agrupada', y='count',
                                  title=f'Salidas de bicicletas por {granularidad.lower()} para el plan {plan}',
                                  labels={'fecha_agrupada': 'Fecha', 'count': 'Cantidad de salidas'},
                                  template='plotly_white')

                    # Mostrar el gráfico en Streamlit
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Por favor selecciona al menos un plan para ver los gráficos.")

    except ConnectionError as e:
        st.error(f"Error al obtener los datos: {e}")

if __name__ == "__main__":
    main()
