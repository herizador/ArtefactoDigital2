import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os

# Cambia el directorio de trabajo si es necesario
os.chdir('C:/Users/id386/Downloads/Artefacto Digital 2')

# Cargar los archivos con el separador correcto y verificar el encoding
try:
    humedad_minima = pd.read_csv('HumedadMinima.txt', sep=';', encoding='utf-8')
    humedad_maxima = pd.read_csv('HumedadMaxima.txt', sep=';', encoding='utf-8')
    temperatura_minima = pd.read_csv('TemperaturaMinima.txt', sep=';', encoding='utf-8')
    temperatura_maxima = pd.read_csv('TemperaturaMaxima.txt', sep=';', encoding='utf-8')
    lluvia = pd.read_csv('lluvia.txt', sep=';', encoding='utf-8')
except Exception as e:
    print(f"Error al cargar los archivos: {e}")

# Verificar que todos los archivos tengan la columna 'Fecha'
for df, nombre in zip(
    [humedad_minima, humedad_maxima, temperatura_minima, temperatura_maxima, lluvia],
    ['HumedadMinima', 'HumedadMaxima', 'TemperaturaMinima', 'TemperaturaMaxima', 'Lluvia']
):
    # Limpiar los nombres de las columnas (eliminar espacios adicionales)
    df.columns = df.columns.str.strip()
    
    if 'Fecha' not in df.columns:
        print(f"Advertencia: El archivo {nombre}.txt no tiene la columna 'Fecha'.")
        print(f"Columnas presentes: {df.columns.tolist()}")
    else:
        print(f"El archivo {nombre}.txt se cargó correctamente.")

# Combinar todos los datos en un solo DataFrame
datos = pd.concat([humedad_minima, humedad_maxima, temperatura_minima, temperatura_maxima, lluvia])

# Verificar que la columna 'Fecha' esté presente en el DataFrame combinado
if 'Fecha' not in datos.columns:
    raise KeyError("La columna 'Fecha' no está presente en el DataFrame combinado.")

# Convertir la columna 'Fecha' a datetime
datos['Fecha'] = pd.to_datetime(datos['Fecha'], format='%d-%m-%Y')

