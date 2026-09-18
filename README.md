# Denuncias registradas en el REA por casos de probable trashumancia electoral

Tablero interno de la Subdirección de Procedimiento Electoral y Georreferenciación
(SDPEG) · Dirección de Registro Electoral · RENIEC.

Sirve para saber **en qué zonas se concentran las denuncias de probable trashumancia electoral**
registradas en el Registro de Alertas.

**Corte vigente:** 14 de setiembre de 2026 · 67 denuncias · 52 distritos ·
15 departamentos · 100 % georreferenciado.

---

## ✏️ Cómo cambiar los textos del tablero

**Todos los textos se editan en un solo archivo: [`configuracion.toml`](configuracion.toml).**
No hace falta tocar ningún archivo `.py`.

| Qué quieres cambiar | Dónde, dentro de `configuracion.toml` |
|---|---|
| Título principal (y el de la pestaña del navegador) | `[encabezado]` → `titulo` |
| Línea bajo el título | `[encabezado]` → `subtitulo` |
| Recuadro azul que explica para qué sirve | `[nota_normativa]` → `texto` |
| Cita del reglamento al pie | `[cita_reglamento]` |
| Etiqueta «Prototipo B / F» arriba a la derecha | `[prototipos]` — déjala vacía `""` para ocultarla |
| Título y explicación de la tabla | `[tabla]` |

**Desde GitHub, sin instalar nada:**

1. Abre `configuracion.toml` en el repositorio y pulsa el lápiz ✏️ (*Edit this file*).
2. Cambia el texto entre comillas.
3. Pulsa **Commit changes**.
4. Streamlit Cloud redespliega **las dos apps** solas en uno o dos minutos.

Para **negrita** escribe `**así**`; para cursiva, `*así*`.

Si al recargar sigues viendo el texto viejo: en Streamlit Cloud, menú de la app →
**Reboot app**.

> `app_b.py` y `app_f.py` **no contienen textos**: solo deciden qué mapa dibujar.
> Por eso no encontrarás el título dentro de ellos.

**Lo que no está en ese archivo, a propósito:** los colores del mapa. Están
validados para que las cuatro categorías se distingan también con daltonismo
(ver *Decisiones de diseño*), y cambiarlos a ojo rompería esa garantía.

---

## Sobre los datos publicados

Este repositorio es **público** y **no contiene datos personales**.

El tablero es anónimo por construcción: el denunciante persona natural aparece
siempre como «Denuncia individual» y solo se nombran las instituciones (ONPE,
Ministerio Público, Defensoría del Pueblo). El campo `OBSERVACIONES` se publica
íntegro porque se verificó, sobre las 67 filas, que no contiene ningún DNI ni
apellido de la base.

El archivo con el detalle nominal (`rea_nominal.csv`) **se queda en el proyecto
local** y está bloqueado en `.gitignore`. Si se copia a mano a `data/`, la sección
«Detalle nominal — RESERVADO» aparece solo en esa ejecución local; en el despliegue
público no existe.

> Antes de añadir cualquier archivo a `data/`, comprobar que no lleva DNI, nombres
> ni direcciones. Lo que entra a un repositorio público queda en su historial de Git
> aunque después se borre.

## Las dos apps

| Entrada | Prototipo | Qué muestra |
|---|---|---|
| `app_b.py` | **B** · coropleta departamental | Magnitud por departamento en rampa azul, con el número impreso sobre cada uno. Lectura inmediata a escala nacional. |
| `app_f.py` | **F** · híbrido | Coropleta departamental en gris + una burbuja por distrito, coloreada por tipo de denuncia. Cada burbuja abre un popup con la observación completa de cada denuncia. |

Ambas comparten el mismo motor (`rea/`), así que no pueden divergir cuando llegue
una actualización de la base.

### Lo que traen las dos

- Filtros de tipo de denuncia, canal de ingreso y departamento, que afectan **a la vez**
  al mapa, a los indicadores y a todas las tablas.
- Cinco indicadores: denuncias, documentos, distritos, departamentos y ciudadanos listados.
- **Una tabla de detalle por distrito**, ordenada por número de denuncias: sus primeras
  filas son el ranking de los lugares más afectados, y sus columnas traen el desglose
  por tipo, el canal de ingreso y los ciudadanos listados.
- Límites **provinciales y distritales que aparecen al acercar** el zoom.
- Nota al pie con la cita literal del Reglamento.

