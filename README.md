# Clockify Manager

GitHub Actions workflow to log time entries to [Clockify](https://clockify.me) via API.

## Setup

### 1. Obtener el API Key de Clockify

Clockify → avatar → **Profile Settings** → sección **API** → copiar el key.

### 2. Agregar secrets al repositorio

**Settings → Secrets and variables → Actions → New repository secret:**

| Secret | Descripción |
|---|---|
| `CLOCKIFY_API_KEY` | Tu API key de Clockify |
| `CLOCKIFY_WORKSPACE_ID` | *(Opcional)* — se auto-detecta si no lo ponés |

### 3. Crear el archivo de schedule

```bash
cp weekly_schedule.example.yml weekly_schedule.yml
```

Editá `weekly_schedule.yml` con tus proyectos y horarios reales (ver sección abajo).

---

## Modos

### `weekly` — Carga masiva semanal *(modo principal)*

Carga todas las horas de una semana según tu archivo de schedule.

**Actions → Log Hours to Clockify → Run workflow:**

| Campo | Descripción |
|---|---|
| Mode | `weekly` |
| Week start | Lunes de la semana a cargar (`2026-05-04`). Vacío = semana actual. |
| Schedule file | Ruta al archivo de schedule (default: `weekly_schedule.yml`) |
| Dry run | `true` para previsualizar sin crear entradas |

**Recomendación:** primero corré con `dry run: true` para verificar las entradas, luego con `false`.

---

### `single` — Una sola entrada

| Campo | Ejemplo |
|---|---|
| Date | `2026-05-09` |
| Start / End time | `09:00` / `18:00` |
| Description | `Desarrollo` |
| Project | `Mi Proyecto` *(opcional)* |
| Billable | `true` / `false` |

---

### `batch` — Múltiples entradas desde archivo

Copiá `entries.example.yml` a `entries.yml`, completalo y corrés el workflow con mode `batch`.

---

## Configurar el schedule semanal

Editá `weekly_schedule.yml` (copiado desde `weekly_schedule.example.yml`):

```yaml
timezone: "America/Argentina/Buenos_Aires"

# Horario por defecto, aplicado todas las semanas
default:
  monday:
    - start: "09:00"
      end: "13:00"
      description: "Desarrollo"
      project: "Proyecto A"
      billable: true
    - start: "14:00"
      end: "18:00"
      description: "Reuniones"
      project: "Proyecto B"
      billable: false

  tuesday:
    - start: "09:00"
      end: "18:00"
      description: "Desarrollo"
      project: "Proyecto A"
      billable: true

  # wednesday: []   # día libre — omitir o lista vacía

  thursday:
    - start: "09:00"
      end: "18:00"
      description: "Desarrollo"
      project: "Proyecto B"
      billable: true

  friday:
    - start: "09:00"
      end: "14:00"
      description: "Desarrollo"
      project: "Proyecto A"
      billable: true

# Semanas con variaciones (clave = lunes de la semana)
weeks:
  "2026-05-11":
    wednesday: []          # feriado
    friday:
      - start: "09:00"
        end: "18:00"
        description: "Entrega sprint"
        project: "Proyecto C"
        billable: true
```

### Reglas del schedule

| Situación | Cómo hacerlo |
|---|---|
| Día libre permanente | No listar el día en `default` |
| Día libre una semana puntual | `wednesday: []` bajo `weeks.YYYY-MM-DD` |
| Semana distinta al default | Agregar la semana bajo `weeks` con solo los días que cambian |
| Cambio de proyecto | Actualizar los `project` en `default` |

### Campos por entrada

| Campo | Requerido | Descripción |
|---|---|---|
| `start` / `end` | Sí | `HH:MM` en la zona horaria del archivo |
| `description` | Sí | Texto libre |
| `project` | No | Nombre exacto del proyecto en Clockify |
| `project_id` | No | ID del proyecto (alternativa a `project`) |
| `billable` | No | `true` / `false` (default: `false`) |
| `tag_ids` | No | Lista de IDs de tags de Clockify |

---

## Uso local

```bash
pip install requests pyyaml tzdata

export CLOCKIFY_API_KEY=tu_api_key

# Previsualizar la semana actual
python scripts/log_hours.py weekly --schedule weekly_schedule.yml --dry-run

# Cargar la semana actual
python scripts/log_hours.py weekly --schedule weekly_schedule.yml

# Cargar una semana específica
python scripts/log_hours.py weekly --schedule weekly_schedule.yml --week 2026-05-04

# Entrada individual
python scripts/log_hours.py single \
  --date 2026-05-09 --start 09:00 --end 18:00 \
  --description "Desarrollo" --project "Mi Proyecto" \
  --timezone "America/Argentina/Buenos_Aires"

# Batch
python scripts/log_hours.py batch --file entries.yml --dry-run
```
