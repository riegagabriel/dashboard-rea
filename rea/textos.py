"""Unico lector de configuracion.toml.

Todo texto visible que se edita a mano pasa por aqui. Si el archivo tiene un
error o le falta algo, la app NO se cae: usa el texto por defecto de este
modulo y devuelve avisos que la pagina muestra en pantalla.

Se lee en cada ejecucion (no se cachea), asi que un cambio en el .toml se ve
en la siguiente carga sin reiniciar la app.
"""
from __future__ import annotations

import difflib
import re
import tomllib
import unicodedata
from pathlib import Path

RUTA = Path(__file__).resolve().parent.parent / "configuracion.toml"

# Texto de respaldo: se usa cuando el .toml no trae la clave o esta danado.
# Debe coincidir con lo que dice configuracion.toml hoy.
POR_DEFECTO: dict = {
    "encabezado": {
        "titulo": "Denuncias registradas en el REA por casos de probable trashumancia electoral",
        "subtitulo": ("Subdirección de Procedimiento Electoral y Georreferenciación · "
                      "Dirección de Registro Electoral · RENIEC"),
    },
    "nota_normativa": {
        "texto": ("Los artículos **13.1** y **14.3** del mismo reglamento establecen que la "
                  "SDPEG debe considerar «las circunscripciones con reiteradas denuncias en el "
                  "REA» para determinar dónde aplicar la verificación domiciliaria. Este tablero "
                  "operativiza ese criterio."),
    },
    "cita_reglamento": {
        "nombre": "Registro de Alertas (REA)",
        "texto": ("Registro que contiene denuncias realizadas por ciudadanos, organizaciones "
                  "políticas, autoridades, de la administración pública y asociaciones civiles "
                  "referidas a cambios domiciliarios irregulares. En este registro se incluyen "
                  "reportes o informes remitidos por entidades de la administración pública "
                  "respecto a riesgos de índole electoral, social y económica que tengan un "
                  "efecto directo sobre la trashumancia electoral."),
        "fuente": ("RENIEC, *Verificación del Domicilio Declarado*, RE-002-DRE/001, "
                   "Segunda Versión, numeral 6.9, p. 6."),
    },
    "prototipos": {
        "b": "B · coropleta departamental",
        "f": "F · híbrido con detalle distrital",
    },
    "filtros": {
        "tipo": "Tipo de denuncia",
        "canal": "Canal de ingreso",
        "departamento": "Departamento",
        "fecha": "Fecha de ingreso",
        "sin_resultados": ("Ninguna denuncia cumple los filtros activos. "
                           "Amplíe la selección."),
    },
    "indicadores": {
        "denuncias": {"etiqueta": "Denuncias", "nota": "de {total} en el registro"},
        "documentos": {"etiqueta": "Documentos", "nota": "proveídos y alertas"},
        "distritos": {"etiqueta": "Distritos", "nota": "con al menos una denuncia"},
        "departamentos": {"etiqueta": "Departamentos", "nota": "de 25 a nivel nacional"},
        "ciudadanos": {"etiqueta": "Ciudadanos listados",
                       "nota": "consta en {cobertura} de {n} denuncias"},
    },
    "graficos": {
        "departamento": {
            "titulo": "Denuncias por departamento",
            "subtitulo": ("Barras apiladas por tipo: el color es el mismo que el de las "
                          "burbujas del mapa."),
        },
        "canal": {
            "titulo": "Canal de ingreso",
            "subtitulo": "Institución por la que llegó la denuncia.",
            "centro": "denuncias",
        },
        "tiempo": {
            "titulo": "Denuncias por fecha de ingreso a RENIEC",
            "subtitulo": ("Por semana (lunes a domingo). Las semanas sin denuncias se "
                          "dibujan en cero, no se omiten."),
            "eje_semana": "Semana",
            "eje_denuncias": "Denuncias",
            "pico": "{n} · semana del {fecha}",
        },
    },
    "tabla": {
        "titulo": "Detalle de denuncias",
        "nota": ("Una fila por denuncia, de la más reciente a la más antigua. Haz clic en "
                 "el encabezado de una columna para ordenarla."),
        "aviso_filtros": ("Estos filtros solo cambian la tabla; el mapa y los gráficos "
                          "no se modifican."),
        "conteo": "Se muestran {n} de {total} denuncias.",
        "sin_resultados": "Ninguna denuncia coincide con los filtros de la tabla.",
        "filtros": {
            "departamento": "Departamento",
            "provincia": "Provincia",
            "distrito": "Distrito",
            "todos": "Todos",
        },
    },
    "tipos": {
        "impugnacion": "Impugnación",
        "verificacion": "Verificación",
        "padron": "Padrón",
        "suspension_de_depuracion": "Suspensión de depuración",
    },
    "canales": {
        "reniec": "RENIEC",
        "ministerio_publico": "Ministerio Público",
        "defensoria_del_pueblo": "Defensoría del Pueblo",
    },
    "ajustes": {
        "altura_mapa": 940,
        "altura_tarjetas": 540,
    },
}