---

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app_f.py      # o app_b.py
```

## Desplegar en Streamlit Community Cloud

Un solo repositorio, dos apps. En **New app**, elegir este repo y cambiar el
*Main file path*:

| App | Main file path |
|---|---|
| Prototipo B | `app_b.py` |
| Prototipo F | `app_f.py` |

Las apps públicas no tienen límite de número en el plan gratuito, así que las dos
conviven sin problema.

---

## Actualizar cuando llegue una base nueva

El ETL **no vive aquí**: está en el proyecto local `DENUNCIAS_REA/scripts/`. Este
repositorio recibe solo el resultado ya validado.

```bash
# en el proyecto local
python scripts/02_procesamiento_rea.py     # procesa y valida el Excel nuevo
python scripts/03_preparar_web.py          # regenera data/ de este repo
# luego: commit y push
```

El paso 2 imprime un reporte de validación que compara contra el corte anterior
(altas, bajas y variación por categoría). Si aparecen territorios sin ubicar, se
añade una línea a `data/interim/equivalencias_territoriales.csv` del proyecto local
y se vuelve a correr. No hay que tocar código.

---

## Decisiones de diseño que conviene no deshacer

**La paleta está validada por cómputo, no elegida por gusto.** Un mapa es una forma
*all-pairs*: cualquier par de marcas puede quedar contiguo. De los 70 subconjuntos
posibles de 4 colores, solo 26 pasan la prueba de separación para daltonismo en ese
modo, y la combinación por defecto **falla**. La elegida da ΔE 13,0 en visión con
deficiencia cromática y 16,3 en visión normal.

**Los colores están congelados por nombre de categoría** en `rea/estilo.py`. Si se
asignaran por frecuencia, una actualización repintaría las categorías y rompería la
comparabilidad entre versiones del tablero.

**El fondo del prototipo F es gris, no azul.** Una rampa azul bajo marcadores azules
pondría magnitud e identidad en la misma familia de color. Y la rampa se corta en
`#dcd8cd` porque más oscuro borra los marcadores justo donde hay más datos: medido,
sobre `#7a756a` los cuatro colores caen por debajo de 2:1 de contraste.

**La tabla no es un extra.** La queja de fondo —«la imagen se ve muy pequeña»— no se
arregla agrandando el mapa, sino haciendo que ninguna cifra dependa de leerlo. Y es
una sola: una tabla que se lee entera pesa más que cinco que obligan a saltar entre
cuadros.

**El mapa no usa teselas.** La coropleta es la superficie; un fondo cartográfico
competiría con ella y añadiría una dependencia de red innecesaria.

---

## Advertencia sobre el UBIGEO

El código territorial que usa el tablero es **UBIGEO INEI**, el que corresponde a la
geometría. **No es el ubigeo RENIEC**: difieren en el **94,1 %** de los distritos, y
los prefijos de departamento divergen desde Callao (INEI 07 = Callao, RENIEC 24 =
Callao). Nunca intercambiarlos.

## Problemas conocidos

| Problema | Estado |
|---|---|
| La fuente escribe `MINISTRIO PUBLICO`, sin la «E» | Se muestra corregido; la fuente no se modifica. Reportado a Cristian. |
| El correo anunciaba el canal «OTROS»; la fuente trae **Defensoría del Pueblo** | No se inventa la categoría anunciada. |
| `El Algarrobal` y `San Juan de Iris` aparecen dos veces, una bien escrita y otra mal | Las equivalencias los hacen converger. Reportado. |
| **Santa Rosa** (Loreto), distrito creado en 2024, no existe en el shapefile INEI | Anclado a su distrito matriz **Yavarí**; ubicación aproximada, declarada en el popup. |
| `CANT_CIUDADANOS` consta solo en 21 de 67 denuncias (31 %) | La cobertura se declara en pantalla junto a la cifra. |
| Desde este corte ya no existe la hoja `DATOS` del Excel | Se perdió el banco de pruebas externo; la validación pasó a comparación entre cortes. |

## Fuentes

| Fuente | Aporta |
|---|---|
| `CONSOLIDADO REA_POST CIERRE PADRON_CRC.xlsx`, hoja `RESUMEN` | Las 67 denuncias. |
| Shapefile distrital INEI (1 891 distritos, EPSG:4326) | Geometría y UBIGEO. |
| `RE-002-DRE/001`, *Verificación del Domicilio Declarado*, 2.ª versión | Definición del REA (numeral 6.9) y los criterios de los arts. 13.1 y 14.3. |
