"""Paleta, tokens visuales y textos normativos. Fuente unica para ambas apps."""
from __future__ import annotations

# --- Paleta categorica -----------------------------------------------------
# Validada con dataviz/scripts/validate_palette.js en modo --pairs all, el que
# corresponde a un mapa (cualquier par de marcas puede quedar contiguo):
#   CVD peor par      dE 13.0   (objetivo >= 8)
#   Vision normal     dE 16.3   (piso     >= 15)
#   Contraste magenta 2.62:1 -> WARN relevado por las tablas resumen.
# De los 70 subconjuntos posibles de 4 colores, solo 26 pasan. El orden por
# defecto de la paleta FALLA (amarillo/naranja, dE 13.7 < 15).
#
# El color sigue a la categoria POR SU NOMBRE. Nunca por frecuencia: si se
# asignara por ranking, una actualizacion repintaria las categorias y romperia
# la comparabilidad entre versiones del tablero.
CATEGORIAS = {
    "IMPUGNACION": "#2a78d6",               # azul
    "VERIFICACION": "#008300",              # verde
    "PADRON": "#4a3aa7",                    # violeta
    "SUSPENSION DE DEPURACION": "#e87ba4",  # magenta (el de menor contraste,
}                                           # asignado a la categoria mas rara)
ORDEN_CATEGORIAS = list(CATEGORIAS)

ETIQUETA_CATEGORIA = {
    "IMPUGNACION": "Impugnación",
    "VERIFICACION": "Verificación",
    "PADRON": "Padrón",
    "SUSPENSION DE DEPURACION": "Suspensión de depuración",
}

# --- Rampa secuencial (magnitud departamental, prototipo B) ----------------
RAMPA_AZUL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

# --- Rampa neutra acotada (prototipo F) ------------------------------------
# El tope es #dcd8cd porque mas oscuro borra los marcadores justo donde hay mas
# datos. Medido:  #dcd8cd -> azul/verde/violeta >=3:1 ;  #7a756a -> los cuatro < 2:1.
CLASES_GRIS = [
    (1, 1, "#f4f2ec", "1 caso"),
    (2, 3, "#eae7dd", "2 a 3"),
    (4, 11, "#e0dcd0", "4 a 11"),
    (12, 10_000, "#dcd8cd", "12 o más"),
]
SIN_CASOS = "#ffffff"

# --- Tinta y superficie ----------------------------------------------------
T = {
    "plano": "#f9f9f7", "superficie": "#fcfcfb", "tinta": "#0b0b0b",
    "tinta2": "#52514e", "tinta3": "#898781", "linea": "#e1e0d9",
    "borde": "rgba(11,11,11,0.10)", "acento": "#2a78d6",
}
FUENTE = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

# --- Textos editables -----------------------------------------------------
# Los textos NO se escriben aqui: se leen de configuracion.toml, en la raiz del
# repositorio. Asi quien solo quiere cambiar una frase no tiene que abrir un
# archivo lleno de CSS y codigos de color.
import re as _re
import tomllib as _tomllib
from pathlib import Path as _Path

_CONFIG = _tomllib.loads(
    (_Path(__file__).resolve().parent.parent / "configuracion.toml")
    .read_text(encoding="utf-8"))


def _md(texto: str) -> str:
    """**negrita** -> <b>, *cursiva* -> <i>. Para que el TOML se escriba natural."""
    texto = _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    return _re.sub(r"\*(.+?)\*", r"<i>\1</i>", texto)


TITULO = _CONFIG["encabezado"]["titulo"]
SUBTITULO = _CONFIG["encabezado"]["subtitulo"]
USO_NORMATIVO = _md(_CONFIG["nota_normativa"]["texto"])

_c = _CONFIG["cita_reglamento"]
CITA_REA = (f"<b>{_c['nombre']}.</b> «{_c['texto']}»<br>— {_md(_c['fuente'])}")

PROTOTIPO_B = _CONFIG["prototipos"]["b"]
PROTOTIPO_F = _CONFIG["prototipos"]["f"]
TABLA_TITULO = _CONFIG["tabla"]["titulo"]
TABLA_NOTA = _CONFIG["tabla"]["nota"]

