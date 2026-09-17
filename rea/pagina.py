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
    st.set_page_config(page_title="Denuncias REA · probable golondrinaje",
                       page_icon="🗺️", layout="wide",
                       initial_sidebar_state="expanded")
    st.markdown(CSS, unsafe_allow_html=True)


def encabezado(meta: dict, prototipo: str) -> None:
    izq, der = st.columns([5, 2])
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
    """Las cuatro tablas resumen que pide el correo, mas el ranking departamental.

    Ninguna cifra del tablero exige leer el mapa: esa era la queja de fondo
    detras de 'la imagen se ve muy pequena'.
    """
    st.markdown("### Ranking · los 5 lugares con más denuncias")
    st.markdown('<div class="nota-tabla">Distrito con mayor concentración de '
                'denuncias y su desglose por tipo.</div>', unsafe_allow_html=True)
    _tabla(datos.tabla_ranking(f, 5))

    a, b = st.columns(2)
    with a:
        st.markdown("### Tipología de las denuncias")
        st.markdown('<div class="nota-tabla">Las cuatro causales registradas en el '
                    'REA.</div>', unsafe_allow_html=True)
        _tabla(datos.tabla_tipologia(f))
    with b:
        st.markdown("### Canal de ingreso")
        st.markdown('<div class="nota-tabla">Entidad por la que ingresó la denuncia, '
                    'según la columna INSTITUCION de la fuente.</div>',
                    unsafe_allow_html=True)
        _tabla(datos.tabla_canal(f))

    c, d = st.columns([1, 1])
    with c:
        st.markdown("### Ranking departamental")
        st.markdown('<div class="nota-tabla">El top 5 distrital esconde el patrón '
                    'regional; este cuadro lo muestra completo.</div>',
                    unsafe_allow_html=True)
        _tabla(datos.tabla_departamentos(f), altura=320)
    with d:
        st.markdown("### Listados de ciudadanos adjuntados")
        lst = datos.tabla_listados(f)
        cob = len(lst)
        st.markdown(f'<div class="nota-tabla">Denuncias que adjuntaron una relación '
                    f'nominal. Consta en {cob} de {len(f)} denuncias '
                    f'({100*cob/max(len(f),1):.0f} %): el resto no declara cantidad.'
                    f'</div>', unsafe_allow_html=True)
        _tabla(lst, altura=320)


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
    st.markdown(f'<div class="aviso-norma">{CITA_REA}</div>', unsafe_allow_html=True)
    sin = total - len(f) if len(f) < total else 0
    st.markdown(
        f'<div class="pie-rea">'
        f'Fuente: <code>{meta["fuente"]}</code> · {meta["geodata"]} · '
        f'generado el {meta["generado"]}.<br>'
        f'{meta["nota_ubigeo"]}<br>'
        f'Mostrando <b>{len(f)}</b> de <b>{total}</b> denuncias del registro'
        f'{f" ({sin} ocultas por los filtros activos)" if sin else ""}. '
        f'Uso interno RENIEC.'
        f'</div>', unsafe_allow_html=True)
