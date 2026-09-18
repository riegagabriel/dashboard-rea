"""Paleta y tokens visuales. Los textos viven en configuracion.toml (ver textos.py)."""
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

# --- Paleta del canal de ingreso (dona) --------------------------------------
# Validada con dataviz/scripts/validate_palette.js --pairs all (una dona es
# all-pairs: todas las porciones se tocan). De los 4 tonos que NO usan los tipos
# de denuncia (azul, verde, violeta, magenta) solo esta terna pasa: lo demas
# repite un tono de los tipos o falla la separacion (naranja/amarillo, naranja/rojo).
#   CVD peor par  dE 6.9  (banda 6-8: legal con etiquetas directas, que la dona lleva)
#   Vision normal dE 20.8 (piso >= 15)
#   Contraste aguamarina 2.74:1 y amarillo 2.11:1 -> WARN cubierto por la leyenda
#   con cantidades y porcentajes junto a la dona.
# Clave = nombre del canal normalizado (rea/textos.py::clave).
CANALES = {
    "reniec": "#1baf7a",                # aguamarina: el canal dominante
    "ministerio_publico": "#eda100",    # amarillo
    "defensoria_del_pueblo": "#e34948",  # rojo
}
# Canales que aparezcan en una base futura y no tengan color asignado:
CANAL_SIN_ASIGNAR = ["#898781", "#52514e", "#b9b5a8"]

# --- Rampa secuencial (magnitud departamental, prototipo B) ----------------
RAMPA_AZUL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

# --- Sombreado provincial (prototipo F) --------------------------------------
# Una sola tinta: en 27 de las 33 provincias con denuncias hay 1 o 2, asi que una
# escala de tonos casi no graduaria y obligaria a una leyenda. La magnitud la lleva
# el numero impreso y la burbuja. Contraste (WCAG) de los marcadores sobre la tinta:
#   azul 3.22 · verde 3.61 · violeta 6.24 · magenta 1.96 (el caso debil de siempre,
#   cubierto por el anillo blanco de la burbuja).
TINTA_PROVINCIA = "#e0dcd0"
LIMITE_DEPARTAMENTO = "#a9a69c"     # tenue: los departamentos quedan de fondo
SIN_CASOS = "#ffffff"

# --- Tinta y superficie ----------------------------------------------------
T = {
    "plano": "#f9f9f7", "superficie": "#fcfcfb", "tinta": "#0b0b0b",
    "tinta2": "#52514e", "tinta3": "#898781", "linea": "#e1e0d9",
    "borde": "rgba(11,11,11,0.10)", "acento": "#2a78d6",
}
FUENTE = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

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

/* Cinco cajas de cifras. HTML propio: st.metric recortaba las etiquetas
   ("Den...", "Ciud...") en columnas estrechas. */
.kpis {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px;
  margin-bottom:14px; }}
.kpi {{ background:{T['superficie']}; border:1px solid {T['borde']};
  border-radius:8px; padding:11px 13px; display:flex; flex-direction:column;
  min-width:0; }}
.kpi-e {{ font-size:0.78rem; line-height:1.25; color:{T['tinta2']}; }}
.kpi b {{ font-size:1.65rem; line-height:1.15; letter-spacing:-0.02em;
  color:{T['tinta']}; margin:3px 0; }}
.kpi em {{ font-style:normal; font-size:0.72rem; line-height:1.3;
  color:{T['tinta3']}; }}

.card-t {{ font-size:0.98rem; font-weight:700; color:{T['tinta']}; margin:0; }}
.card-s {{ font-size:0.78rem; color:{T['tinta3']}; margin:1px 0 6px;
  line-height:1.35; }}
.lg-canal {{ display:flex; align-items:center; gap:8px; font-size:0.84rem;
  color:{T['tinta']}; margin:5px 0; }}
.lg-canal i {{ width:12px; height:12px; border-radius:3px; flex:none; }}
.lg-canal b {{ margin-left:auto; padding-left:10px; color:{T['tinta2']};
  font-variant-numeric:tabular-nums; }}

[data-testid="stSelectbox"] label p {{ font-size:0.8rem; color:{T['tinta2']}; }}

/* Debajo de ~1000 px el mapa y la columna de graficos se apilan. Streamlit solo
   apila a 640 px, y entre 640 y 1000 quedarian demasiado estrechos. */
@media (max-width: 1000px) {{
  [data-testid="stHorizontalBlock"] {{ flex-wrap:wrap !important; }}
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
    flex:1 1 100% !important; min-width:100% !important; }}
  .kpis {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
}}

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

.nom-prov {{ background:none !important; border:none !important;
  pointer-events:none; }}
.nom-prov div {{ font-size:11px; font-weight:600; color:{T['tinta2']};
  text-align:center; white-space:nowrap;
  text-shadow:0 0 2px #fff,0 0 2px #fff,0 0 3px #fff,0 0 3px #fff; }}
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
