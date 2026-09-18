"""Construccion de los mapas Folium: coropleta departamental (B) y
provincias + distritos con burbujas (F). La app F deja elegir entre los dos."""
from __future__ import annotations

import math

import folium
import pandas as pd
import streamlit as st
from branca.element import MacroElement, Template
from shapely.geometry import shape

from . import datos
from .datos import geojson
from .estilo import (CATEGORIAS, CSS_MAPA, LIMITE_DEPARTAMENTO, ORDEN_CATEGORIAS,
                     RAMPA_AZUL, SIN_CASOS, T, TINTA_PROVINCIA)
from .textos import Textos, cargar as cargar_textos, clave

PERU = [[-18.6, -81.5], [0.2, -68.4]]
ZOOM_PROVINCIA = 7      # B: a partir de aqui aparecen los limites provinciales
ZOOM_DISTRITO = 9       # B: a partir de aqui, los distritales
ZOOM_NOMBRES = 7        # F: nombres de provincia
ZOOM_DISTRITO_F = 7.5   # F: limites distritales (2 clics desde el zoom inicial)


class LimitesPorZoom(MacroElement):
    """Muestra cada capa solo a partir de su zoom minimo.

    Se usa MacroElement y no un <script> suelto porque folium renderiza los
    macros DESPUES del mapa y de las capas: es el unico punto donde las
    variables JS de ambos ya existen. `capas` es una lista de (capa, zoom_minimo).
    """

    _template = Template("""
        {% macro script(this, kwargs) %}
        (function(){
          var mapa = {{ this._parent.get_name() }};
          var capas = [{% for nombre, z in this.capas %}[{{ nombre }}, {{ z }}]{% if not loop.last %},{% endif %}{% endfor %}];
          capas.forEach(function(c){ mapa.removeLayer(c[0]); });
          function ajustar(){
            var z = mapa.getZoom();
            capas.forEach(function(c){
              var visible = z >= c[1];
              if (visible && !mapa.hasLayer(c[0])) mapa.addLayer(c[0]);
              else if (!visible && mapa.hasLayer(c[0])) mapa.removeLayer(c[0]);
            });
          }
          mapa.on('zoomend', ajustar);
          ajustar();
        })();
        {% endmacro %}
    """)

    def __init__(self, capas):
        super().__init__()
        self._name = "LimitesPorZoom"
        self.capas = [(c.get_name(), z) for c, z in capas]


def _base() -> folium.Map:
    # Sin teselas: la coropleta es la superficie. Un basemap competiria con ella
    # y anadiria una dependencia de red que el entregable no necesita.
    # Peru ocupa unos 490 px de ancho a zoom 5.75; con el mapa al 50 % de la
    # pantalla llena el recuadro. El centro va corrido hacia el sur-oeste para que
    # el pais quede arriba a la derecha y la leyenda (abajo a la izquierda) caiga
    # sobre el oceano y no tape la costa. zoomSnap 0.25 es lo que permite un zoom
    # fraccionario: con el valor por defecto (1) Leaflet lo redondea a 6.
    m = folium.Map(location=[-10.9, -76.7], zoom_start=5.75, tiles=None,
                   control_scale=False, zoom_control=True,
                   min_zoom=4, max_bounds=True, zoomSnap=0.25)
    m.get_root().header.add_child(folium.Element(CSS_MAPA))
    return m


def _color_azul(n: int, vmax: int) -> str:
    if n <= 0:
        return SIN_CASOS
    i = min(int(math.ceil(n / max(vmax, 1) * len(RAMPA_AZUL))) - 1, len(RAMPA_AZUL) - 1)
    return RAMPA_AZUL[max(i, 0)]


def _capa_distritos(m: folium.Map, tx: Textos, punteado: bool) -> folium.GeoJson:
    mp = tx["mapa"]
    estilo = {"fillOpacity": 0, "color": "#b5b1a6" if punteado else "#bdbab1",
              "weight": 0.5 if punteado else 0.45}
    if punteado:
        estilo["dashArray"] = "2 2"
    capa = folium.GeoJson(
        geojson("distritos_contexto"), name="Distritos",
        style_function=lambda _: estilo,
        tooltip=folium.GeoJsonTooltip(
            fields=["DISTRITO", "PROVINCIA", "DEPARTAMEN"],
            aliases=[mp["tooltip_distrito"], mp["tooltip_provincia"], mp["tooltip_departamento"]],
            class_name="tt"))
    capa.add_to(m)
    return capa


