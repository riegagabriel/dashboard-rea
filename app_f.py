"""TEXTOS Y TITULOS: se editan en configuracion.toml, no aqui.

Prototipo F - Hibrido: coropleta departamental en gris + burbujas distritales.

El gris responde CUANTO por departamento; el color de la burbuja, DONDE y DE
QUE TIPO por distrito. Cada burbuja abre un popup con la observacion completa
de cada denuncia.

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
from rea.estilo import PROTOTIPO_F
from rea.mapas import mapa_f

pagina.configurar("F")
d = datos.cargar()
df = datos.casos_df()

pagina.encabezado(d["meta"], PROTOTIPO_F)
tipos, canales, deps = pagina.filtros(df)
f = datos.filtrar(df, tipos, canales, deps)

pagina.indicadores(f, len(df))

if f.empty:
    import streamlit as st
    st.warning("Ninguna denuncia cumple los filtros activos. "
               "Amplíe la selección en el panel lateral.")
else:
    por_tipo = f["tipo"].value_counts().to_dict()
    activos = set(f["ubigeo_inei"])
    territorios = [t for t in d["territorios"] if t["ubigeo_inei"] in activos]
    st_folium(mapa_f(datos.por_departamento(f), territorios,
                     datos.por_territorio(f), por_tipo),
              use_container_width=True, height=640,
              returned_objects=[], key="mapa_f")
    pagina.tablas(f)
    pagina.reservado(f)

pagina.pie(d["meta"], f, len(df))
