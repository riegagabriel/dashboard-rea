"""Armazon comun de las dos apps: encabezado, mapa 50/50, graficos y tabla.

app_b.py y app_f.py solo cambian el mapa (la funcion que le pasan a tablero()).
Todo lo demas vive aqui para que los dos prototipos no puedan divergir cuando
llegue una actualizacion de la base. Los textos se leen de configuracion.toml.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd
import streamlit as st

from . import datos, graficos, textos
from .estilo import CATEGORIAS, CSS, T


ALTO_SELECTOR = 52   # px que ocupa el selector de mapa: el mapa se reduce en esa cantidad


# --- Cabecera ---------------------------------------------------------------
def configurar(prototipo: str) -> None:
    t = textos.cargar()
    st.set_page_config(page_title=t.titulo, page_icon="🗺️", layout="wide",
                       initial_sidebar_state="collapsed")
    st.markdown(CSS, unsafe_allow_html=True)
    for e in t.errores:
        st.error(e)
    if t.avisos:
        st.warning("**Revisar configuracion.toml:**\n\n" + "\n".join(f"- {a}" for a in t.avisos))


def encabezado(meta: dict, prototipo: str) -> None:
    t = textos.cargar()
    etiqueta = t.prototipo(prototipo)
    izq, der = st.columns([7, 2])
    with izq:
        st.markdown(f'<p class="titulo-rea">{t.titulo}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-rea">{t.subtitulo}</p>', unsafe_allow_html=True)
    with der:
        st.markdown(
            f'<div style="text-align:right;padding-bottom:16px">'
            f'<span class="corte-rea">Fecha de corte: <b>{meta["fecha_corte"]}</b>'
            f'</span>'
            + (f'<br><span class="corte-rea" style="margin-top:6px">'
               f'Prototipo <b>{etiqueta}</b></span>' if etiqueta else '')
            + '</div>',
            unsafe_allow_html=True)


# --- Selector de mapa ----------------------------------------------------------
def selector_mapa(t: textos.Textos) -> str:
    """'b' (coropleta departamental) o 'f' (provincias y distritos)."""
    mp = t["mapa"]
    etiquetas = {"b": mp["selector_b"], "f": mp["selector_f"]}
    elegido = st.segmented_control(
        mp["selector_titulo"], list(etiquetas), default=mp["inicial"],
        format_func=etiquetas.get, selection_mode="single", key="modo_mapa",
        label_visibility="collapsed")
    if elegido is None:      # el control devuelve None si se deselecciona: se conserva el modo
        elegido = st.session_state.get("modo_mapa_previo", mp["inicial"])
    st.session_state["modo_mapa_previo"] = elegido
    return elegido


# --- Panel derecho ----------------------------------------------------------
def indicadores(f: pd.DataFrame, total: int) -> None:
    t = textos.cargar()
    cajas = ""
    for k, valor, vars_ in datos.kpis(f, total):
        etq, nota = t.indicador(k, **vars_)
        cajas += (f'<div class="kpi"><span class="kpi-e">{etq}</span>'
                  f'<b>{valor}</b><em>{nota}</em></div>')
    st.markdown(f'<div class="kpis">{cajas}</div>', unsafe_allow_html=True)


def _cabecera(g: dict) -> None:
    st.markdown(f'<div class="card-t">{g["titulo"]}</div>'
                f'<div class="card-s">{g["subtitulo"]}</div>', unsafe_allow_html=True)


def _leyenda_canal(c: pd.DataFrame, t: textos.Textos) -> str:
    colores = graficos.colores_canal(list(c["canal"]))
    return "".join(
        f'<div class="lg-canal"><i style="background:{colores[r.canal]}"></i>'
        f'{t.canal(r.canal)}<b>{r.n} · {r.pct:.0f} %</b></div>'
        for r in c.itertuples())


def panel_derecho(f: pd.DataFrame, total: int) -> None:
    t = textos.cargar()
    indicadores(f, total)
    izq, der = st.columns([3, 2])
    with izq, st.container(border=True, height=t.altura_tarjetas):
        _cabecera(t.grafico("departamento"))
        st.altair_chart(graficos.barras_departamento(datos.por_departamento_tipo(f), t),
                        width="stretch", theme=None)
    with der, st.container(border=True, height=t.altura_tarjetas):
        _cabecera(t.grafico("canal"))
        canal = datos.por_canal(f)
        st.altair_chart(graficos.dona_canal(canal, t), width="stretch", theme=None)
        st.markdown(_leyenda_canal(canal, t), unsafe_allow_html=True)
    with st.container(border=True):
        _cabecera(t.grafico("tiempo"))
        st.altair_chart(graficos.linea_tiempo(datos.serie_semanal(f), t),
                        width="stretch", theme=None)


# --- Tabla ----------------------------------------------------------------
def _selectbox(etiqueta: str, opciones: list[str], key: str) -> str:
    # Si el filtro de arriba cambio y esta seleccion ya no existe, vuelve a "Todos".
    if st.session_state.get(key) not in opciones:
        st.session_state.pop(key, None)
    return st.selectbox(etiqueta, opciones, key=key)


def _texto_sobre(fondo: str) -> str:
    """Blanco salvo que el fondo sea claro (el magenta, 2.6:1 con blanco): texto
    en negrita sobre color, donde bastan 4:1."""
    def lum(c: int) -> float:
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (int(fondo[i:i + 2], 16) for i in (1, 3, 5))
    L = 0.2126 * lum(r) + 0.7152 * lum(g) + 0.0722 * lum(b)
    return "#ffffff" if 1.05 / (L + 0.05) >= 4.0 else T["tinta"]


def _config_columnas(columnas: dict[str, str]) -> dict:
    cfg = {}
    for i, nombre in columnas.items():
        if i == "fecha":
            cfg[i] = st.column_config.DateColumn(nombre, format="DD/MM/YYYY")
        elif i in ("ciudadanos", "item"):
            cfg[i] = st.column_config.NumberColumn(nombre, format="%d")
        elif i == "observacion":
            cfg[i] = st.column_config.TextColumn(nombre, width="large")
        elif i == "documento":
            cfg[i] = st.column_config.TextColumn(nombre, width="medium")
        else:
            cfg[i] = st.column_config.TextColumn(nombre)
    return cfg


def tabla(f: pd.DataFrame) -> None:
    t = textos.cargar()
    tf = t["tabla"]["filtros"]
    todos = tf["todos"]
    st.markdown(f"### {t.tabla_titulo}")
    st.markdown(f'<div class="nota-tabla">{t.tabla_nota}</div>', unsafe_allow_html=True)

    # Tres filtros en cascada, solo para esta tabla.
    deps, _, _ = datos.opciones_territorio(f, None, None)
    c1, c2, c3 = st.columns(3)
    with c1:
        dep = _selectbox(tf["departamento"], [todos] + deps, "tf_dep")
    dep_v = None if dep == todos else dep
    _, provs, _ = datos.opciones_territorio(f, dep_v, None)
    with c2:
        prov = _selectbox(tf["provincia"], [todos] + provs, "tf_prov")
    prov_v = None if prov == todos else prov
    _, _, dists = datos.opciones_territorio(f, dep_v, prov_v)
    pares = {e: (p, d) for e, p, d in dists}
    with c3:
        dist = _selectbox(tf["distrito"], [todos] + list(pares), "tf_dist")
    st.markdown(f'<div class="nota-tabla">{t["tabla"]["aviso_filtros"]}</div>',
                unsafe_allow_html=True)

    g = datos.filtrar_tabla(f, dep_v, prov_v, None if dist == todos else pares[dist])
    if g.empty:
        st.info(t["tabla"]["sin_resultados"])
        return
    columnas = t.columnas()
    tab = datos.tabla_denuncias(g, list(columnas))
    if "tipo" in tab:
        tab["tipo"] = tab["tipo"].map(t.tipo)
    if "canal" in tab:
        tab["canal"] = tab["canal"].map(t.canal)

    estilo = tab.style
    if "tipo" in tab:
        color = {t.tipo(c): hexa for c, hexa in CATEGORIAS.items()}
        estilo = estilo.map(
            lambda v: (f"background-color:{color[v]};color:{_texto_sobre(color[v])};"
                       f"font-weight:600") if v in color else "", subset=["tipo"])
    st.dataframe(estilo, hide_index=True, height=520,
                 column_config=_config_columnas(columnas), column_order=list(columnas))
    st.markdown(
        f'<div class="nota-tabla">'
        f'{textos.rellenar(t["tabla"]["conteo"], n=len(tab), total=len(f))}</div>',
        unsafe_allow_html=True)


def reservado(f: pd.DataFrame) -> None:
    """Detalle nominal del denunciante. Fuera del cuerpo del tablero, a proposito.

    Solo aparece si el archivo local existe: el repositorio es publico y ese
    archivo NUNCA se sube (esta bloqueado en .gitignore).
    """
    ruta = Path(__file__).resolve().parent.parent / "data" / "rea_nominal.csv"
    if not ruta.exists():
        return
    with st.expander("🔒 Detalle nominal del denunciante — RESERVADO", expanded=False):
        st.caption("Contiene datos personales (Ley 29733). No difundir ni exportar "
                   "fuera de RENIEC. El resto del tablero es anónimo.")
        nom = pd.read_csv(ruta, sep=";", dtype=str, encoding="utf-8-sig")
        cols = [c for c in ["ITEM", "DNI", "APELLIDO PATERNO", "APELLIDO MATERNO",
                            "PRENOMBRES", "CANAL", "CASOS", "DEPARTAMENTO_INEI",
                            "PROVINCIA_INEI", "DISTRITO_INEI", "UBIGEO_INEI"]
                if c in nom.columns]
        visibles = set(f["item"].astype(str))
        nom = nom[nom["ITEM"].astype(str).isin(visibles)]
        st.dataframe(nom[cols], hide_index=True, height=320)
        st.caption(f"{len(nom)} registros, según los filtros activos.")


def pie() -> None:
    """Solo la cita del Reglamento, que es lo que pidio el correo."""
    st.markdown(f'<div class="aviso-norma">{textos.cargar().cita()}</div>',
                unsafe_allow_html=True)


# --- Pagina completa ----------------------------------------------------------
def tablero(df: pd.DataFrame, dibujar_mapa: Callable[[pd.DataFrame, int], None]) -> None:
    """Mapa al 50 % a la izquierda; cifras y graficos a la derecha; tabla debajo a todo
    el ancho. `dibujar_mapa(df, altura)` es lo unico que cambia entre el prototipo B y
    el F. No hay filtros globales: la unica busqueda es la de la tabla."""
    t = textos.cargar()
    izq, der = st.columns(2, gap="medium")
    with izq:
        dibujar_mapa(df, t.altura_mapa)
    with der:
        panel_derecho(df, len(df))
    tabla(df)
    reservado(df)
    pie()
