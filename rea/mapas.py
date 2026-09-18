"""Construccion de los dos mapas Folium: prototipo B y prototipo F."""
from __future__ import annotations

import math

import folium
import pandas as pd
from branca.element import MacroElement, Template

from .datos import geojson
from .estilo import (CATEGORIAS, CLASES_GRIS, CSS_MAPA, ORDEN_CATEGORIAS,
                     RAMPA_AZUL, SIN_CASOS, T)
from .textos import Textos, cargar as cargar_textos

PERU = [[-18.6, -81.5], [0.2, -68.4]]
ZOOM_PROVINCIA = 7   # a partir de aqui aparecen los limites provinciales
ZOOM_DISTRITO = 9    # a partir de aqui, los distritales


class LimitesPorZoom(MacroElement):
    """Muestra provincias y distritos solo al acercar.

    Se usa MacroElement y no un <script> suelto porque folium renderiza los
    macros DESPUES del mapa y de las capas: es el unico punto donde las
    variables JS de ambos ya existen.
    """

    _template = Template("""
        {% macro script(this, kwargs) %}
        (function(){
          var mapa = {{ this._parent.get_name() }};
          var prov = {{ this.prov.get_name() }};
          var dist = {{ this.dist.get_name() }};
          mapa.removeLayer(prov); mapa.removeLayer(dist);
          function ajustar(){
            var z = mapa.getZoom();
            if (z >= {{ this.z_prov }}) { if (!mapa.hasLayer(prov)) mapa.addLayer(prov); }
            else { if (mapa.hasLayer(prov)) mapa.removeLayer(prov); }
            if (z >= {{ this.z_dist }}) { if (!mapa.hasLayer(dist)) mapa.addLayer(dist); }
            else { if (mapa.hasLayer(dist)) mapa.removeLayer(dist); }
          }
          mapa.on('zoomend', ajustar);
          ajustar();
        })();
        {% endmacro %}
    """)

    def __init__(self, prov, dist, z_prov=ZOOM_PROVINCIA, z_dist=ZOOM_DISTRITO):
        super().__init__()
        self._name = "LimitesPorZoom"
        self.prov, self.dist = prov, dist
        self.z_prov, self.z_dist = z_prov, z_dist


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


def _contexto(m: folium.Map) -> None:
    prov = folium.GeoJson(
        geojson("provincias"), name="Provincias",
        style_function=lambda _: {"fillOpacity": 0, "color": "#a8a59c",
                                  "weight": 0.6},
        tooltip=folium.GeoJsonTooltip(fields=["PROVINCIA", "DEPARTAMEN"],
                                      aliases=["Provincia", "Departamento"],
                                      class_name="tt"))
    prov.add_to(m)
    dist = folium.GeoJson(
        geojson("distritos_contexto"), name="Distritos",
        style_function=lambda _: {"fillOpacity": 0, "color": "#bdbab1",
                                  "weight": 0.45},
        tooltip=folium.GeoJsonTooltip(fields=["DISTRITO", "PROVINCIA", "DEPARTAMEN"],
                                      aliases=["Distrito", "Provincia", "Departamento"],
                                      class_name="tt"))
    dist.add_to(m)
    m.add_child(LimitesPorZoom(prov, dist))


def _color_azul(n: int, vmax: int) -> str:
    if n <= 0:
        return SIN_CASOS
    i = min(int(math.ceil(n / max(vmax, 1) * len(RAMPA_AZUL))) - 1, len(RAMPA_AZUL) - 1)
    return RAMPA_AZUL[max(i, 0)]


def _color_gris(n: int) -> str:
    if n <= 0:
        return SIN_CASOS
    for lo, hi, color, _ in CLASES_GRIS:
        if lo <= n <= hi:
            return color
    return CLASES_GRIS[-1][2]


