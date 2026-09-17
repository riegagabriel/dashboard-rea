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

# --- Textos normativos -----------------------------------------------------
TITULO = "Denuncias registradas en el REA por casos de probable golondrinaje"
SUBTITULO = ("Subdirección de Procedimiento Electoral y Georreferenciación · "
             "Dirección de Registro Electoral · RENIEC")

CITA_REA = (
    "<b>Registro de Alertas (REA).</b> «Registro que contiene denuncias realizadas por "
    "ciudadanos, organizaciones políticas, autoridades, de la administración pública y "
    "asociaciones civiles referidas a cambios domiciliarios irregulares. En este registro "
    "se incluyen reportes o informes remitidos por entidades de la administración pública "
    "respecto a riesgos de índole electoral, social y económica que tengan un efecto "
    "directo sobre la trashumancia electoral.»  \n"
    "<br>— RENIEC, <i>Verificación del Domicilio Declarado</i>, RE-002-DRE/001, "
    "Segunda Versión, numeral 6.9, p. 6."
)
USO_NORMATIVO = (
    "Los artículos <b>13.1</b> y <b>14.3</b> del mismo reglamento establecen que la SDPEG debe "
    "considerar «las circunscripciones con reiteradas denuncias en el REA» para determinar "
    "dónde aplicar la verificación domiciliaria. Este tablero operativiza ese criterio."
)

# --- CSS -------------------------------------------------------------------
# La leyenda va a 15 px por pedido expreso: era el punto mas criticado de la
# version anterior.
CSS = f"""
<style>
.stApp {{ background:{T['plano']}; }}
html, body, [class*="css"] {{ font-family:{FUENTE}; }}
#MainMenu, footer {{ visibility:hidden; }}
.block-container {{ padding-top:2.1rem; padding-bottom:2.5rem; max-width:1500px; }}

.titulo-rea {{ font-size:1.62rem; font-weight:700; letter-spacing:-0.015em;
  color:{T['tinta']}; line-height:1.25; margin:0 0 3px; }}
.sub-rea {{ font-size:0.9rem; color:{T['tinta2']}; margin:0 0 4px; }}
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
