# Limpieza de los catálogos de recursos SAMUR (bases, hospitales y unidades)

Limpieza de los tres catálogos de recursos que quedaban sin limpiar: `bases_samur.csv`, `hospitales.csv` y `unidades_samur.csv`. Un notebook por dataset en `cleaning/`, con cada decisión explicada, y un CSV limpio por cada uno en `data_clean/`. Los CSV originales no se tocan.

- `limpieza_bases_samur.ipynb` -> `bases_samur_limpio.csv` (15 filas)
- `limpieza_hospitales.ipynb` -> `hospitales_limpio.csv` (20 filas)
- `limpieza_unidades_samur.ipynb` -> `unidades_samur_limpio.csv` (60 filas)

Mismas reglas que en el resto de limpiezas del caso: normalización por reglas (mayúsculas, sin tildes, sin artículo del principio; un texto se completa solo si es el principio de una única categoría o distrito oficial), sin diccionarios cerrados. Lo que no se puede saber no se inventa: queda vacío, como `NO CONSTA` o con su texto original, y se documenta.

**Ojo con `cruces_datasets.ipynb`:** los CSV limpios NO son un reemplazo directo de lo que hacen los cruces hoy. Hay dos diferencias conscientes, documentadas abajo: las 10 unidades de `VALLECAS` quedan sin asignar (en los cruces se contaron en Puente de Vallecas por inferencia) y las camas imposibles de 2 hospitales pasan a vacío. Si algún día los cruces se rehacen sobre los limpios, esos dos puntos cambian números de `tabla_distritos.csv` y hay que decidirlo, no asumirlo.

## Bases (`bases_samur_limpio.csv`, 15 filas)

- **Distrito:** venía con mayúsculas y minúsculas mezcladas y un artículo (`La Latina`). Con la regla de siempre las 15 bases quedan con su distrito oficial.
- **Tipo de base:** solo cambiaba la escritura (`principal`, `PRINCIPAL`, `Secundaria`...). Quedan las 4 categorías reales: `PRINCIPAL`, `SECUNDARIA`, `SATELITE` y `AUXILIAR`. No hizo falta ninguna equivalencia.
- **Coordenadas imposibles:** Base Hortaleza (latitud -95,2), Base Barajas (latitud 91,5) y Base Moncloa (longitud 185) están fuera del rango posible de Madrid. Pasan a vacío: no sabemos las coordenadas reales y no las inventamos. Las bases se conservan con el resto de sus datos.
- **Año de apertura:** faltaba en 2 bases (Base Vallecas y Base Vicálvaro). No hay otra tabla del proyecto donde mirarlo, así que queda vacío. El año se deja como entero (venía como `1985.0`).
- No hay filas repetidas: las 15 filas se quedan.

## Hospitales (`hospitales_limpio.csv`, 20 filas)

- **Tipo:** solo cambiaba la escritura (`Público`, `PRIVADO`, `publico`...). Quedan las 3 categorías reales: `PUBLICO`, `PRIVADO` y `PRIVADO-CONCERTADO`.
- **Nombre corto:** mismo formato que el resto de textos (mayúsculas, sin tildes), para que un mismo hospital no aparezca escrito de dos formas.
- **Distrito o municipio:** 10 hospitales están en distritos de Madrid y quedan con el nombre oficial. Los demás no se fuerzan:
  - 9 son hospitales de otros municipios (Getafe, Móstoles, Alcorcón...): el dato es real, así que se conserva el nombre del municipio. Es la misma situación que en `accidentes.csv`: fuera del término municipal no hay datos socioeconómicos con los que cruzar, y en los cruces ya quedan fuera de la oferta por distrito.
  - El Hospital Infanta Leonor trae `VALLECAS` a secas: no sabemos si es Puente o Villa de Vallecas, y un hospital no sale de una base del SAMUR, así que no se puede aplicar el criterio de las unidades. Se queda como `VALLECAS`, sin asignar, igual que las activaciones de `VALLECAS`.
- **Camas:** 5 hospitales se quedan sin dato. Tres ya venían vacíos (Fundación Jiménez Díaz, Príncipe de Asturias y H. Móstoles) y dos traían -50, un valor imposible, que pasa a vacío. No se inventa el dato; cuando hace falta un número, `cruces_datasets.ipynb` ya lo trata allí (un hospital sin camas no cuenta como 0).
- `urgencias_24h` y `helipad` ya venían bien (solo 0 y 1) y no se tocan.

## Unidades (`unidades_samur_limpio.csv`, 60 filas)

- **Clave buena:** `unidad_id` no se repite. El `codigo` se repite en 10 parejas: 8 se contradicen en algo (tipo, estado o kilómetros) y 2 son iguales en todo menos en el id. Como no podemos saber si esas 2 son la misma unidad registrada dos veces, se conservan todas las filas y se documenta, igual que en activaciones. Para cruzar: siempre por `unidad_id`, nunca por `codigo`.
- **Tipo de unidad:** venía con puntos y mayúsculas mezcladas (`UVI`, `U.V.I.`, `uvi`). Quitando puntos y poniendo mayúsculas quedan las 5 categorías reales: `UVI`, `SVB`, `VIR`, `MOTO` y `JEFATURA`. Las 8 filas sin tipo quedan vacías.
- **Estado:** se normaliza por escritura y `MANT` pasa a `MANTENIMIENTO` por la regla del principio único. `OK` se queda como categoría propia: seguramente quiera decir "operativa", pero no podemos comprobarlo y no inventamos la equivalencia. Categorías finales: `OPERATIVA`, `MANTENIMIENTO`, `BAJA`, `INACTIVA` y `OK`.
- **Distrito de la base:** misma regla de nombres. `FUENCARRAL` pasa a `FUENCARRAL-EL PARDO` (único distrito oficial que empieza así). **`VALLECAS` se queda como `VALLECAS`, sin asignar:** es principio de dos distritos y no hay fuente que diga a cuál pertenece cada unidad. En `cruces_datasets.ipynb` esas 10 unidades se contaron en Puente de Vallecas por inferencia (es el único de los dos con base en el catálogo), pero el catálogo podría estar incompleto, así que aquí lo dejamos explícito y pendiente de confirmar con Bluetab: el número de unidades de Puente en `tabla_distritos.csv` depende de esa suposición. Las 5 unidades sin distrito quedan como `NO CONSTA`, igual que en activaciones.
- **Año de adquisición:** los datos se entregaron con el proyecto en septiembre de 2026 (correo de Bluetab del 15/09/2026). 2 unidades traen 2029, posterior a la propia entrega del dataset y con kilómetros ya registrados: imposible, pasa a vacío. Otras 2 traen 2026, que sí es posible, y se conservan. No asumimos que el catálogo sea una foto de 2024 solo porque las activaciones sean de 2024.
- **Kilómetros:** 5 unidades traen kilómetros negativos, imposible. Pasan a vacío. Los valores altos (máximo 1.447.628 km) se quedan: son muchos pero no imposibles, y no hay ninguna regla que los descarte.

## Huecos que quedan (resumen)

Ningún hueco se ha rellenado inventando datos:

- Bases: 3 coordenadas y 2 años de apertura.
- Hospitales: 5 camas.
- Unidades: 8 tipos de unidad, 5 distritos de base (`NO CONSTA`) más 10 `VALLECAS` sin asignar, 2 años y 5 kilómetros.
