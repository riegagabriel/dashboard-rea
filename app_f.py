"""TEXTOS Y TITULOS: se editan en configuracion.toml, no aqui.

Prototipo F - Mapa intercambiable. Un selector sobre el mapa alterna entre:

  B  coropleta por departamento (la misma de la app B), con su leyenda.
  F  provincias sombreadas en una sola tinta, limites departamentales tenues y una
     burbuja por distrito, coloreada por tipo de denuncia. Al acercar aparecen los
     nombres de provincia y los limites de distrito. Solo lleva leyenda de tipo.

Mapa al 50 % de la pantalla; cifras, graficos y tabla en pagina.py.

Ejecutar en local:  streamlit run app_f.py
"""
import sys

# Streamlit Cloud reutiliza el proceso al actualizar el repo: sin esto, un rea/*.py
# viejo en memoria convive con este archivo ya nuevo y falla el import.
for _m in [m for m in sys.modules if m == "rea" or m.startswith("rea.")]:
    del sys.modules[_m]

import streamlit.components.v1 as componentes

from rea import datos, mapas, pagina, textos


def mapa(df, altura):
    t = textos.cargar()
    modo = pagina.selector_mapa(t)
    alto = altura - pagina.ALTO_SELECTOR
    html = (mapas.mapa_b_html if modo == "b" else mapas.mapa_f_html)(t.huella)
    # El mapa no devuelve nada a Streamlit, asi que basta un iframe con el HTML ya
    # renderizado (st_folium volveria a renderizar el objeto en cada ejecucion).
    componentes.html(html, height=alto, scrolling=False)


pagina.configurar("F")
d = datos.cargar()
pagina.encabezado(d["meta"], "f")
pagina.tablero(datos.casos_df(), mapa)
