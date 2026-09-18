"""Los tres graficos del panel derecho. Altair viene incluido con Streamlit.

Los colores de los tipos salen de estilo.CATEGORIAS (no se redefinen aqui) y los
del canal de estilo.CANALES; ambas paletas estan validadas con la herramienta del
skill dataviz. Los nombres visibles llegan por Textos (configuracion.toml).
"""
from __future__ import annotations

import math

import altair as alt
import pandas as pd

from .estilo import (CANAL_SIN_ASIGNAR, CANALES, CATEGORIAS, FUENTE,
                     ORDEN_CATEGORIAS, T)
from .textos import Textos, clave

MESES = '["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]'


def _tema(c: alt.TopLevelMixin) -> alt.TopLevelMixin:
    return (c.configure(background="rgba(0,0,0,0)", font=FUENTE)
             .configure_view(strokeWidth=0)
             .configure_axis(labelColor=T["tinta2"], titleColor=T["tinta2"],
                             labelFontSize=12, domainColor=T["linea"],
                             tickColor=T["linea"], gridColor=T["linea"])
             .configure_legend(labelColor=T["tinta2"], labelFontSize=12,
                               symbolSize=110, padding=0))


def color_canal(valor: str, sin_asignar: list[str]) -> str:
    """Color fijo por canal. Uno desconocido toma un gris de la lista de reserva."""
    k = clave(valor)
    if k in CANALES:
        return CANALES[k]
    return CANAL_SIN_ASIGNAR[len(sin_asignar) % len(CANAL_SIN_ASIGNAR)]


def colores_canal(canales: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    extra: list[str] = []
    for c in canales:
        out[c] = color_canal(c, extra)
        if clave(c) not in CANALES:
            extra.append(c)
    return out


def barras_departamento(d: pd.DataFrame, t: Textos) -> alt.Chart:
    """Barras horizontales apiladas por tipo. `d` viene de datos.por_departamento_tipo."""
    presentes = [c for c in ORDEN_CATEGORIAS if c in set(d["tipo"])]
    d = d.assign(tipo_etq=d["tipo"].map(t.tipo))
    orden = list(dict.fromkeys(d["departamento"]))            # ya viene por total desc.
    maximo = int(d["total"].max())
    escala_x = alt.Scale(domain=[0, maximo * 1.14])
    y = alt.Y("departamento:N", sort=orden, title=None,
              axis=alt.Axis(ticks=False, domain=False, labelLimit=150, labelPadding=6))
    barras = (alt.Chart(d)
              .mark_bar(stroke=T["superficie"], strokeWidth=1.5, cornerRadiusEnd=0)
              .encode(
                  y=y,
                  x=alt.X("n:Q", stack="zero", axis=None, scale=escala_x),
                  color=alt.Color(
                      "tipo_etq:N", title=None,
                      scale=alt.Scale(domain=[t.tipo(c) for c in presentes],
                                      range=[CATEGORIAS[c] for c in presentes]),
                      legend=alt.Legend(orient="bottom", columns=2, symbolType="square")),
                  order=alt.Order("orden_tipo:Q"),
                  tooltip=[alt.Tooltip("departamento:N", title=t.etiqueta_columna("departamento")),
                           alt.Tooltip("tipo_etq:N", title=t.etiqueta_columna("tipo")),
                           alt.Tooltip("n:Q", title=t.indicador("denuncias")[0])]))
    totales = (alt.Chart(d.drop_duplicates("departamento"))
               .mark_text(align="left", dx=5, fontSize=12, fontWeight=700, color=T["tinta"])
               .encode(y=y, x=alt.X("total:Q", axis=None, scale=escala_x), text="total:Q"))
    return _tema((barras + totales).properties(height=alt.Step(24), width="container"))


def dona_canal(c: pd.DataFrame, t: Textos) -> alt.Chart:
    """Dona del canal de ingreso. `c` viene de datos.por_canal."""
    colores = colores_canal(list(c["canal"]))
    d = c.assign(canal_etq=c["canal"].map(t.canal))
    arco = (alt.Chart(d)
            .mark_arc(innerRadius=62, outerRadius=92, stroke=T["superficie"], strokeWidth=2)
            .encode(theta=alt.Theta("n:Q", stack=True),
                    color=alt.Color("canal_etq:N", legend=None,
                                    scale=alt.Scale(domain=list(d["canal_etq"]),
                                                    range=[colores[k] for k in d["canal"]]),
                                    sort=list(d["canal_etq"])),
                    order=alt.Order("n:Q", sort="descending"),
                    tooltip=[alt.Tooltip("canal_etq:N", title=t.etiqueta_columna("canal")),
                             alt.Tooltip("n:Q", title=t.indicador("denuncias")[0]),
                             alt.Tooltip("pct:Q", title="%", format=".0f")]))
    total = alt.Chart(pd.DataFrame({"t": [str(int(d["n"].sum()))]})).mark_text(
        size=30, fontWeight=700, color=T["tinta"], dy=-6).encode(text="t:N")
    rotulo = alt.Chart(pd.DataFrame({"t": [t.grafico("canal")["centro"]]})).mark_text(
        size=12, color=T["tinta3"], dy=16).encode(text="t:N")
    return _tema((arco + total + rotulo).properties(height=210, width="container"))


def linea_tiempo(s: pd.DataFrame, t: Textos) -> alt.Chart:
    """Denuncias por semana. `s` viene de datos.serie_semanal (semanas vacias en 0)."""
    g = t.grafico("tiempo")
    d = s.assign(etq=s["semana"].dt.strftime("%d/%m") + " – " + s["fin"].dt.strftime("%d/%m"))
    tope = max(5, int(math.ceil(d["n"].max() / 5.0) * 5))
    x = alt.X("semana:T", title=None,
              axis=alt.Axis(tickCount="month", grid=False, labelPadding=6,
                            labelExpr=f"{MESES}[month(datum.value)]"))
    y = alt.Y("n:Q", title=None, scale=alt.Scale(domain=[0, tope], nice=False),
              axis=alt.Axis(tickMinStep=1, tickCount=4, domain=False))
    base = alt.Chart(d).encode(x=x, y=y)
    area = base.mark_area(color=T["tinta"], opacity=0.07)
    linea = base.mark_line(color=T["tinta"], strokeWidth=2)
    puntos = base.mark_point(filled=True, color=T["tinta"], size=44, opacity=1,
                             stroke=T["superficie"], strokeWidth=1.5).encode(
        tooltip=[alt.Tooltip("etq:N", title=g["eje_semana"]),
                 alt.Tooltip("n:Q", title=g["eje_denuncias"])])
    pico = d.loc[d["n"] == d["n"].max()].head(1).assign(
        txt=lambda q: [g["pico"].replace("{n}", str(int(r.n))).replace(
            "{fecha}", r.semana.strftime("%d/%m")) for r in q.itertuples()])
    rotulo = (alt.Chart(pico)
              .mark_text(align="left", dx=9, dy=-2, fontSize=12, fontWeight=600, color=T["tinta"])
              .encode(x="semana:T", y="n:Q", text="txt:N"))
    return _tema((area + linea + puntos + rotulo).properties(height=190, width="container"))
