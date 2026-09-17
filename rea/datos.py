"""Carga de datos, KPIs y las cuatro tablas resumen. Compartido por B y F."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from .estilo import ETIQUETA_CATEGORIA, ORDEN_CATEGORIAS

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
    df["tipo_etq"] = df["tipo"].map(ETIQUETA_CATEGORIA)
    for c in ("departamento", "provincia", "distrito"):
        df[c] = df[c].str.title()
    return df


def filtrar(df: pd.DataFrame, tipos: list[str], canales: list[str],
            deps: list[str]) -> pd.DataFrame:
    f = df[df["tipo"].isin(tipos) & df["canal"].isin(canales)]
    if deps:
        f = f[f["departamento"].isin(deps)]
    return f


# --- KPIs -------------------------------------------------------------------
def kpis(f: pd.DataFrame, total: int) -> list[tuple[str, str, str]]:
    ciud = f["ciudadanos"].dropna()
    cob = len(ciud)
    return [
        ("Denuncias", f"{len(f)}", f"de {total} en el registro"),
        ("Documentos", f"{f['documento'].nunique()}", "proveídos y alertas"),
        ("Distritos", f"{f['ubigeo_inei'].nunique()}", "con al menos una denuncia"),
        ("Departamentos", f"{f['departamento'].nunique()}", "de 25 a nivel nacional"),
        ("Ciudadanos listados", f"{int(ciud.sum()):,}".replace(",", " "),
         f"consta en {cob} de {len(f)} denuncias"),
    ]


# --- Tablas resumen ---------------------------------------------------------
def tabla_ranking(f: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Los n lugares con mas denuncias, con su desglose por tipo."""
    g = (f.groupby(["distrito", "provincia", "departamento", "ubigeo_inei"])
           .size().reset_index(name="Denuncias"))
    piv = (f.pivot_table(index="ubigeo_inei", columns="tipo_etq",
                         aggfunc="size", fill_value=0))
    g = g.merge(piv, on="ubigeo_inei", how="left").fillna(0)
    g = g.sort_values("Denuncias", ascending=False).head(n)
    cols = ["distrito", "provincia", "departamento", "ubigeo_inei", "Denuncias"]
    extra = [ETIQUETA_CATEGORIA[c] for c in ORDEN_CATEGORIAS
             if ETIQUETA_CATEGORIA[c] in g.columns]
    g = g[cols + extra].rename(columns={
        "distrito": "Distrito", "provincia": "Provincia",
        "departamento": "Departamento", "ubigeo_inei": "Ubigeo INEI"})
    for c in extra:
        g[c] = g[c].astype(int)
    return g.reset_index(drop=True)


def tabla_departamentos(f: pd.DataFrame) -> pd.DataFrame:
    """Ranking departamental completo: el top 5 distrital esconde el patron regional."""
    g = f.groupby("departamento").agg(
        Denuncias=("item", "size"),
        Distritos=("ubigeo_inei", "nunique"),
        Ciudadanos=("ciudadanos", lambda s: int(s.dropna().sum())),
    ).reset_index().rename(columns={"departamento": "Departamento"})
    g["% del total"] = (100 * g["Denuncias"] / max(len(f), 1)).round(1)
    return g.sort_values("Denuncias", ascending=False).reset_index(drop=True)


def tabla_tipologia(f: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for c in ORDEN_CATEGORIAS:
        sub = f[f["tipo"] == c]
        filas.append({
            "Tipo de denuncia": ETIQUETA_CATEGORIA[c],
            "Denuncias": len(sub),
            "% del total": round(100 * len(sub) / max(len(f), 1), 1),
            "Distritos alcanzados": sub["ubigeo_inei"].nunique(),
            "Departamentos": sub["departamento"].nunique(),
        })
    return pd.DataFrame(filas)


def tabla_canal(f: pd.DataFrame) -> pd.DataFrame:
    g = f.groupby("canal").agg(
        Denuncias=("item", "size"),
        Distritos=("ubigeo_inei", "nunique"),
    ).reset_index().rename(columns={"canal": "Canal de ingreso"})
    g["% del total"] = (100 * g["Denuncias"] / max(len(f), 1)).round(1)
    return g.sort_values("Denuncias", ascending=False).reset_index(drop=True)


def tabla_listados(f: pd.DataFrame) -> pd.DataFrame:
    """Denuncias que adjuntaron un listado nominal de ciudadanos."""
    con = f[f["ciudadanos"].notna()].copy()
    if con.empty:
        return pd.DataFrame(columns=["Distrito", "Provincia", "Departamento",
                                     "Ciudadanos listados", "Tipo", "Documento"])
    con = con.sort_values("ciudadanos", ascending=False)
    g = con[["distrito", "provincia", "departamento", "ciudadanos",
             "tipo_etq", "documento"]].rename(columns={
        "distrito": "Distrito", "provincia": "Provincia",
        "departamento": "Departamento", "ciudadanos": "Ciudadanos listados",
        "tipo_etq": "Tipo", "documento": "Documento"})
    g["Ciudadanos listados"] = g["Ciudadanos listados"].astype(int)
    return g.reset_index(drop=True)


def por_departamento(f: pd.DataFrame) -> dict[str, int]:
    return f.groupby("departamento").size().to_dict()


def por_territorio(f: pd.DataFrame) -> dict[str, list[dict]]:
    salida: dict[str, list[dict]] = {}
    for u, g in f.groupby("ubigeo_inei"):
        salida[u] = g.to_dict("records")
    return salida
