"""Prototipo B - Coropleta departamental.

La magnitud por departamento se lee de un vistazo a escala nacional, con el
numero impreso sobre cada uno. Al acercar aparecen los limites provinciales y
distritales.

Ejecutar en local:  streamlit run app_b.py
"""
from streamlit_folium import st_folium

from rea import datos, pagina
from rea.mapas import mapa_b

pagina.configurar("B")
d = datos.cargar()
df = datos.casos_df()

pagina.encabezado(d["meta"], "B · coropleta departamental")
tipos, canales, deps = pagina.filtros(df)
f = datos.filtrar(df, tipos, canales, deps)

pagina.indicadores(f, len(df))

if f.empty:
    import streamlit as st
    st.warning("Ninguna denuncia cumple los filtros activos. "
               "Amplíe la selección en el panel lateral.")
else:
    por_tipo = f["tipo"].value_counts().to_dict()
    st_folium(mapa_b(datos.por_departamento(f), por_tipo),
              use_container_width=True, height=640,
              returned_objects=[], key="mapa_b")
    pagina.tablas(f)
    pagina.reservado(f)

pagina.pie(d["meta"], f, len(df))