# --- CSS -------------------------------------------------------------------
# La leyenda va a 15 px por pedido expreso: era el punto mas criticado de la
# version anterior.
CSS = f"""
<style>
.stApp {{ background:{T['plano']}; }}
html, body, [class*="css"] {{ font-family:{FUENTE}; }}
#MainMenu, footer {{ visibility:hidden; }}

/* El encabezado de Streamlit mide 60 px y es opaco: con 2.1rem de padding
   tapaba los 10 px superiores del titulo. */
[data-testid="stHeader"] {{ background:transparent; }}
[data-testid="stMainBlockContainer"], .block-container {{
  padding-top:4.6rem !important; padding-bottom:2.5rem; max-width:1500px; }}

/* Streamlit fija el tamano de los <p> de su markdown con un selector mas
   especifico que una sola clase: sin .stApp y sin !important el titulo se
   quedaba en 16 px en vez de los 26 pedidos. */
.stApp .titulo-rea {{ font-size:1.75rem !important; line-height:1.3 !important;
  font-weight:700; letter-spacing:-0.015em; color:{T['tinta']};
  margin:0 0 6px !important; }}
.stApp .sub-rea {{ font-size:0.92rem !important; line-height:1.45 !important;
  color:{T['tinta2']}; margin:0 0 4px !important; }}
.corte-rea {{ display:inline-block; font-size:0.84rem; color:{T['tinta2']};
  background:{T['superficie']}; border:1px solid {T['borde']}; border-radius:6px;
  padding:5px 12px; }}
.corte-rea b {{ color:{T['tinta']}; }}
.aviso-norma {{ font-size:0.86rem; color:{T['tinta2']}; background:{T['superficie']};
  border:1px solid {T['borde']}; border-left:3px solid {T['acento']};
  border-radius:6px; padding:10px 14px; margin:14px 0 4px; }}

div[data-testid="stMetric"] {{ background:{T['superficie']};
  border:1px solid {T['borde']}; border-radius:8px; padding:12px 15px; }}
div[data-testid="stMetricValue"] {{ font-size:1.72rem; font-weight:700;
  letter-spacing:-0.02em; color:{T['tinta']}; }}
div[data-testid="stMetricLabel"] p {{ font-size:0.8rem; color:{T['tinta2']}; }}

h3 {{ font-size:1.02rem !important; font-weight:700 !important; color:{T['tinta']};
  margin-top:1.4rem !important; }}
.nota-tabla {{ font-size:0.78rem; color:{T['tinta3']}; margin:-6px 0 8px; }}
.pie-rea {{ font-size:0.8rem; color:{T['tinta2']}; border-top:1px solid {T['linea']};
  padding-top:14px; margin-top:24px; line-height:1.55; }}
.pie-rea code {{ background:#efeee9; padding:1px 5px; border-radius:3px;
  font-size:0.76rem; }}
</style>
"""

# CSS que viaja DENTRO del iframe del mapa (Streamlit lo aisla del resto).
CSS_MAPA = f"""
<style>
.leaflet-container {{ font-family:{FUENTE}; background:#ffffff; }}
.mk {{ background:none !important; border:none !important; }}

/* Leyenda: 15 px por pedido expreso. */
.leyenda {{ position:absolute; left:12px; bottom:14px; z-index:650;
  background:{T['superficie']}; border:1px solid {T['borde']}; border-radius:8px;
  padding:12px 15px; font-size:15px; color:{T['tinta']}; line-height:1.5;
  box-shadow:0 1px 4px rgba(11,11,11,0.10); max-width:280px; }}
.leyenda .t {{ font-size:12px; text-transform:uppercase; letter-spacing:0.06em;
  color:{T['tinta3']}; font-weight:700; margin-bottom:7px; }}
.leyenda .f {{ display:flex; align-items:center; gap:9px; margin:5px 0; }}
.leyenda .pt {{ width:14px; height:14px; border-radius:50%; flex:none;
  border:1px solid rgba(11,11,11,0.35); }}
.leyenda .sw {{ width:20px; height:13px; border:1px solid {T['linea']}; flex:none;
  border-radius:2px; }}
.leyenda .c {{ margin-left:auto; color:{T['tinta2']}; font-variant-numeric:tabular-nums;
  font-weight:600; }}
.leyenda .sep {{ height:1px; background:{T['linea']}; margin:10px 0 9px; }}
.leyenda .nota {{ margin-top:9px; padding-top:8px; border-top:1px solid {T['linea']};
  color:{T['tinta3']}; font-size:12.5px; line-height:1.4; }}

.num-dep {{ background:none !important; border:none !important; font-weight:700;
  font-size:13px; color:{T['tinta']}; text-align:center; pointer-events:none;
  text-shadow:0 0 3px #fff,0 0 3px #fff,0 0 3px #fff,0 0 3px #fff; }}

.leaflet-tooltip.tt {{ font-size:13px; padding:6px 9px;
  border:1px solid {T['borde']}; box-shadow:0 1px 3px rgba(11,11,11,0.10); }}
.leaflet-popup-content {{ font-size:13px; margin:12px 14px; line-height:1.5;
  max-height:340px; overflow-y:auto; }}
.leaflet-popup-content h4 {{ margin:0 0 2px; font-size:15px; }}
.pop-ub {{ color:{T['tinta3']}; font-size:12px; font-variant-numeric:tabular-nums; }}
.pop-sec {{ margin-top:10px; padding-top:8px; border-top:1px solid {T['linea']}; }}
.pop-tag {{ display:inline-block; padding:1px 7px; border-radius:99px;
  font-size:11.5px; font-weight:600; color:#fff; }}
.pop-obs {{ font-size:12.5px; color:{T['tinta2']}; margin:5px 0 0;
  border-left:2px solid {T['linea']}; padding-left:9px; }}
.pop-meta {{ font-size:11.5px; color:{T['tinta3']}; margin-top:2px; }}
</style>
"""
