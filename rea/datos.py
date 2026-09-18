"""Carga de datos, KPIs, agregaciones y filtros de la tabla. Compartido por B y F.

Nada de aqui pone texto visible: los nombres de tipos, canales y columnas se
aplican al dibujar (rea/textos.py), porque casos_df() esta en cache y un cambio
en configuracion.toml no debe quedar congelado en ella.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from .estilo import ORDEN_CATEGORIAS

DATA = Path(__file__).resolve().parent.parent / "data"


@st.cache_data(show_spinner=False)
def cargar() -> dict:
    return json.loads((DATA / "rea.json").read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def geojson(nombre: str) -> dict:
    return json.loads((DATA / f"{nombre}.geojson").read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def casos_df() -> pd.DataFrame:
    df = pd.DataFrame(cargar()["casos"])
    for c in ("departamento", "provincia", "distrito"):
        df[c] = df[c].str.title()
    # Una fecha ilegible detiene la carga con mensaje: contarla mal en silencio
    # movería denuncias de semana sin que nadie lo note.
    fecha = pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce")
    if fecha.isna().any():
        malas = df.loc[fecha.isna(), ["item", "fecha"]].to_dict("records")
        raise ValueError(f"Fecha de ingreso ilegible en {len(malas)} denuncia(s): {malas[:5]}")
    df["fecha_dt"] = fecha
    df["semana"] = fecha.dt.to_period("W-SUN").dt.start_time   # el lunes de cada semana
    return df


# --- Indicadores ------------------------------------------------------------
def kpis(f: pd.DataFrame, total: int) -> list[tuple[str, str, dict]]:
    """(clave, valor, variables para la nota). El texto vive en configuracion.toml."""
    ciud = f["ciudadanos"].dropna()
    cob = len(ciud)
    return [
        ("denuncias", f"{len(f)}", {"total": total}),
        ("documentos", f"{f['documento'].nunique()}", {}),
        ("distritos", f"{f['ubigeo_inei'].nunique()}", {}),
        ("departamentos", f"{f['departamento'].nunique()}", {}),
        ("ciudadanos", f"{int(ciud.sum()):,}".replace(",", " "),
         {"cobertura": cob, "n": len(f)}),
    ]


# --- Agregaciones para los graficos ------------------------------------------
def por_departamento(f: pd.DataFrame) -> dict[str, int]:
    return f.groupby("departamento").size().to_dict()


def por_territorio(f: pd.DataFrame) -> dict[str, list[dict]]:
    salida: dict[str, list[dict]] = {}
    for u, g in f.groupby("ubigeo_inei"):
        salida[u] = g.to_dict("records")
    return salida


def por_departamento_tipo(f: pd.DataFrame) -> pd.DataFrame:
    """Denuncias por departamento y tipo, con el total; el mayor departamento primero."""
    g = f.groupby(["departamento", "tipo"]).size().reset_index(name="n")
    g = g.merge(g.groupby("departamento")["n"].sum().rename("total"),
                on="departamento")
    g["orden_tipo"] = g["tipo"].map({c: i for i, c in enumerate(ORDEN_CATEGORIAS)})
    return (g.sort_values(["total", "departamento", "orden_tipo"],
                          ascending=[False, True, True])
             .reset_index(drop=True))


def por_canal(f: pd.DataFrame) -> pd.DataFrame:
    g = (f.groupby("canal").size().reset_index(name="n")
          .sort_values(["n", "canal"], ascending=[False, True]))
    g["pct"] = 100 * g["n"] / g["n"].sum()
    return g.reset_index(drop=True)


def semanas_corte() -> pd.DatetimeIndex:
    """Todas las semanas del corte, de la primera a la ultima, incluidas las vacias."""
    df = casos_df()
    return pd.date_range(df["semana"].min(), df["semana"].max(), freq="7D")


def serie_semanal(f: pd.DataFrame) -> pd.DataFrame:
    """Denuncias por semana de ingreso; las semanas vacias valen 0, no se omiten."""
    cuenta = f.groupby("semana").size().reindex(semanas_corte(), fill_value=0)
    s = cuenta.rename_axis("semana").reset_index(name="n")
    s["fin"] = s["semana"] + pd.Timedelta(days=6)
    return s


# --- Tabla de detalle ---------------------------------------------------------
def tabla_denuncias(f: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """Una fila por denuncia, la mas reciente primero, con las columnas pedidas."""
    t = f.sort_values(["fecha_dt", "item"], ascending=[False, True]).copy()
    t["fecha"] = t["fecha_dt"]
    t["ciudadanos"] = t["ciudadanos"].astype("Int64")
    return t[columnas].reset_index(drop=True)


def opciones_territorio(f: pd.DataFrame, dep: str | None, prov: str | None
                        ) -> tuple[list[str], list[str], list[tuple[str, str, str]]]:
    """Opciones en cascada para las tres barras de filtro de la tabla.

    Devuelve (departamentos, provincias del departamento, distritos de la provincia)
    con cada distrito como (etiqueta, provincia, distrito). Hay nombres de distrito
    repetidos en provincias distintas (Cochas): en ese caso la etiqueta lleva la
    provincia, y el filtro real usa siempre el par (provincia, distrito).
    """
    deps = sorted(f["departamento"].unique())
    sub = f[f["departamento"] == dep] if dep else f
    provs = sorted(sub["provincia"].unique())
    sub = sub[sub["provincia"] == prov] if prov else sub
    pares = sorted(set(zip(sub["provincia"], sub["distrito"])), key=lambda p: (p[1], p[0]))
    nombres = [d for _, d in pares]
    dists = [((d if nombres.count(d) == 1 else f"{d} ({p})"), p, d) for p, d in pares]
    return deps, provs, dists


def filtrar_tabla(f: pd.DataFrame, dep: str | None, prov: str | None,
                  par: tuple[str, str] | None) -> pd.DataFrame:
    if dep:
        f = f[f["departamento"] == dep]
    if prov:
        f = f[f["provincia"] == prov]
    if par:
        f = f[(f["provincia"] == par[0]) & (f["distrito"] == par[1])]
    return f
