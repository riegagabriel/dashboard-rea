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
No hace falta tocar ningún archivo `.py`. `app_b.py` y `app_f.py` no contienen textos:
solo eligen el mapa.

| Qué quieres cambiar | Sección de `configuracion.toml` |
|---|---|
| Título (y el de la pestaña del navegador) y subtítulo | `[encabezado]` |
| Cita del reglamento al pie | `[cita_reglamento]` |
| Etiqueta «Prototipo B / F» (hoy la cabecera ya no la muestra) | `[prototipos]` |
| Las cuatro cajas de cifras | `[indicadores.denuncias]`, `[indicadores.distritos]`… |
| El desglose de ciudadanos por tipo (texto «sin dato» y recuadro de cobertura) | `[indicadores.ciudadanos]` → `sin_dato`, `cobertura_tipo` |
| Títulos y subtítulos de los tres gráficos | `[graficos.departamento]`, `[graficos.canal]`, `[graficos.tiempo]` |
| Título, nota y filtros de la tabla | `[tabla]`, `[tabla.filtros]` |
| **Nombre, orden y visibilidad de las columnas de la tabla** | `[tabla.columnas]` |
| Nombre de cada tipo de denuncia / de cada canal | `[tipos]`, `[canales]` |
| Recuadro «¿Qué es cada tipo de denuncia?» bajo el mapa (textos, título, línea de procedencia; `mostrar = false` lo oculta) | `[leyenda_tipos]` |
| Selector de mapa, leyendas y recuadros del mapa | `[mapa]` |
| Alto de la columna del mapa (incluye el recuadro de tipos) y de las tarjetas de gráficos | `[ajustes]` |

**Desde GitHub, sin instalar nada:**

1. Abre `configuracion.toml` en el repositorio y pulsa el lápiz ✏️ (*Edit this file*).
2. Cambia el texto entre comillas.
3. Pulsa **Commit changes**.
4. Las **dos apps** toman el cambio en la siguiente carga de la página (no hace falta reiniciarlas).

Para **negrita** escribe `**así**`; para cursiva, `*así*`.

### Columnas de la tabla

Cada línea de `[tabla.columnas]` es `id_interno = "Nombre que se muestra"`:

```toml
[tabla.columnas]
fecha        = "Fecha de ingreso"
departamento = "Departamento"
distrito     = "Distrito"
observacion  = "Observación"
```

- **Renombrar:** cambia lo que está entre comillas.
- **Reordenar:** cambia las líneas de lugar.
- **Ocultar:** borra la línea (o antepón `#`).
- **Mostrar más:** añade una línea con un id válido. Ids disponibles: `item`, `fecha`,
  `departamento`, `provincia`, `distrito`, `ubigeo_inei`, `tipo`, `documento`, `formato`,
  `canal`, `denunciante`, `caracter`, `ciudadanos`, `observacion`.
- El **id de la izquierda no se renombra**: es el que conecta con los datos.

### Si te equivocas

La app **no se cae**. Muestra un recuadro amarillo arriba con lo que hay que corregir
(por ejemplo, «`tabla.columnas.distritos` no es una columna válida, ¿quisiste decir
`distrito`?») y mientras tanto usa el texto original. Un error de sintaxis, como una
comilla sin cerrar, se muestra como un aviso rojo con el número de línea. Las marcas
como `{total}` que se escriban mal se muestran tal cual, sin romper nada.

### Lo que NO está en ese archivo, a propósito

| Qué | Dónde | Por qué |
|---|---|---|
| Colores de los 4 tipos de denuncia | `rea/estilo.py` → `CATEGORIAS` | Validados por cómputo para daltonismo; cambiarlos a ojo rompe la garantía |
| Colores de los canales | `rea/estilo.py` → `CANALES` | Ídem, validados en modo «todos los pares» |
| Tinta de las provincias del mapa F | `rea/estilo.py` → `TINTA_PROVINCIA` | Medida contra los marcadores: azul, verde y violeta quedan sobre 3:1 |
| Orden y tamaño de los bloques de la página | `rea/pagina.py` | Es estructura, no texto |

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

| Entrada | Prototipo | Qué muestra el mapa |
|---|---|---|
| `app_b.py` | **B** · coropleta departamental | Magnitud por departamento en rampa azul, con el número impreso sobre cada uno. Lectura inmediata a escala nacional. |
| `app_f.py` | **F** · mapa intercambiable | Un **selector sobre el mapa** alterna entre dos vistas: la coropleta **B** (la misma de la app B) y el mapa **F**: provincias sombreadas, límites departamentales tenues y una burbuja por distrito, coloreada por tipo de denuncia. Cada burbuja abre un popup con la observación completa de cada denuncia. |

**El mapa F, en detalle.**

