import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

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

# Necesario para que Render reconozca la aplicación
server = app.server

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

# Callbacks (sin cambios)
# ...

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=False)  # Desactiva el modo de depuración en producción
