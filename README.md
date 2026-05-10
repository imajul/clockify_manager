# Clockify Manager

Herramienta para registrar horas en [Clockify](https://clockify.me) desde una interfaz web o directamente desde GitHub Actions. Permite distribuir horas de trabajo entre proyectos por día, semana o entrada individual, y las carga automáticamente via API.

---

## Índice

1. [Descripción general](#1-descripción-general)
2. [Requisitos previos](#2-requisitos-previos)
3. [Paso 1 — Hacer fork del repositorio](#3-paso-1--hacer-fork-del-repositorio)
4. [Paso 2 — Obtener el API Key de Clockify](#4-paso-2--obtener-el-api-key-de-clockify)
5. [Paso 3 — Obtener el Workspace ID de Clockify](#5-paso-3--obtener-el-workspace-id-de-clockify)
6. [Paso 4 — Crear un Personal Access Token de GitHub](#6-paso-4--crear-un-personal-access-token-de-github)
7. [Paso 5 — Agregar secrets al repositorio](#7-paso-5--agregar-secrets-al-repositorio)
8. [Paso 6 — Habilitar GitHub Pages](#8-paso-6--habilitar-github-pages)
9. [Paso 7 — Configurar la interfaz web](#9-paso-7--configurar-la-interfaz-web)
10. [Cómo usar la interfaz web](#10-cómo-usar-la-interfaz-web)
11. [Actualizar la lista de proyectos](#11-actualizar-la-lista-de-proyectos)
12. [Cargar horas desde GitHub Actions](#12-cargar-horas-desde-github-actions)
13. [Configurar el schedule semanal](#13-configurar-el-schedule-semanal)
14. [Uso local (Python)](#14-uso-local-python)

---

## 1. Descripción general

El sistema tiene tres componentes:

| Componente | Descripción |
|---|---|
| **Interfaz web** | Página en GitHub Pages para distribuir horas entre proyectos visualmente, día a día |
| **GitHub Actions** | Workflow que ejecuta el script Python para cargar las horas en Clockify |
| **Script Python** | `scripts/log_hours.py` — se conecta a la API de Clockify y crea las entradas |

**Flujo típico de uso:**

1. Abrís la interfaz web → seleccionás los días trabajados → distribuís porcentajes por proyecto → presionás *Cargar a Clockify*.
2. La web genera un archivo `entries.yml` con las entradas y lo sube al repositorio via API de GitHub.
3. GitHub Actions detecta el archivo y ejecuta el script Python que carga todo en Clockify.

---

## 2. Requisitos previos

- Cuenta en [Clockify](https://clockify.me) (el plan gratuito es suficiente)
- Cuenta en [GitHub](https://github.com) con acceso al repositorio

No necesitás instalar nada en tu computadora para usar la interfaz web.

---

## 3. Paso 1 — Hacer fork del repositorio

1. Entrá a la página del repositorio en GitHub.
2. Hacé clic en el botón **Fork** (arriba a la derecha).
3. Elegí tu cuenta personal como destino y confirmá.

Esto crea una copia del repositorio en tu cuenta, sobre la cual vas a configurar todo.

---

## 4. Paso 2 — Obtener el API Key de Clockify

1. Iniciá sesión en [clockify.me](https://clockify.me).
2. Hacé clic en tu **avatar** (arriba a la derecha) → **Profile Settings**.
3. Bajá hasta la sección **API**.
4. Copiá el valor del campo **API Key**.

Guardalo en un lugar seguro, lo vas a necesitar en los pasos siguientes.

---

## 5. Paso 3 — Obtener el Workspace ID de Clockify

El Workspace ID es opcional (se auto-detecta si no lo configurás), pero se recomienda fijarlo explícitamente.

1. En Clockify, hacé clic en tu nombre de workspace (barra lateral izquierda, arriba).
2. Seleccioná **Workspace Settings**.
3. Copiá la URL del navegador — el ID es la cadena alfanumérica que aparece en ella:
   ```
   https://app.clockify.me/en/settings/workspace/XXXXXXXXXXXXXXXXXXXXXXXX
                                                   ^^^^^^^^^^^^^^^^^^^^^^^^
                                                   este es el Workspace ID
   ```

---

## 6. Paso 4 — Crear un Personal Access Token de GitHub

La interfaz web necesita un token de GitHub para poder subir archivos y disparar el workflow de Actions directamente desde el navegador.

1. Iniciá sesión en GitHub → hacé clic en tu **avatar** (arriba a la derecha) → **Settings**.
2. En el menú lateral izquierdo, bajá hasta el final y hacé clic en **Developer settings**.
3. Seleccioná **Personal access tokens** → **Tokens (classic)**.
4. Hacé clic en **Generate new token** → **Generate new token (classic)**.
5. Completá los campos:
   - **Note:** `Clockify Manager` (cualquier nombre descriptivo)
   - **Expiration:** elegí la duración que prefieras (90 días o sin vencimiento)
   - **Scopes:** tildá únicamente **`repo`** (incluye lectura/escritura al repositorio y permisos para disparar workflows)
6. Hacé clic en **Generate token** al final de la página.
7. **Copiá el token inmediatamente** — solo se muestra una vez. Empieza con `ghp_`.

---

## 7. Paso 5 — Agregar secrets al repositorio

Los secrets son variables cifradas que usa GitHub Actions para conectarse a Clockify sin exponer las credenciales en el código.

1. En tu repositorio de GitHub, andá a **Settings** → **Secrets and variables** → **Actions**.
2. Hacé clic en **New repository secret** para cada uno de los siguientes:

| Nombre del secret | Valor | Obligatorio |
|---|---|---|
| `CLOCKIFY_API_KEY` | Tu API Key de Clockify (del Paso 2) | Sí |
| `CLOCKIFY_WORKSPACE_ID` | Tu Workspace ID (del Paso 3) | No (se auto-detecta) |

---

## 8. Paso 6 — Habilitar GitHub Pages

La interfaz web se sirve automáticamente desde la carpeta `docs/` de la rama `main`.

1. En tu repositorio, andá a **Settings** → **Pages** (menú lateral, sección *Code and automation*).
2. En **Source**, seleccioná **Deploy from a branch**.
3. En **Branch**, elegí `main` y la carpeta `/docs`.
4. Hacé clic en **Save**.

Después de unos segundos, GitHub muestra la URL de tu página. Tiene el formato:

```
https://<tu-usuario>.github.io/<nombre-del-repo>/
```

---

## 9. Paso 7 — Configurar la interfaz web

La primera vez que abrís la interfaz web, necesitás ingresar tus credenciales. Se guardan en el almacenamiento local del navegador y nunca se suben a ningún servidor.

1. Abrí la URL de tu GitHub Pages (del paso anterior).
2. Hacé clic en el ícono de engranaje ⚙️ (arriba a la derecha) para abrir la configuración.
3. Completá los cuatro campos:

| Campo | Valor |
|---|---|
| **GitHub Token** | El Personal Access Token que creaste en el Paso 4 (empieza con `ghp_`) |
| **Repositorio** | Tu repositorio en formato `usuario/nombre-repo` (ej: `juanperez/clockify_manager`) |
| **Clockify API Key** | Tu API Key de Clockify (del Paso 2) |
| **Workspace ID** | Tu Workspace ID de Clockify (del Paso 3) |

4. Hacé clic en **Guardar**.

---

## 10. Cómo usar la interfaz web

### Seleccionar días trabajados

- El calendario muestra el mes actual. Los fines de semana están deshabilitados.
- Hacé clic en los días que trabajaste para seleccionarlos (se resaltan en azul).
- Para cambiar de mes usá las flechas `‹` `›`.

### Agregar proyectos

1. Hacé clic en **+ Agregar proyecto**.
2. Seleccioná el **proyecto** del menú desplegable.
3. Seleccioná el **cliente** (el menú se filtra según el proyecto elegido).
4. Seleccioná la **etiqueta** (tipo de trabajo): *Ejecución de Ingeniería*, *Gestión de Ingeniería*, *Revisión de Ingeniería*, o *Visita a Obra*.
5. Ajustá el **porcentaje** de horas con el slider o escribiendo el número directamente.
6. Repetí para cada proyecto adicional.

> El total de porcentajes debe sumar exactamente 100 %. La barra inferior indica si está OK o si falta ajustar.

### Vista previa en grilla

La grilla de la derecha muestra cómo quedan distribuidas las entradas por día. Los bloques de color representan entradas; los bloques punteados grises indican que ese día no tiene horas asignadas.

Cada día laboral tiene **8 horas** distribuidas en dos tramos: mañana (09:00–13:00) y tarde (14:00–18:00). La distribución se hace con granularidad de 1 hora, y los bloques consecutivos del mismo proyecto se combinan automáticamente en una sola entrada.

### Cargar las horas

1. Hacé clic en **Vista previa** para ver exactamente qué entradas se van a crear.
2. Si todo está bien, hacé clic en **Cargar a Clockify**.
3. La web verifica si ya existen entradas en Clockify para esos días:
   - Si hay **superposición**, te consulta si querés saltear los conflictos o sobreescribir.
4. Una vez confirmado, se genera el archivo `entries.yml`, se sube al repositorio y se dispara el workflow de GitHub Actions.
5. El workflow tarda ~1–2 minutos. Podés seguirlo en **Actions** → **Log Hours to Clockify**.

---

## 11. Actualizar la lista de proyectos

La interfaz web carga los proyectos y clientes disponibles desde el archivo `docs/projects.json`, que se genera automáticamente a partir de un Excel exportado de Clockify.

### Exportar el Excel desde Clockify

1. En Clockify, andá a **Projects** (menú lateral).
2. Hacé clic en el ícono de exportación (arriba a la derecha) → **Export as Excel**.
3. El archivo descargado tiene las columnas **Name** (proyecto) y **Client** (cliente), que es exactamente el formato que espera el script.

### Subir el Excel al repositorio

1. En tu repositorio de GitHub, hacé clic en **Add file → Upload files**.
2. Subí el archivo con el nombre exacto **`projects.xlsx`** (en la raíz del repositorio).
3. Hacé clic en **Commit changes** → **Commit directly to the `main` branch**.

Eso es todo. El workflow **Convert Projects Excel to JSON** se dispara automáticamente, convierte el Excel al archivo `docs/projects.json` y hace el commit. En la próxima apertura de la interfaz web ya aparecen los proyectos actualizados.

> Si subís el Excel con otro nombre, el workflow no se dispara. El nombre debe ser exactamente `projects.xlsx`.

---

## 12. Cargar horas desde GitHub Actions


También podés disparar el workflow manualmente desde GitHub para casos puntuales.

Ir a: **Actions** → **Log Hours to Clockify** → **Run workflow**

### Modo `weekly` — Carga semanal desde schedule

Carga todas las horas de una semana según el archivo `weekly_schedule.yml`.

| Campo | Descripción |
|---|---|
| Mode | `weekly` |
| Week start | Lunes de la semana a cargar (`YYYY-MM-DD`). Vacío = semana actual. |
| Schedule file | Ruta al archivo (default: `weekly_schedule.yml`) |
| Dry run | `true` para previsualizar sin crear entradas |

**Recomendación:** probá siempre con `dry run: true` antes de crear las entradas reales.

### Modo `single` — Una sola entrada

| Campo | Ejemplo |
|---|---|
| Mode | `single` |
| Date | `2026-05-09` |
| Start time | `09:00` |
| End time | `18:00` |
| Description | `Desarrollo` |
| Project | `BESS AMBA` |
| Billable | `true` / `false` |

### Modo `batch` — Múltiples entradas desde archivo

Creá un archivo `entries.yml` en la raíz del repositorio con el siguiente formato y luego corré el workflow con Mode = `batch`:

```yaml
timezone: "America/Argentina/Buenos_Aires"

entries:
  - date: "2026-05-09"
    start: "09:00"
    end: "13:00"
    description: "Desarrollo"
    project: "BESS AMBA"
    client: "DNN"
    billable: true
    tags:
      - "Ejecución de Ingenieria"

  - date: "2026-05-09"
    start: "14:00"
    end: "18:00"
    description: "Reuniones"
    project: "CTBRA"
    client: "O&M"
    billable: false
```

---

## 13. Configurar el schedule semanal

El archivo `weekly_schedule.yml` define un horario recurrente que se aplica semana a semana. Es útil si tenés una distribución fija de proyectos.

### Estructura del archivo

```yaml
timezone: "America/Argentina/Buenos_Aires"

# Horario por defecto — se aplica todas las semanas
default:
  monday:
    - start: "09:00"
      end: "13:00"
      description: "Desarrollo"
      project: "BESS AMBA"
      client: "DNN"
      billable: true
    - start: "14:00"
      end: "18:00"
      description: "Reuniones"
      project: "CTBRA"
      client: "O&M"
      billable: false

  tuesday:
    - start: "09:00"
      end: "18:00"
      description: "Desarrollo"
      project: "ALMA SADI"
      client: "DNN"
      billable: true

  # wednesday: []   # feriado o día libre permanente

# Semanas con variaciones (clave = lunes de la semana en YYYY-MM-DD)
weeks:
  "2026-05-11":
    wednesday: []     # día libre solo esa semana
    friday:
      - start: "09:00"
        end: "18:00"
        description: "Entrega sprint"
        project: "BESS AMBA"
        client: "DNN"
        billable: true
```

### Reglas

| Situación | Cómo hacerlo |
|---|---|
| Día libre permanente | No listar el día en `default` |
| Día libre una semana puntual | `wednesday: []` bajo `weeks.YYYY-MM-DD` |
| Semana distinta al default | Agregar la semana bajo `weeks` con solo los días que cambian |
| Cambiar proyectos para siempre | Actualizar los `project` en `default` |

### Campos por entrada

| Campo | Requerido | Descripción |
|---|---|---|
| `start` / `end` | Sí | Hora en formato `HH:MM`, en la zona horaria del archivo |
| `description` | Sí | Texto libre |
| `project` | No | Nombre exacto del proyecto en Clockify |
| `client` | No | Nombre exacto del cliente (necesario si un proyecto tiene varios clientes) |
| `billable` | No | `true` / `false` (default: `false`) |
| `tags` | No | Lista de nombres de tags de Clockify |

---

## 14. Uso local (Python)

Si preferís ejecutar el script directamente desde tu computadora sin GitHub Actions:

### Instalación

```bash
pip install requests pyyaml tzdata
```

### Variables de entorno

```bash
export CLOCKIFY_API_KEY=tu_api_key
export CLOCKIFY_WORKSPACE_ID=tu_workspace_id   # opcional
```

### Comandos

```bash
# Previsualizar la semana actual (sin crear entradas)
python scripts/log_hours.py weekly --schedule weekly_schedule.yml --dry-run

# Cargar la semana actual
python scripts/log_hours.py weekly --schedule weekly_schedule.yml

# Cargar una semana específica
python scripts/log_hours.py weekly --schedule weekly_schedule.yml --week 2026-05-04

# Entrada individual
python scripts/log_hours.py single \
  --date 2026-05-09 --start 09:00 --end 18:00 \
  --description "Desarrollo" --project "BESS AMBA" \
  --timezone "America/Argentina/Buenos_Aires"

# Batch desde archivo (previsualizar primero)
python scripts/log_hours.py batch --file entries.yml --dry-run
python scripts/log_hours.py batch --file entries.yml
```

### Detección de superposición

El script verifica automáticamente que no haya entradas que se superpongan, tanto entre las entradas nuevas como contra las ya existentes en Clockify. Si detecta un conflicto, cancela toda la carga y muestra un mensaje indicando qué entradas se superponen.
