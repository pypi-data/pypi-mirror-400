
# colorstreak

`colorstreak` es una mini-lib para imprimir logs en la terminal con colores ANSI, sin acoplarte a un framework de logging.
La API está pensada para sentirse como `print()` (acepta `sep`, `end`, `file`, `flush`) pero con niveles semánticos.

## ¿Qué resuelve?

- Salida de terminal más legible (debug/info/warning/error/success, etc.).
- Un prefijo consistente por nivel (ej: `[INFO]`).
- Control simple del estilo (solo prefijo, todo coloreado, o “soft”).
- Compatibilidad con `NO_COLOR` para desactivar colores.

## Instalación

```bash
pip install colorstreak
```

## Uso rápido

```python
from colorstreak import Logger

Logger.info("Servidor arriba")
Logger.warning("Cache fría")
Logger.error("No se pudo conectar")
Logger.success("Deploy OK")
```

## Estilos

Hay 3 estilos de salida:

- `full` (default): prefijo y mensaje coloreados
- `prefix`: solo el prefijo coloreado
- `soft`: prefijo resaltado y mensaje atenuado

Configúralo en runtime:

```python
from colorstreak import Logger

Logger.configure(style="soft")
```

O por variable de entorno:

```bash
export COLORSTREAK_STYLE=prefix
```

## Desactivar colores

Si tu entorno no soporta ANSI o quieres logs “planos”, usa `NO_COLOR`:

```bash
export NO_COLOR=1
```

## Niveles disponibles

Base:

- `Logger.debug()`
- `Logger.info()`
- `Logger.warning()`
- `Logger.error()`
- `Logger.library()`
- `Logger.success()`

Helpers:

- `Logger.step()`
- `Logger.note()`
- `Logger.title()`
- `Logger.metric()`

## Compatible con print()

Cada método acepta `sep=`, `end=`, `file=`, `flush=` igual que `print()`:

```python
from colorstreak import Logger

Logger.info("Multiple", "args", 123, sep=" | ")
Logger.warning("Sin salto...", end="")
Logger.warning(" <- continúa")
```
