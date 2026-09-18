"""TEXTOS Y TITULOS: se editan en configuracion.toml, no aqui.

Prototipo B - Coropleta departamental.

La magnitud por departamento se lee de un vistazo a escala nacional, con el
numero impreso sobre cada uno. Al acercar aparecen los limites provinciales y
distritales. Mapa al 50 % de la pantalla; cifras, graficos y tabla en pagina.py.

Ejecutar en local:  streamlit run app_b.py
"""
import sys

# Streamlit Cloud reutiliza el proceso al actualizar el repo: sin esto, un rea/*.py
# viejo en memoria convive con este archivo ya nuevo y falla el import.
for _m in [m for m in sys.modules if m == "rea" or m.startswith("rea.")]:
    del sys.modules[_m]

from streamlit_folium import st_folium

from rea import datos, pagina
from rea.mapas import mapa_b


def mapa(f, altura):
    st_folium(mapa_b(datos.por_departamento(f), f["tipo"].value_counts().to_dict()),
              use_container_width=True, height=altura,
              returned_objects=[], key="mapa_b")


pagina.configurar("B")
d = datos.cargar()
pagina.encabezado(d["meta"], "b")
pagina.tablero(datos.casos_df(), mapa)