def _contexto(m: folium.Map, tx: Textos) -> None:
    """Prototipo B: limites provinciales y distritales que aparecen al acercar."""
    mp = tx["mapa"]
    prov = folium.GeoJson(
        geojson("provincias"), name="Provincias",
        style_function=lambda _: {"fillOpacity": 0, "color": "#a8a59c",
                                  "weight": 0.6},
        tooltip=folium.GeoJsonTooltip(
            fields=["PROVINCIA", "DEPARTAMEN"],
            aliases=[mp["tooltip_provincia"], mp["tooltip_departamento"]],
            class_name="tt"))
    prov.add_to(m)
    dist = _capa_distritos(m, tx, punteado=False)
    m.add_child(LimitesPorZoom([(prov, ZOOM_PROVINCIA), (dist, ZOOM_DISTRITO)]))


def _departamentos(m: folium.Map, conteo: dict[str, int], tx: Textos) -> dict:
    """Capa departamental del prototipo B: coropleta azul con el numero impreso."""
    mp = tx["mapa"]
    gj = geojson("departamentos")
    vmax = max(conteo.values()) if conteo else 1
    for f in gj["features"]:
        n = int(conteo.get(f["properties"]["DEPARTAMEN"].title(), 0))
        f["properties"]["n"] = n
        f["properties"]["color"] = _color_azul(n, vmax)

    capa = folium.FeatureGroup(name="Departamentos", show=True)
    folium.GeoJson(
        gj,
        style_function=lambda f: {"fillColor": f["properties"]["color"],
                                  "fillOpacity": 1.0, "color": T["linea"],
                                  "weight": 0.9},
        highlight_function=lambda _: {"color": T["tinta2"], "weight": 2.2},
        tooltip=folium.GeoJsonTooltip(
            fields=["DEPARTAMEN", "n"],
            aliases=[mp["tooltip_departamento"], mp["tooltip_denuncias"]],
            class_name="tt"),
    ).add_to(capa)

    # El numero impreso: la magnitud no queda solo en el color.
    for f in gj["features"]:
        if f["properties"]["n"] <= 0:
            continue
        pt = shape(f["geometry"]).representative_point()
        folium.Marker(
            [pt.y, pt.x],
            icon=folium.DivIcon(icon_size=(38, 18), icon_anchor=(19, 9),
                                class_name="num-dep",
                                html=f"<div>{f['properties']['n']}</div>"),
        ).add_to(capa)
    capa.add_to(m)
    return {"vmax": vmax}


def _provincias(m: folium.Map, conteo: dict[tuple[str, str], int], tx: Textos) -> None:
    """Prototipo F: una sola tinta en las provincias con denuncias; el tooltip da la cifra."""
    mp = tx["mapa"]
    gj = geojson("provincias")
    for f in gj["features"]:
        p = f["properties"]
        p["n"] = int(conteo.get((clave(p["DEPARTAMEN"]), clave(p["PROVINCIA"])), 0))
        p["rotulo"] = f'{p["PROVINCIA"].title()} ({p["DEPARTAMEN"].title()})'
    folium.GeoJson(
        gj, name="Provincias",
        style_function=lambda f: {
            "fillColor": TINTA_PROVINCIA if f["properties"]["n"] > 0 else SIN_CASOS,
            "fillOpacity": 1.0, "color": "#c9c5ba", "weight": 0.6},
        highlight_function=lambda _: {"color": T["tinta2"], "weight": 1.8},
        tooltip=folium.GeoJsonTooltip(
            fields=["rotulo", "n"],
            aliases=[mp["tooltip_provincia"], mp["tooltip_denuncias"]],
            class_name="tt"),
    ).add_to(m)


def _limites_departamentos(m: folium.Map) -> None:
    """Contorno departamental tenue. interactive=False: no le quita el hover a las provincias."""
    folium.GeoJson(
        geojson("departamentos"), name="Limites departamentales",
        style_function=lambda _: {"fillOpacity": 0, "color": LIMITE_DEPARTAMENTO,
                                  "weight": 0.9, "opacity": 0.85},
        interactive=False,
    ).add_to(m)


