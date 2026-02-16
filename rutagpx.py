import gpxpy
import folium
import os
import exifread


# CONFIGURACIÓN

gpx_file_path = "rutaSTAR.gpx"
fotos_dir = "fotos"


# LEER GPX

if not os.path.exists(gpx_file_path):
    print("❌ Archivo GPX no encontrado")
    exit()

with open(gpx_file_path, "r", encoding="utf-8") as gpx_file:
    gpx = gpxpy.parse(gpx_file)

latitudes = []
longitudes = []

for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            latitudes.append(float(point.latitude))
            longitudes.append(float(point.longitude))

if len(latitudes) == 0:
    print("❌ No se encontraron puntos en el GPX")
    exit()

print("✅ Ruta cargada correctamente")

# CREAR MAPA

mapa = folium.Map(
    location=[latitudes[0], longitudes[0]],
    zoom_start=15
)

# Dibujar ruta
folium.PolyLine(
    list(zip(latitudes, longitudes)),
    color="blue",
    weight=4
).add_to(mapa)

# FUNCIONES PARA EXTRAER GPS EXIF

def convertir_a_decimal(valores):
    grados = float(valores[0].num) / float(valores[0].den)
    minutos = float(valores[1].num) / float(valores[1].den)
    segundos = float(valores[2].num) / float(valores[2].den)
    return grados + (minutos / 60.0) + (segundos / 3600.0)

def obtener_gps(ruta_imagen):
    try:
        with open(ruta_imagen, 'rb') as f:
            tags = exifread.process_file(f)

        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:

            lat = convertir_a_decimal(tags['GPS GPSLatitude'].values)
            lon = convertir_a_decimal(tags['GPS GPSLongitude'].values)

            if tags['GPS GPSLatitudeRef'].values != 'N':
                lat = -lat

            if tags['GPS GPSLongitudeRef'].values != 'E':
                lon = -lon

            return lat, lon

    except:
        return None

    return None

# AGREGAR FOTOS COMO MARCADORES

if os.path.exists(fotos_dir):

    for archivo in os.listdir(fotos_dir):

        if archivo.lower().endswith((".jpg", ".jpeg")):

            ruta_img = os.path.join(fotos_dir, archivo)
            gps = obtener_gps(ruta_img)

            if gps:
                lat, lon = gps

                html = f"""
                <div>
                    <b>{archivo}</b><br>
                    <a href="fotos/{archivo}" target="_blank">
                        Abrir imagen
                    </a>
                </div>
                """

                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(html, max_width=250),
                    icon=folium.Icon(color="red", icon="camera")
                ).add_to(mapa)

                print(f"✅ Foto agregada: {archivo}")

            else:
                print(f"⚠ No tiene GPS: {archivo}")


# GUARDAR MAPA


mapa.save("mapa_con_fotos.html")
print("✅ Mapa generado: mapa_con_fotos.html")

# -------------------------------------------------
# 7️⃣ CREAR MAPA 3D CON MAPA BASE VISIBLE
# -------------------------------------------------

import pydeck as pdk

# Crear capa de ruta 3D
layer = pdk.Layer(
    "PathLayer",
    data=[{
        "path": list(zip(longitudes, latitudes)),
        "color": [0, 0, 255],
        "width": 5
    }],
    get_path="path",
    get_color="color",
    width_scale=1,
    width_min_pixels=2
)

# Vista inicial
view_state = pdk.ViewState(
    latitude=latitudes[0],
    longitude=longitudes[0],
    zoom=16,
    pitch=50,   # inclinación 3D
    bearing=0
)

# Crear mapa 3D con estilo OpenStreetMap
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_provider="carto",   # importante
    map_style="light"       # estilo visible sin token
)

# Guardar archivo
deck.to_html("mapa_3D.html")

print("✅ Mapa 3D generado correctamente: mapa_3D.html")

# -------------------------------------------------
# 8️⃣ AGREGAR FOTOS AL MAPA 3D
# -------------------------------------------------

import pydeck as pdk
import exifread

datos_fotos_3d = []

def convertir_a_decimal(valores):
    grados = float(valores[0].num) / float(valores[0].den)
    minutos = float(valores[1].num) / float(valores[1].den)
    segundos = float(valores[2].num) / float(valores[2].den)
    return grados + (minutos / 60.0) + (segundos / 3600.0)

def obtener_gps(ruta_imagen):
    try:
        with open(ruta_imagen, 'rb') as f:
            tags = exifread.process_file(f)

        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:

            lat = convertir_a_decimal(tags['GPS GPSLatitude'].values)
            lon = convertir_a_decimal(tags['GPS GPSLongitude'].values)

            if tags['GPS GPSLatitudeRef'].values != 'N':
                lat = -lat

            if tags['GPS GPSLongitudeRef'].values != 'E':
                lon = -lon

            return lat, lon
    except:
        return None
    return None

# Leer fotos
for archivo in os.listdir("fotos"):
    if archivo.lower().endswith((".jpg", ".jpeg")):
        ruta_img = os.path.join("fotos", archivo)
        gps = obtener_gps(ruta_img)
        if gps:
            lat, lon = gps
            datos_fotos_3d.append({
                "lat": lat,
                "lon": lon,
                "nombre": archivo,
                "ruta": f"fotos/{archivo}"
            })

# Capa de puntos para fotos
layer_fotos = pdk.Layer(
    "ScatterplotLayer",
    data=datos_fotos_3d,
    get_position='[lon, lat]',
    get_color='[255, 0, 0]',
    get_radius=8,
    pickable=True
)

# Recrear el mapa 3D incluyendo fotos
deck = pdk.Deck(
    layers=[layer, layer_fotos],  # ruta + fotos
    initial_view_state=view_state,
    map_provider="carto",
    map_style="light",
    tooltip={
        "html": "<b>{nombre}</b><br/>Click derecho → abrir imagen",
        "style": {"color": "white"}
    }
)

deck.to_html("mapa_3D_con_fotos.html")

print("✅ Mapa 3D con fotos generado: mapa_3D_con_fotos.html")
