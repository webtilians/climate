import numpy as np
import pandas as pd
import os
from geopy.distance import distance as geopy_distance

# Configurar parámetros de simulación
N = 10000  # Aumentar el número de muestras para cubrir escenarios variados
np.random.seed(42)  # Para reproducibilidad

# Coordenadas del hogar del usuario (ejemplo)
coordenadas_hogar = (40.4168, -3.7038)  # Madrid, España

# Generar perfiles de usuario
perfiles_usuario = [
    {"nombre": "trabajador", "temp_pref_dia": 22, "temp_pref_noche": 20},
    {"nombre": "hogareno", "temp_pref_dia": 24, "temp_pref_noche": 22},
    {"nombre": "viajero", "temp_pref_dia": 21, "temp_pref_noche": 19}
]

# Funciones auxiliares

def generar_geolocalizacion():
    # Generar coordenadas aleatorias cercanas al hogar
    lat = coordenadas_hogar[0] + np.random.uniform(-0.1, 0.1)
    lon = coordenadas_hogar[1] + np.random.uniform(-0.1, 0.1)
    return (lat, lon)

def esta_en_casa(coordenadas_usuario):
    # Calcular la distancia al hogar
    distancia = geopy_distance(coordenadas_hogar, coordenadas_usuario).km
    return distancia < 0.5  # Considerar "en casa" si está a menos de 500 metros

def generar_comando_voz(hora):
    comandos = ["encender", "apagar", "subir temperatura", "bajar temperatura"]
    if hora < 6 or hora > 22:
        return "apagar"
    return np.random.choice(comandos)

def generar_ocupacion():
    return np.random.choice(["ocupado", "vacío"], p=[0.7, 0.3])

def generar_temperatura(epoca, hora):
    # Rango de temperaturas según la época del año y la hora
    if epoca == "verano":
        if 8 <= hora < 12:
            return np.random.uniform(18, 24)
        elif 12 <= hora < 16:
            return np.random.uniform(24, 35)
        elif 16 <= hora < 20:
            return np.random.uniform(30, 35)
        elif 20 <= hora < 24:
            return np.random.uniform(20, 30)
        else:
            return np.random.uniform(15, 20)
    elif epoca == "otoño":
        return generar_temperatura("verano", hora) - 5
    elif epoca == "invierno":
        return generar_temperatura("verano", hora) - 10
    elif epoca == "primavera":
        return generar_temperatura("otoño", hora)
    else:
        raise ValueError("Época del año no válida")

# Función para generar datos simulados
def generar_datos():
    horas = np.random.randint(0, 24, N)  # Hora del día (0 a 23)
    epocas = np.random.choice(["invierno", "primavera", "verano", "otoño"], N)

    # Generar temperaturas basadas en la época del año y la hora
    temp_exterior = [generar_temperatura(epoca, hora) for epoca, hora in zip(epocas, horas)]

    # Asignar perfiles aleatorios a los usuarios
    perfiles = np.random.choice(perfiles_usuario, N)

    # Generar datos en función del perfil y la hora
    temp_interior = []
    consumo_energetico = []
    eficiencia = np.random.uniform(0.8, 1.2, N)  # Eficiencia energética del climatizador
    comandos_voz = []
    ocupacion = []
    ubicaciones = []
    en_casa = []

    for ext, h, perfil, ef in zip(temp_exterior, horas, perfiles, eficiencia):
        # Elegir la temperatura preferida según el horario
        if 6 <= h <= 22:
            temp_pref = perfil["temp_pref_dia"]
        else:
            temp_pref = perfil["temp_pref_noche"]

        # Calcular temperatura interior y consumo energético
        temp_interior.append(temp_pref)
        consumo = abs(ext - temp_pref) * ef  # Consumo proporcional a la diferencia y eficiencia
        consumo_energetico.append(consumo)

        # Generar comando de voz
        comandos_voz.append(generar_comando_voz(h))

        # Generar ocupación de habitación
        ocupacion.append(generar_ocupacion())

        # Generar geolocalización y estado en casa
        ubicacion = generar_geolocalizacion()
        ubicaciones.append(ubicacion)
        en_casa.append(esta_en_casa(ubicacion))

    # Incorporar condiciones climáticas dinámicas
    humedad = np.random.uniform(30, 90, N)  # Humedad en porcentaje
    viento = np.random.uniform(0, 20, N)  # Velocidad del viento en km/h
    calidad_aire = np.random.uniform(0, 100, N)  # Calidad del aire (0 = malo, 100 = excelente)

    # Crear DataFrame
    datos = pd.DataFrame({
        "hora": horas,
        "epoca": epocas,
        "temp_exterior": temp_exterior,
        "temp_interior": temp_interior,
        "perfil_usuario": [p["nombre"] for p in perfiles],
        "consumo_energetico": consumo_energetico,
        "eficiencia": eficiencia,
        "humedad": humedad,
        "viento": viento,
        "calidad_aire": calidad_aire,
        "comando_voz": comandos_voz,
        "ocupacion": ocupacion,
        "ubicacion": ubicaciones,
        "en_casa": en_casa
    })

    # Guardar los datos en un archivo CSV
    if not os.path.exists("../data"):
        os.makedirs("../data")
    datos.to_csv("../data/datos_climatizador.csv", index=False)

    print("Datos simulados generados y guardados en 'data/datos_climatizador.csv'.")

if __name__ == "__main__":
    generar_datos()