- Las provincias con denuncias llevan **una sola tinta**; las demás, blanco. El **número** de denuncias se imprime sobre las provincias con 2 o más, y al pasar el ratón sobre cualquiera se lee «Provincia · Denuncias».
- **Al acercar:** desde el zoom 7 aparecen los nombres de las provincias con denuncias, y desde el 7,5 los límites de distrito (2 clics desde el inicio).
- **La leyenda es solo la del tipo de denuncia.** Una sola tinta no lleva escala, así que no hay leyenda de sombreado.
- **Por qué provincia y no departamento:** sombrear por departamento tiñe el 72 % del país y esconde que Yauyos concentra 10 de las 67 denuncias; por provincia se tiñe el 16 %.
- **Sesgo conocido:** una provincia grande con una sola denuncia (Loreto, 68 700 km²) es la mayor mancha del mapa, y Mariscal Luzuriaga (5 denuncias, 667 km²) casi no se ve a escala nacional. Para eso están el número y la burbuja.

Ambas comparten **toda la página** (`rea/pagina.py`) y solo difieren en el mapa, así que
no pueden divergir cuando llegue una actualización de la base.

### La página

```
┌────────────────────────────────────────────────────────────┐
│ Título · fecha de corte                                    │
├─────────────────────────┬──────────────────────────────────┤
│ MAPA (50 % de la        │ 5 cajas de cifras                │
│ pantalla)               ├─────────────────────┬────────────┤
│                         │ Barras por depto.   │ Dona canal │
│                         ├─────────────────────┴────────────┤
│                         │ Línea de tiempo por semana       │
├─────────────────────────┴──────────────────────────────────┤
│ Tabla de denuncias (una fila por denuncia)                 │
│ con filtros propios: Departamento · Provincia · Distrito   │
└────────────────────────────────────────────────────────────┘
```

- **No hay filtros generales**: el mapa, las cifras y los gráficos muestran siempre todas las
  denuncias del corte.
- Los **tres filtros de la tabla** (departamento, provincia, distrito) afectan solo a la tabla,
  y van en cascada. `Cochas` existe en dos provincias, así que el distrito se identifica
  siempre por el par provincia-distrito.
- La línea de tiempo usa la columna «INGRESO A RENIEC», por semana (lunes a domingo). Las
  semanas sin denuncias valen cero, no se omiten.
- Límites **provinciales y distritales que aparecen al acercar** el zoom del mapa.
- Por debajo de ~1000 px de ancho, el mapa y los gráficos se apilan.
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

**El recuadro de tipos resta alto al mapa.** Va debajo del mapa y mide unos 200 px; `rea/pagina.py` (`ALTO_LEYENDA`) se lo resta al mapa para que su columna termine a la altura de la de gráficos. Con textos mucho más largos o más cortos, la nota cambia de alto y las columnas se descuadran unos píxeles: se corrige con `altura_mapa`. El mapa es de zoom fijo (5,75) y centro `[-9,6, -76,7]`: con menos de ~750 px de alto o menos de ~620 px de ancho el país no entra entero.

**Los colores están congelados por nombre de categoría** en `rea/estilo.py`. Si se
asignaran por frecuencia, una actualización repintaría las categorías y rompería la
comparabilidad entre versiones del tablero.

**El sombreado del mapa F es gris, no azul, y de una sola tinta.** Una rampa azul bajo
marcadores azules pondría magnitud e identidad en la misma familia de color. Y la tinta
(`#e0dcd0`) no puede ser más oscura: medido, sobre `#7a756a` los cuatro colores caen por
debajo de 2:1 de contraste, mientras que sobre `#e0dcd0` azul, verde y violeta quedan en
3,2 / 3,6 / 6,2. Con provincias, 27 de las 33 que tienen denuncias tienen solo 1 o 2:
una escala de tonos casi no graduaría, y la magnitud la llevan el número y la burbuja.

**«Ciudadanos listados» trae su desglose por tipo.** Solo 21 de las 67 denuncias traen la cifra, y Padrón y Suspensión de depuración no traen ninguna: se muestran como «sin dato», nunca como 0. Cada barra lleva en su recuadro la cobertura del tipo («consta en 17 de 39 denuncias»). Una sola denuncia (Urarinas, Loreto: 1 986) pesa el 39 % del total.

**Las cajas de cifras se adaptan al ancho de su contenedor** (consulta de contenedor de CSS). Con 600 px o más van cuatro en una fila, con la de ciudadanos al doble de ancho; con menos, las tres simples ocupan una fila y la de ciudadanos la suya; con menos de 400 px, una columna. Así ningún texto queda apretado ni cortado.

**El mapa se guarda ya renderizado.** Renderizar dos veces el mismo objeto de folium da HTML
distinto (la segunda vez agrega `addTo(map)` sueltos y el mapa llega sin marcadores). Por eso
`rea/mapas.py` guarda en caché el **HTML** de cada mapa, con la huella de `configuracion.toml`
en la llave, y la app F lo sirve en un `iframe`. Un cambio de texto en el `.toml` renueva el mapa.

**La tabla no es un extra.** La queja de fondo —«la imagen se ve muy pequeña»— no se
arregla agrandando el mapa, sino haciendo que ninguna cifra dependa de leerlo. Y es
una sola, con una fila por denuncia: se lee entera y trae casi toda la información
del Excel.

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