# Nombre por defecto de cada columna que la tabla puede mostrar. El id de la
# izquierda es el nombre interno y NO se renombra: conecta con los datos.
NOMBRES_COLUMNA: dict[str, str] = {
    "item": "Ítem",
    "fecha": "Fecha de ingreso",
    "departamento": "Departamento",
    "provincia": "Provincia",
    "distrito": "Distrito",
    "ubigeo_inei": "Ubigeo INEI",
    "tipo": "Tipo",
    "documento": "Documento",
    "formato": "Formato",
    "canal": "Canal",
    "denunciante": "Denunciante",
    "caracter": "Carácter",
    "ciudadanos": "Ciudadanos",
    "observacion": "Observación",
}
COLUMNAS_POR_DEFECTO = ("fecha", "departamento", "provincia", "distrito", "tipo",
                        "documento", "canal", "ciudadanos", "observacion")

ALTURA_MIN, ALTURA_MAX = 400, 2000


def clave(texto: str) -> str:
    """'Ministerio Publico' -> 'ministerio_publico'. Une los valores de los datos
    con las claves del .toml sin depender de tildes ni mayusculas."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", str(texto))
                         if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", sin_tildes.lower()).strip("_")


def _md(texto: str) -> str:
    """**negrita** -> <b>, *cursiva* -> <i>, para escribir el .toml con naturalidad."""
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", texto)


def rellenar(texto: str, **valores) -> str:
    """Sustituye {nombre} por su valor. Una marca desconocida se deja tal cual:
    nunca lanza error aunque el usuario la escriba mal o la borre."""
    return re.sub(r"\{(\w+)\}",
                  lambda m: str(valores.get(m.group(1), m.group(0))), texto)


def _combinar(defecto: dict, usuario: dict, ruta: str, avisos: list[str]) -> dict:
    for k in usuario:
        if k not in defecto:
            cercana = difflib.get_close_matches(k, list(defecto), n=1)
            ayuda = (f"¿quisiste decir «{cercana[0]}»?" if cercana
                     else f"claves válidas aquí: {', '.join(defecto)}")
            avisos.append(f"«{ruta}{k}» no existe; {ayuda}")
    salida: dict = {}
    for k, base in defecto.items():
        valor = usuario.get(k)
        if isinstance(base, dict):
            if k in usuario and not isinstance(valor, dict):
                avisos.append(f"«{ruta}{k}» debe ser una sección [{ruta}{k}], "
                              f"no un texto; se usan los textos por defecto.")
                valor = {}
            salida[k] = _combinar(base, valor or {}, f"{ruta}{k}.", avisos)
        elif k not in usuario:
            salida[k] = base
        elif isinstance(base, int):
            if (isinstance(valor, int) and not isinstance(valor, bool)
                    and ALTURA_MIN <= valor <= ALTURA_MAX):
                salida[k] = valor
            else:
                avisos.append(f"«{ruta}{k}» debe ser un número entre {ALTURA_MIN} y "
                              f"{ALTURA_MAX}; se usa {base}.")
                salida[k] = base
        elif isinstance(valor, str):
            salida[k] = valor
        else:
            avisos.append(f"«{ruta}{k}» debe ser un texto entre comillas; "
                          f"se usa el texto por defecto.")
            salida[k] = base
    return salida


def _columnas(usuario, avisos: list[str]) -> dict[str, str]:
    """Orden y nombres de las columnas de la tabla. Lo que el usuario escribe
    manda; un id inexistente se avisa y se ignora."""
    if usuario is None:
        return {c: NOMBRES_COLUMNA[c] for c in COLUMNAS_POR_DEFECTO}
    if not isinstance(usuario, dict) or not usuario:
        avisos.append("«tabla.columnas» está vacía o mal escrita; se usan las columnas "
                      "por defecto.")
        return {c: NOMBRES_COLUMNA[c] for c in COLUMNAS_POR_DEFECTO}
    salida: dict[str, str] = {}
    for c, nombre in usuario.items():
        if c not in NOMBRES_COLUMNA:
            cercana = difflib.get_close_matches(c, list(NOMBRES_COLUMNA), n=1)
            ayuda = (f"¿quisiste decir «{cercana[0]}»?" if cercana else "")
            avisos.append(f"«tabla.columnas.{c}» no es una columna válida. {ayuda} "
                          f"Ids válidos: {', '.join(NOMBRES_COLUMNA)}.".replace("  ", " "))
            continue
        if isinstance(nombre, str) and nombre.strip():
            salida[c] = nombre
        else:
            avisos.append(f"«tabla.columnas.{c}» debe ser un texto entre comillas; "
                          f"se usa «{NOMBRES_COLUMNA[c]}».")
            salida[c] = NOMBRES_COLUMNA[c]
    if not salida:
        avisos.append("Ninguna columna de «tabla.columnas» es válida; se usan las "
                      "columnas por defecto.")
        return {c: NOMBRES_COLUMNA[c] for c in COLUMNAS_POR_DEFECTO}
    return salida


def _canales(usuario, defecto: dict, avisos: list[str]) -> dict[str, str]:
    """Nombres mostrados de los canales. Mapa abierto: el usuario puede agregar
    un canal nuevo que aparezca en una base futura."""
    salida = dict(defecto)
    if usuario is None:
        return salida
    if not isinstance(usuario, dict):
        avisos.append("«canales» debe ser una sección [canales]; se usan los nombres "
                      "por defecto.")
        return salida
    for k, v in usuario.items():
        if isinstance(v, str) and v.strip():
            salida[clave(k)] = v
        else:
            avisos.append(f"«canales.{k}» debe ser un texto entre comillas; se ignora.")
    return salida


class Textos:
    def __init__(self, datos: dict, avisos: list[str], errores: list[str]):
        self._d = datos
        self.avisos = avisos
        self.errores = errores

    def __getitem__(self, seccion: str):
        return self._d[seccion]

    @property
    def titulo(self) -> str:
        return self._d["encabezado"]["titulo"]

    @property
    def subtitulo(self) -> str:
        return self._d["encabezado"]["subtitulo"]

    @property
    def tabla_titulo(self) -> str:
        return self._d["tabla"]["titulo"]

    @property
    def tabla_nota(self) -> str:
        return self._d["tabla"]["nota"]

    @property
    def altura_mapa(self) -> int:
        return self._d["ajustes"]["altura_mapa"]

    @property
    def altura_tarjetas(self) -> int:
        return self._d["ajustes"]["altura_tarjetas"]

    def nota_normativa(self) -> str:
        return _md(self._d["nota_normativa"]["texto"])

    def cita(self) -> str:
        c = self._d["cita_reglamento"]
        return f"<b>{c['nombre']}.</b> «{c['texto']}»<br>— {_md(c['fuente'])}"

    def prototipo(self, k: str) -> str:
        return self._d["prototipos"].get(k.lower(), "")

    def filtro(self, k: str) -> str:
        return self._d["filtros"][k]

    def indicador(self, k: str, **valores) -> tuple[str, str]:
        i = self._d["indicadores"][k]
        return i["etiqueta"], rellenar(i["nota"], **valores)

    def grafico(self, k: str) -> dict:
        return self._d["graficos"][k]

    def tabla_filtro(self, k: str) -> str:
        return self._d["tabla"]["filtros"][k]

    def columnas(self) -> dict[str, str]:
        return self._d["columnas"]

    def tipo(self, id_tipo: str) -> str:
        """Nombre mostrado de un tipo. Un tipo sin nombre configurado se muestra tal cual."""
        return self._d["tipos"].get(clave(id_tipo), id_tipo)

    def canal(self, valor: str) -> str:
        return self._d["canales"].get(clave(valor), valor)


def cargar() -> Textos:
    avisos: list[str] = []
    errores: list[str] = []
    usuario: dict = {}
    try:
        usuario = tomllib.loads(RUTA.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errores.append("No se encontró configuracion.toml; se muestran los textos por defecto.")
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        errores.append(f"configuracion.toml tiene un error y no se pudo leer ({e}). "
                       f"Se muestran los textos por defecto hasta que se corrija.")

    # Secciones de contenido abierto: se procesan aparte, no con claves fijas.
    usuario = dict(usuario)
    columnas_u = canales_u = None
    tabla_u = usuario.get("tabla")
    if isinstance(tabla_u, dict) and "columnas" in tabla_u:
        tabla_u = dict(tabla_u)
        columnas_u = tabla_u.pop("columnas")
        usuario["tabla"] = tabla_u
    if "canales" in usuario:
        canales_u = usuario.pop("canales")

    base = {k: v for k, v in POR_DEFECTO.items() if k != "canales"}
    datos = _combinar(base, usuario, "", avisos)
    datos["canales"] = _canales(canales_u, POR_DEFECTO["canales"], avisos)
    datos["columnas"] = _columnas(columnas_u, avisos)
    return Textos(datos, avisos, errores)