def _departamentos(m: folium.Map, conteo: dict[str, int], modo: str) -> dict:
    """Capa departamental. modo 'azul' (prototipo B) o 'gris' (prototipo F)."""
    gj = geojson("departamentos")
    vmax = max(conteo.values()) if conteo else 1
    por_clase: dict[str, int] = {e: 0 for *_, e in CLASES_GRIS}
    for f in gj["features"]:
        n = int(conteo.get(f["properties"]["DEPARTAMEN"].title(), 0))
        f["properties"]["n"] = n
        f["properties"]["color"] = (_color_azul(n, vmax) if modo == "azul"
                                    else _color_gris(n))
        if n > 0 and modo == "gris":
            for lo, hi, _, etq in CLASES_GRIS:
                if lo <= n <= hi:
                    por_clase[etq] += 1
                    break

    capa = folium.FeatureGroup(name="Departamentos", show=True)
    folium.GeoJson(
        gj,
        style_function=lambda f: {"fillColor": f["properties"]["color"],
                                  "fillOpacity": 1.0, "color": T["linea"],
                                  "weight": 0.9},
        highlight_function=lambda _: {"color": T["tinta2"], "weight": 2.2},
        tooltip=folium.GeoJsonTooltip(fields=["DEPARTAMEN", "n"],
                                      aliases=["Departamento", "Denuncias"],
                                      class_name="tt"),
    ).add_to(capa)

    # El numero impreso: la magnitud no queda solo en el color.
    for f in gj["features"]:
        if f["properties"]["n"] <= 0:
            continue
        from shapely.geometry import shape
        p = shape(f["geometry"]).representative_point()
        folium.Marker(
            [p.y, p.x],
            icon=folium.DivIcon(icon_size=(38, 18), icon_anchor=(19, 9),
                                class_name="num-dep",
                                html=f"<div>{f['properties']['n']}</div>"),
        ).add_to(capa)
    capa.add_to(m)
    return {"vmax": vmax, "por_clase": por_clase}


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


def mapa_b(conteo_dep: dict[str, int], por_tipo: dict[str, int]) -> folium.Map:
    """Prototipo B: coropleta departamental."""
    m = _base()
    info = _departamentos(m, conteo_dep, "azul")
    _contexto(m)
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
             '<div class="t">Denuncias por departamento</div>' + pasos +
             f'<div class="f"><span class="sw" style="background:{SIN_CASOS}"></span>'
             f'<span>sin denuncias</span></div>'
             '<div class="nota">El número impreso es el total del departamento. '
             'Al acercar aparecen los límites provinciales y distritales.</div>')
    return m


def mapa_f(conteo_dep: dict[str, int], territorios: list[dict],
           agrupado: dict[str, list[dict]], por_tipo: dict[str, int]) -> folium.Map:
    """Prototipo F: coropleta departamental en gris + burbujas distritales."""
    tx = cargar_textos()
    m = _base()
    info = _departamentos(m, conteo_dep, "gris")
    _contexto(m)
    _burbujas(m, territorios, agrupado, tx)
    grises = "".join(
        f'<div class="f"><span class="sw" style="background:{color}"></span>'
        f'<span>{etq}</span><span class="c">{info["por_clase"].get(etq, 0)}</span></div>'
        for _, _, color, etq in CLASES_GRIS)
    tipos = "".join(
        f'<div class="f"><span class="pt" style="background:{CATEGORIAS[c]}"></span>'
        f'<span>{tx.tipo(c)}</span>'
        f'<span class="c">{por_tipo.get(c, 0)}</span></div>'
        for c in ORDEN_CATEGORIAS)
    _leyenda(m,
             '<div class="t">Departamento · denuncias</div>' + grises +
             '<div class="sep"></div>'
             '<div class="t">Distrito · tipo de denuncia</div>' + tipos +
             '<div class="nota">El tamaño del círculo indica el número de denuncias '
             'del distrito; partido, que hay más de un tipo. Clic para ver de qué '
             'trata cada denuncia.</div>')
    return m