def _rotulos_provincia(m: folium.Map, conteo: dict[tuple[str, str], int]
                       ) -> folium.FeatureGroup:
    """Numero sobre las provincias con 2 o mas denuncias (siempre visible) y nombre de
    todas las que tienen denuncias (solo al acercar). Devuelve la capa de nombres."""
    centros = datos.centros_provincia()
    numeros = folium.FeatureGroup(name="Totales por provincia", show=True)
    nombres = folium.FeatureGroup(name="Nombres de provincia", show=True)
    for k, n in conteo.items():
        c = centros.get(k)
        if c is None or n <= 0:
            continue
        if n >= 2:
            folium.Marker(
                [c["lat"], c["lon"]], z_index_offset=1000,
                icon=folium.DivIcon(icon_size=(38, 18), icon_anchor=(19, 9),
                                    class_name="num-dep", html=f"<div>{n}</div>"),
            ).add_to(numeros)
        folium.Marker(
            [c["lat"], c["lon"]],
            icon=folium.DivIcon(icon_size=(130, 16), icon_anchor=(65, 26),
                                class_name="nom-prov", html=f"<div>{c['provincia']}</div>"),
        ).add_to(nombres)
    numeros.add_to(m)
    nombres.add_to(m)
    return nombres


def _svg_burbuja(cuenta: dict[str, int], total: int, r: float) -> str:
    """Circulo, partido en sectores cuando el distrito tiene mas de un tipo.

    El anillo blanco delimita la marca sobre cualquier fondo de la coropleta.
    """
    activos = [c for c in ORDEN_CATEGORIAS if cuenta.get(c, 0) > 0]
    cx = cy = r + 3
    piezas = [f'<circle cx="{cx}" cy="{cy}" r="{r+1.6}" fill="#fff" fill-opacity="0.95"/>']
    if len(activos) == 1:
        piezas.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{CATEGORIAS[activos[0]]}"/>')
    else:
        a0 = -math.pi / 2
        for c in activos:
            a1 = a0 + 2 * math.pi * (cuenta[c] / total)
            x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
            x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
            big = 1 if (a1 - a0) > math.pi else 0
            piezas.append(f'<path d="M{cx},{cy} L{x0:.2f},{y0:.2f} '
                          f'A{r},{r} 0 {big} 1 {x1:.2f},{y1:.2f} Z" '
                          f'fill="{CATEGORIAS[c]}"/>')
            a0 = a1
    piezas.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#0b0b0b" '
                  f'stroke-opacity="0.55" stroke-width="1.2"/>')
    return "".join(piezas)


def _popup(terr: dict, filas: list[dict], tx: Textos) -> str:
    """Contenido del popup: es lo que responde 'de que trata la denuncia'."""
    n = len(filas)
    cuenta: dict[str, int] = {}
    for f in filas:
        cuenta[f["tipo"]] = cuenta.get(f["tipo"], 0) + 1
    chips = " ".join(
        f'<span class="pop-tag" style="background:{CATEGORIAS[c]}">'
        f'{tx.tipo(c)} {v}</span>'
        for c, v in sorted(cuenta.items(), key=lambda x: ORDEN_CATEGORIAS.index(x[0])))

    loc = ""
    if terr.get("localidades"):
        loc = (f'<div class="pop-meta">Incluye el anexo '
               f'{", ".join(x.title() for x in terr["localidades"])}, '
               f'agregado a este distrito.</div>')

    detalle = ""
    for f in filas:
        # pandas devuelve NaN, no None: 'is not None' dejaria pasar el NaN.
        v = f.get("ciudadanos")
        ciu = (f' · {int(v)} ciudadanos listados'
               if v is not None and pd.notna(v) else "")
        detalle += (
            f'<div class="pop-sec">'
            f'<span class="pop-tag" style="background:{CATEGORIAS[f["tipo"]]}">'
            f'{tx.tipo(f["tipo"])}</span>'
            f'<div class="pop-meta">{f["fecha"]} · {f["documento"]} · '
            f'canal {tx.canal(f["canal"])}{ciu}</div>'
            f'<p class="pop-obs">{f["observacion"]}</p></div>')

    return (
        f'<h4>{terr["distrito"].title()}</h4>'
        f'<div class="pop-ub">{terr["provincia"].title()}, '
        f'{terr["departamento"].title()} · ubigeo INEI {terr["ubigeo_inei"]}</div>'
        f'{loc}'
        f'<div class="pop-sec"><b>{n} denuncia{"s" if n > 1 else ""}</b><br>{chips}</div>'
        f'{detalle}')


