"""Armazon comun de las dos apps: encabezado, filtros, KPIs, tablas y pie.

app_b.py y app_f.py solo cambian el mapa. Todo lo demas vive aqui para que los
dos prototipos no puedan divergir cuando llegue una actualizacion de la base.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from . import datos
from .estilo import (CITA_REA, CSS, ETIQUETA_CATEGORIA, ORDEN_CATEGORIAS,
                     SUBTITULO, TITULO, USO_NORMATIVO)


def configurar(prototipo: str) -> None:
    st.set_page_config(page_title=TITULO,
                       page_icon="🗺️", layout="wide",
                       initial_sidebar_state="expanded")
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(meta: dict, prototipo: str) -> None:
    izq, der = st.columns([7, 2])
    with izq:
        st.markdown(f'<p class="titulo-rea">{TITULO}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="sub-rea">{SUBTITULO}</p>', unsafe_allow_html=True)
    with der:
        st.markdown(
            f'<div style="text-align:right">'
            f'<span class="corte-rea">Fecha de corte: <b>{meta["fecha_corte"]}</b>'
            f'</span><br><span class="corte-rea" style="margin-top:6px">'
            f'Prototipo <b>{prototipo}</b></span></div>',
            unsafe_allow_html=True)
    st.markdown(f'<div class="aviso-norma">{USO_NORMATIVO}</div>',
                unsafe_allow_html=True)


def filtros(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    with st.sidebar:
        st.markdown("### Filtros")
        etiquetas = {ETIQUETA_CATEGORIA[c]: c for c in ORDEN_CATEGORIAS
                     if c in set(df["tipo"])}
        sel_t = st.multiselect("Tipo de denuncia", list(etiquetas),
                               default=list(etiquetas))
        tipos = [etiquetas[e] for e in sel_t] or list(etiquetas.values())

        canales_disp = sorted(df["canal"].unique())
        canales = st.multiselect("Canal de ingreso", canales_disp,
                                 default=canales_disp) or canales_disp

        deps = st.multiselect("Departamento", sorted(df["departamento"].unique()),
                              default=[])
        st.caption("Sin selección de departamento se muestra todo el país.")
        st.divider()
        st.caption("Los filtros afectan al mapa, a los indicadores y a todas las "
                   "tablas a la vez.")
    return tipos, canales, deps


def indicadores(f: pd.DataFrame, total: int) -> None:
    cols = st.columns(5)
    for col, (etq, valor, nota) in zip(cols, datos.kpis(f, total)):
        col.metric(etq, valor, help=nota)
        col.markdown(f'<div class="nota-tabla">{nota}</div>', unsafe_allow_html=True)


def _tabla(df: pd.DataFrame, altura: int | None = None) -> None:
    # No se usa use_container_width: esta deprecado y su ruta interna deja
    # height en None, que Streamlit >= 1.6x rechaza. `width` ya vale 'stretch'
    # por defecto, y `height` solo se pasa cuando hay un valor real.
    if altura:
        st.dataframe(df, hide_index=True, height=altura)
    else:
        st.dataframe(df, hide_index=True)


def tablas(f: pd.DataFrame) -> None:
    """Una sola tabla, ordenada por numero de denuncias.

    Sus primeras filas son el ranking de los lugares mas afectados, y las
    columnas traen la tipologia, el canal y los ciudadanos listados. Una tabla
    que se lee entera pesa mas que cinco que obligan a saltar entre cuadros.
    """
    st.markdown("### Detalle por distrito")
    lst = f["ciudadanos"].notna().sum()
    st.markdown(
        f'<div class="nota-tabla">Ordenado por número de denuncias: las primeras '
        f'filas son los lugares con mayor concentración. Incluye el desglose por '
        f'tipo, el canal de ingreso y los ciudadanos listados, que constan en '
        f'{lst} de {len(f)} denuncias.</div>', unsafe_allow_html=True)
    _tabla(datos.tabla_resumen(f), altura=460)


def reservado(f: pd.DataFrame) -> None:
    """Detalle nominal del denunciante. Fuera del cuerpo del tablero, a proposito.

    El repositorio es privado y lleva la base completa por decision del usuario.
    Eso hace imprescindible que la app tenga acceso restringido en Streamlit
    Cloud: un repositorio privado NO hace privada la URL de la app.
    """
    from pathlib import Path
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


def pie(meta: dict, f: pd.DataFrame, total: int) -> None:
    """Solo la cita del Reglamento, que es lo que pidio el correo.

    Se retiro la ficha tecnica (fuente, shapefile, fecha de generacion, nota de
    ubigeo, conteo de filtrados): esa informacion es para quien mantiene el
    tablero, no para quien lo consulta, y vive en el README.
    """
    st.markdown(f'<div class="aviso-norma">{CITA_REA}</div>', unsafe_allow_html=True)