# Convertir la columna 'Valor' a tipo numérico (float)
# Reemplazar comas por puntos y convertir a float
datos['Valor'] = datos['Valor'].str.replace(',', '.').astype(float)

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Estilo CSS personalizado
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Diseño del dashboard
app.layout = html.Div([
    html.H1("Dashboard Meteorológico de Torla (2014-2024)", style={'textAlign': 'center', 'color': '#2c3e50', 'fontFamily': 'Arial, sans-serif'}),
    
    html.Div([
        html.Label("Selecciona una variable:", style={'fontSize': '20px', 'fontFamily': 'Arial, sans-serif'}),
        dcc.Dropdown(
            id='variable-dropdown',
            options=[
                {'label': 'Temperatura Mínima', 'value': 'Temperatura Mínima'},
                {'label': 'Temperatura Máxima', 'value': 'Temperatura Máxima'},
                {'label': 'Humedad Mínima', 'value': 'Humedad Mínima'},
                {'label': 'Humedad Máxima', 'value': 'Humedad Máxima'},
                {'label': 'Lluvia máxima', 'value': 'Lluvia máxima'}
            ],
            value='Temperatura Mínima',  # Valor por defecto
            style={'width': '50%', 'margin': 'auto', 'fontFamily': 'Arial, sans-serif'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.DatePickerRange(
            id='date-range',
            start_date=datos['Fecha'].min(),
            end_date=datos['Fecha'].max(),
            display_format='YYYY-MM-DD',
            style={'fontFamily': 'Arial, sans-serif'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Graph(id='grafico-evolucion'),
    ], style={'width': '80%', 'margin': 'auto', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Graph(id='grafico-temperatura-media'),
    ], style={'width': '80%', 'margin': 'auto', 'marginBottom': '20px'}),
    
    html.Div([
        dcc.Graph(id='grafico-correlacion'),
    ], style={'width': '80%', 'margin': 'auto', 'marginBottom': '20px'}),
])

# Callback para actualizar el gráfico de evolución
@app.callback(
    Output('grafico-evolucion', 'figure'),
    [Input('variable-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_grafico(selected_variable, start_date, end_date):
    filtered_data = datos[(datos['Nombre de la variable'] == selected_variable) & 
                          (datos['Fecha'] >= start_date) & 
                          (datos['Fecha'] <= end_date)]
    fig = px.line(filtered_data, x='Fecha', y='Valor', 
                  title=f'Evolución de {selected_variable} en Torla',
                  labels={'Valor': selected_variable, 'Fecha': 'Fecha'},
                  template='plotly_dark',
                  line_shape='spline',
                  hover_data={'Valor': ':.2f'})
    fig.update_traces(line=dict(width=2.5))
    return fig

# Callback para actualizar el gráfico de temperatura media por año
@app.callback(
    Output('grafico-temperatura-media', 'figure'),
    [Input('variable-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_grafico_temperatura(selected_variable, start_date, end_date):
    # Filtrar datos de temperatura mínima y máxima
    temp_min = datos[(datos['Nombre de la variable'] == 'Temperatura Mínima') & 
                     (datos['Fecha'] >= start_date) & 
                     (datos['Fecha'] <= end_date)]
    temp_max = datos[(datos['Nombre de la variable'] == 'Temperatura Máxima') & 
                     (datos['Fecha'] >= start_date) & 
                     (datos['Fecha'] <= end_date)]
    
    # Calcular la temperatura media por año
    temp_min_anual = temp_min.groupby(temp_min['Fecha'].dt.year)['Valor'].mean().reset_index()
    temp_max_anual = temp_max.groupby(temp_max['Fecha'].dt.year)['Valor'].mean().reset_index()
    
    # Combinar los datos de temperatura mínima y máxima
    temp_media_anual = pd.merge(temp_min_anual, temp_max_anual, on='Fecha', suffixes=('_min', '_max'))
    temp_media_anual['Temperatura Media'] = (temp_media_anual['Valor_min'] + temp_media_anual['Valor_max']) / 2
    
    # Crear el gráfico de barras
    fig = px.bar(temp_media_anual, x='Fecha', y='Temperatura Media', 
                 title='Temperatura Media por Año en Torla',
                 labels={'Temperatura Media': 'Temperatura Media (°C)', 'Fecha': 'Año'},
                 template='plotly_dark',
                 color='Temperatura Media',
                 color_continuous_scale='Viridis')
    return fig

# Callback para actualizar el gráfico de correlación
@app.callback(
    Output('grafico-correlacion', 'figure'),
    [Input('variable-dropdown', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_grafico_correlacion(selected_variable, start_date, end_date):
    # Filtrar datos de temperatura y humedad
    temp_min = datos[(datos['Nombre de la variable'] == 'Temperatura Mínima') & 
                     (datos['Fecha'] >= start_date) & 
                     (datos['Fecha'] <= end_date)]
    humedad_max = datos[(datos['Nombre de la variable'] == 'Humedad Máxima') & 
                        (datos['Fecha'] >= start_date) & 
                        (datos['Fecha'] <= end_date)]
    
    # Combinar los datos
    correlacion_data = pd.merge(temp_min, humedad_max, on='Fecha', suffixes=('_temp', '_hum'))
    
    # Crear el gráfico de dispersión
    fig = px.scatter(correlacion_data, x='Valor_temp', y='Valor_hum', 
                     title='Correlación entre Temperatura Mínima y Humedad Máxima',
                     labels={'Valor_temp': 'Temperatura Mínima (°C)', 'Valor_hum': 'Humedad Máxima (%)'},
                     template='plotly_dark',
                     color='Valor_temp',
                     color_continuous_scale='Viridis',
                     hover_data={'Valor_temp': ':.2f', 'Valor_hum': ':.2f'})
    return fig

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)