def _burbujas(m: folium.Map, territorios: list[dict],
              agrupado: dict[str, list[dict]], tx: Textos) -> None:
    grupo = folium.FeatureGroup(name="Distritos con denuncias", show=True)
    for t in territorios:
        filas = agrupado.get(t["ubigeo_inei"])
        if not filas:
            continue
        n = len(filas)
        cuenta: dict[str, int] = {}
        for f in filas:
            cuenta[f["tipo"]] = cuenta.get(f["tipo"], 0) + 1
        r = 7 + 4.5 * math.sqrt(n - 1)          # area proporcional, no el valor crudo
        lado = int((r + 3) * 2)
        folium.Marker(
            [t["lat"], t["lon"]],
            icon=folium.DivIcon(
                icon_size=(lado, lado), icon_anchor=(lado / 2, lado / 2),
                class_name="mk",
                html=f'<svg width="{lado}" height="{lado}" viewBox="0 0 {lado} {lado}">'
                     f'{_svg_burbuja(cuenta, n, r)}</svg>'),
            tooltip=folium.Tooltip(
                f'<b>{t["distrito"].title()}</b><br>{n} denuncia{"s" if n > 1 else ""}'
                f'<br><i>clic para ver el detalle</i>', class_name="tt"),
            popup=folium.Popup(_popup(t, filas, tx), max_width=380),
        ).add_to(grupo)
    grupo.add_to(m)


def _leyenda(m: folium.Map, html: str) -> None:
    m.get_root().html.add_child(folium.Element(f'<div class="leyenda">{html}</div>'))


def mapa_b(conteo_dep: dict[str, int], por_tipo: dict[str, int],
           tx: Textos | None = None) -> folium.Map:
    """Prototipo B: coropleta departamental."""
    tx = tx or cargar_textos()
    mp = tx["mapa"]
    m = _base()
    info = _departamentos(m, conteo_dep, tx)
    _contexto(m, tx)
    vmax = info["vmax"]
    pasos = ""
    for i, color in enumerate(RAMPA_AZUL):
        lo = int(vmax * i / len(RAMPA_AZUL)) + 1
        hi = int(vmax * (i + 1) / len(RAMPA_AZUL))
        if hi < lo:
            continue
        pasos += (f'<div class="f"><span class="sw" style="background:{color}"></span>'
                  f'<span>{lo if lo == hi else f"{lo} a {hi}"}</span></div>')
    _leyenda(m,
             f'<div class="t">{mp["leyenda_b_titulo"]}</div>' + pasos +
             f'<div class="f"><span class="sw" style="background:{SIN_CASOS}"></span>'
             f'<span>{mp["leyenda_b_sin_denuncias"]}</span></div>'
             f'<div class="nota">{mp["leyenda_b_nota"]}</div>')
    return m


def mapa_f(conteo_prov: dict[tuple[str, str], int], territorios: list[dict],
           agrupado: dict[str, list[dict]], por_tipo: dict[str, int],
           tx: Textos | None = None) -> folium.Map:
    """Prototipo F: provincias sombreadas, departamentos tenues y una burbuja por distrito.

    La leyenda es solo la del tipo de denuncia: el sombreado es una sola tinta, asi que
    no hay escala que explicar.
    """
    tx = tx or cargar_textos()
    mp = tx["mapa"]
    m = _base()
    _provincias(m, conteo_prov, tx)
    _limites_departamentos(m)
    distritos = _capa_distritos(m, tx, punteado=True)
    nombres = _rotulos_provincia(m, conteo_prov)
    _burbujas(m, territorios, agrupado, tx)
    m.add_child(LimitesPorZoom([(nombres, ZOOM_NOMBRES), (distritos, ZOOM_DISTRITO_F)]))
    tipos = "".join(
        f'<div class="f"><span class="pt" style="background:{CATEGORIAS[c]}"></span>'
        f'<span>{tx.tipo(c)}</span>'
        f'<span class="c">{por_tipo.get(c, 0)}</span></div>'
        for c in ORDEN_CATEGORIAS)
    _leyenda(m,
             f'<div class="t">{mp["leyenda_f_titulo"]}</div>' + tipos +
             f'<div class="nota">{mp["leyenda_f_nota"]}</div>')
    return m


# --- Mapas ya renderizados ----------------------------------------------------------
# Sin filtros generales, cada mapa es siempre el mismo. Se guarda su HTML, uno por modo;
# la huella del configuracion.toml va en la llave para que un cambio de texto lo renueve.
# Se guarda el HTML y NO el objeto folium: renderizar dos veces el mismo objeto da HTML
# distinto (la segunda vez agrega addTo(map) sueltos y el mapa llega sin marcadores).
@st.cache_resource(show_spinner=False)
def mapa_b_html(huella: str) -> str:
    df = datos.casos_df()
    return mapa_b(datos.por_departamento(df), df["tipo"].value_counts().to_dict(),
                  cargar_textos()).get_root().render()


@st.cache_resource(show_spinner=False)
def mapa_f_html(huella: str) -> str:
    df = datos.casos_df()
    return mapa_f(datos.por_provincia(df), datos.cargar()["territorios"],
                  datos.por_territorio(df), df["tipo"].value_counts().to_dict(),
                  cargar_textos()).get_root().render()
