"""TEXTOS Y TITULOS: se editan en configuracion.toml, no aqui.

Prototipo F - Hibrido: coropleta departamental en gris + burbujas distritales.

El gris responde CUANTO por departamento; el color de la burbuja, DONDE y DE
QUE TIPO por distrito. Cada burbuja abre un popup con la observacion completa
de cada denuncia. Mapa al 50 % de la pantalla; cifras, graficos y tabla en pagina.py.

Por que el fondo es gris y no una rampa azul: una rampa azul bajo marcadores
azules pondria magnitud e identidad en la misma familia de color. Y la rampa se
corta en #dcd8cd porque mas oscuro borra los marcadores justo donde hay mas
datos (medido: sobre #7a756a los cuatro colores caen por debajo de 2:1).

Ejecutar en local:  streamlit run app_f.py
"""
import sys

# Streamlit Cloud reutiliza el proceso al actualizar el repo: sin esto, un rea/*.py
# viejo en memoria convive con este archivo ya nuevo y falla el import.
for _m in [m for m in sys.modules if m == "rea" or m.startswith("rea.")]:
    del sys.modules[_m]

from streamlit_folium import st_folium

from rea import datos, pagina
from rea.mapas import mapa_f


def mapa(f, altura):
    activos = set(f["ubigeo_inei"])
    territorios = [t for t in d["territorios"] if t["ubigeo_inei"] in activos]
    st_folium(mapa_f(datos.por_departamento(f), territorios,
                     datos.por_territorio(f), f["tipo"].value_counts().to_dict()),
              use_container_width=True, height=altura,
              returned_objects=[], key="mapa_f")


pagina.configurar("F")
d = datos.cargar()
pagina.encabezado(d["meta"], "f")
pagina.tablero(datos.casos_df(), mapa)
