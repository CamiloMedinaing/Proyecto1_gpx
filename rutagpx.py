#code:cp1252
import gpxpy
import folium
import plotly.graph_objects as go
import os
from PIL import Image
import exifread
import base64

# ---------------------------
# FUNCIONES AUXILIARES
# ---------------------------

def convertir_a_grados(valor):
    """Convierte coordenadas EXIF a grados decimales"""
    d = float(valor.values[0].num) / float(valor.values[0].den)
    m = float(valor.values[1].num) / float(valor.values[1].den)
    s = float(valor.values[2].num) / float(valor.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)

def obtener_gps_imagen(ruta_imagen):
    """Extrae latitud y longitud desde EXIF"""
    with open(ruta_imagen, 'rb') as f:
        tags = exifread.process_file(f)

    if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
        lat = convertir_a_grados(tags['GPS GPSLatitude'])
        lon = convertir_a_grados(tags['GPS GPSLongitude'])

        if tags.get('GPS GPSLatitudeRef').values != 'N':
            lat = -lat
        if tags.get('GPS GPSLongitudeRef').values != 'E':
            lon = -lon

        return lat, lon
    return None

def imagen_a_base64(ruta):
    """Convierte imagen en base64 para mostrarla en el popup"""
    with open(ruta, "rb") as img:
        return base64.b64encode(img.read()).decode()

# ---------------------------
# 1️⃣ LEER GPX
# ---------------------------

with open("ruta.gpx", "r", encoding="utf-8") as gpx_file:
    gpx = gpxpy.parse(gpx_file)

latitudes = []
longitudes = []
elevaciones = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            latitudes.append(point.latitude)
            longitudes.append(point.longitude)
            elevaciones.append(point.elevation)

# ---------------------------
# 2️⃣ MAPA 2D (FOLIUM)
# ---------------------------

mapa_2d = folium.Map(location=[latitudes[0], longitudes[0]], zoom_start=15)

# Dibujar ruta
folium.PolyLine(list(zip(latitudes, longitudes)), color="blue").add_to(mapa_2d)

# ---------------------------
# 3️⃣ AGREGAR FOTOS
# ---------------------------

carpeta_fotos = "fotos"

for archivo in os.listdir(carpeta_fotos):
    if archivo.lower().endswith((".jpg", ".jpeg")):
        ruta_imagen = os.path.join(carpeta_fotos, archivo)
        gps = obtener_gps_imagen(ruta_imagen)

        if gps:
            lat, lon = gps
            img_base64 = imagen_a_base64(ruta_imagen)

            html = f'<img src="data:image/jpeg;base64,{img_base64}" width="300">'
            iframe = folium.IFrame(html, width=320, height=320)
            popup = folium.Popup(iframe)

            folium.Marker(
                location=[lat, lon],
                popup=popup,
                icon=folium.Icon(color="red", icon="camera")
            ).add_to(mapa_2d)

mapa_2d.save("mapa_2D.html")

# ---------------------------
# 4️⃣ MAPA 3D (PLOTLY)
# ---------------------------

fig = go.Figure()

fig.add_trace(go.Scatter3d(
    x=longitudes,
    y=latitudes,
    z=elevaciones,
    mode='lines',
    line=dict(color='blue', width=4),
    name='Ruta GPX'
))

fig.update_layout(
    scene=dict(
        xaxis_title='Longitud',
        yaxis_title='Latitud',
        zaxis_title='Elevación'
    ),
    title="Visualización 3D de Ruta GPX"
)

fig.write_html("mapa_3D.html")

print("✅ Mapa 2D guardado como mapa_2D.html")
print("✅ Mapa 3D guardado como mapa_3D.html")
