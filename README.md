# Clockify Manager

Herramienta para registrar horas en Clockify desde una página web sencilla, sin necesidad de instalar nada en tu computadora.

> **¿Nunca usaste GitHub?** No hay problema. Esta guía te explica cada paso desde cero, incluyendo qué es cada cosa y exactamente dónde hacer clic.

---

## Índice

- [¿Cómo funciona?](#cómo-funciona)
- [Lo que vas a necesitar antes de empezar](#lo-que-vas-a-necesitar-antes-de-empezar)
- [Paso 1 — Crear tu copia del repositorio (Fork)](#paso-1--crear-tu-copia-del-repositorio-fork)
- [Paso 2 — Obtener tu clave de API de Clockify](#paso-2--obtener-tu-clave-de-api-de-clockify)
- [Paso 3 — Obtener tu Workspace ID de Clockify](#paso-3--obtener-tu-workspace-id-de-clockify)
- [Paso 4 — Crear un token de acceso en GitHub](#paso-4--crear-un-token-de-acceso-en-github)
- [Paso 5 — Guardar tus claves en el repositorio](#paso-5--guardar-tus-claves-en-el-repositorio)
- [Paso 6 — Activar tu página web](#paso-6--activar-tu-página-web)
- [Paso 7 — Configurar la página web por primera vez](#paso-7--configurar-la-página-web-por-primera-vez)
- [Cómo usar la página web día a día](#cómo-usar-la-página-web-día-a-día)
- [Cómo actualizar la lista de proyectos](#cómo-actualizar-la-lista-de-proyectos)
- [Preguntas frecuentes](#preguntas-frecuentes)
- [Uso avanzado](#uso-avanzado)

---

## ¿Cómo funciona?

La herramienta tiene tres partes que trabajan juntas automáticamente:

| Parte | Qué es | Para qué sirve |
|---|---|---|
| **Página web** | Una web que vos abrís desde el navegador | Elegís los días y proyectos, y apretás un botón para cargar |
| **GitHub** | Un sitio web gratuito que guarda el código | Actúa como intermediario y ejecuta la carga automáticamente |
| **Clockify** | Tu sistema de registro de horas | Donde quedan guardadas las entradas finalmente |

**El proceso, en palabras simples:**

1. Abrís la página web → elegís los días trabajados → asignás proyectos → apretás *Cargar a Clockify*
2. La página sube un archivo con las horas a tu repositorio de GitHub
3. GitHub detecta ese archivo y ejecuta automáticamente el proceso que carga todo en Clockify
4. En 1–2 minutos, las horas aparecen en Clockify

---

## Lo que vas a necesitar antes de empezar

- **Una cuenta en Clockify** → [clockify.me](https://clockify.me) (el plan gratuito es suficiente)
- **Una cuenta en GitHub** → [github.com](https://github.com) (también gratuita)
- **Un navegador web** (Chrome, Firefox, Edge — el que uses normalmente)

No necesitás instalar ningún programa ni saber programar.

---

## Paso 1 — Crear tu copia del repositorio (Fork)

> **¿Qué es un repositorio?** Es como una carpeta en la nube que contiene todos los archivos del proyecto. Está alojada en GitHub.
>
> **¿Qué es un Fork?** Es hacer una copia de esa carpeta en tu propia cuenta de GitHub. Vas a trabajar sobre esa copia, no sobre el original.

### Pasos:

1. Abrí la página principal de este repositorio en GitHub (la misma donde estás leyendo esto).

2. Buscá el botón **Fork** en la esquina superior derecha de la página y hacé clic en él.

3. Se abre una pantalla que pregunta dónde crear la copia. Bajo **Owner**, asegurate de que esté seleccionada **tu cuenta personal** (no la de otra organización).

4. Dejá el nombre como está y hacé clic en el botón verde **Create fork**.

5. GitHub te redirige automáticamente a tu nueva copia del repositorio. La URL debería decir `github.com/TU-USUARIO/clockify_manager`.

> ✅ **¿Cómo sé que funcionó?** En la esquina superior izquierda vas a ver el nombre de tu repositorio con una leyenda que dice *"forked from ..."*

---

## Paso 2 — Obtener tu clave de API de Clockify

> **¿Qué es una API Key?** Es una contraseña especial que le permite a esta herramienta hablar con Clockify en tu nombre. Clockify la genera automáticamente para vos.

### Pasos:

1. Abrí [clockify.me](https://clockify.me) e iniciá sesión con tu usuario y contraseña.

2. Hacé clic en tu **foto de perfil o iniciales** en la esquina superior derecha.

3. En el menú que aparece, hacé clic en **Profile Settings**.

4. En la página de configuración, bajá con el scroll hasta encontrar la sección **API**.

5. Vas a ver un campo que dice **API Key** con una cadena de letras y números. Hacé clic en el ícono de copiar que está al lado.

6. Guardá ese texto en un lugar seguro (por ejemplo, en un archivo de texto o en el Bloc de Notas). Lo vas a necesitar en los pasos 5 y 7.

> ⚠️ **Importante:** Esta clave es como una contraseña. No la compartas con nadie ni la publiques en ningún lado.

---

## Paso 3 — Obtener tu Workspace ID de Clockify

> **¿Qué es el Workspace?** Es el espacio de trabajo dentro de Clockify donde están todos tus proyectos. El Workspace ID es el número identificador de ese espacio.

### Pasos:

1. Estando en Clockify, mirá la barra lateral izquierda. Arriba del todo vas a ver el nombre de tu workspace (generalmente es tu nombre o el nombre de tu empresa).

2. Hacé clic en ese nombre. Aparece un menú desplegable.

3. Hacé clic en **Workspace Settings**.

4. Mirá la barra de direcciones de tu navegador. La URL va a tener un formato similar a este:

   ```
   https://app.clockify.me/en/settings/workspace/XXXXXXXXXXXXXXXXXXXXXXXX
   ```

5. La parte que está al final, después de `/workspace/`, es tu **Workspace ID**. Copiá esa cadena de letras y números y guardala junto con tu API Key.

> 💡 **Consejo:** Si no encontrás el Workspace ID, no te preocupes. La herramienta puede detectarlo automáticamente. Podés dejarlo vacío en los pasos siguientes.

---

## Paso 4 — Crear un token de acceso en GitHub

> **¿Para qué sirve esto?** La página web necesita un permiso especial para poder guardar archivos en tu repositorio de GitHub y disparar el proceso automático. Ese permiso es el "Personal Access Token" — es como una contraseña de un solo uso para aplicaciones.

### Pasos:

1. Abrí [github.com](https://github.com) e iniciá sesión.

2. Hacé clic en tu **foto de perfil** en la esquina superior derecha → **Settings**.

3. En la página de configuración, buscá el menú lateral izquierdo. Bajá hasta el final del todo y hacé clic en **Developer settings**.

4. En la nueva página, hacé clic en **Personal access tokens** → **Tokens (classic)**.

5. Hacé clic en el botón **Generate new token** → **Generate new token (classic)**.

6. GitHub puede pedirte que confirmes tu contraseña. Ingresala si es necesario.

7. Completá el formulario:
   - **Note:** Escribí `Clockify Manager` (es solo un nombre para que recuerdes para qué es)
   - **Expiration:** Elegí cuánto tiempo querés que dure. Si no querés renovarlo periódicamente, elegí **No expiration**
   - **Select scopes:** Buscá la opción **`repo`** y tildá la casilla que está al lado. Con eso es suficiente.

8. Bajá hasta el final de la página y hacé clic en el botón verde **Generate token**.

9. La página muestra el token una sola vez, comenzando con `ghp_`. **Copialo ahora** y guardalo junto con tus otros datos, porque no vas a poder verlo de nuevo.

> ⚠️ **Importante:** Si cerrás esta página sin copiarlo, tendrás que generar uno nuevo. No hay forma de recuperarlo.

---

## Paso 5 — Guardar tus claves en el repositorio

> **¿Qué son los "Secrets"?** Son variables secretas que GitHub guarda de forma cifrada. El proceso automático las usa para conectarse a Clockify, pero nadie puede verlas (ni vos desde GitHub). Es la forma segura de guardar contraseñas en este tipo de herramientas.

### Pasos:

1. Andá a tu repositorio en GitHub (`github.com/TU-USUARIO/clockify_manager`).

2. Hacé clic en la pestaña **Settings** (es la última pestaña en la barra del repositorio).

3. En el menú lateral izquierdo, buscá **Secrets and variables** y hacé clic. Después hacé clic en **Actions**.

4. Hacé clic en el botón **New repository secret**.

5. Creá el primer secret:
   - **Name:** `CLOCKIFY_API_KEY`
   - **Secret:** Pegá tu API Key de Clockify (la del Paso 2)
   - Hacé clic en **Add secret**

6. Hacé clic de nuevo en **New repository secret** y creá el segundo:
   - **Name:** `CLOCKIFY_WORKSPACE_ID`
   - **Secret:** Pegá tu Workspace ID (el del Paso 3). Si no lo tenés, podés omitir este secret.
   - Hacé clic en **Add secret**

> ✅ **¿Cómo sé que funcionó?** Vas a ver los dos secrets listados en la página. No se muestra su contenido — solo el nombre y la fecha de creación. Eso es correcto.

---

## Paso 6 — Activar tu página web

> **¿Qué es GitHub Pages?** Es un servicio gratuito de GitHub que convierte los archivos de tu repositorio en una página web accesible desde cualquier navegador.

### Pasos:

1. En tu repositorio, andá a **Settings** → buscá **Pages** en el menú lateral izquierdo (está en la sección *Code and automation*).

2. En la sección **Build and deployment**, bajo **Source**, asegurate de que esté seleccionada la opción **Deploy from a branch**.

3. En el selector de **Branch**, elegí **`main`**. En el selector de carpeta que aparece al lado, elegí **`/docs`**.

4. Hacé clic en **Save**.

5. Esperá unos segundos y recargá la página. Arriba de todo vas a ver un mensaje con la URL de tu página, con el formato:

   ```
   https://TU-USUARIO.github.io/clockify_manager/
   ```

6. **Guardá esa URL** — es la dirección de tu página web para cargar horas.

> 💡 **Consejo:** La primera vez puede tardar hasta 1–2 minutos en aparecer. Si el mensaje no aparece, recargá la página después de un momento.

---

## Paso 7 — Configurar la página web por primera vez

La primera vez que abrís tu página web, tenés que ingresar tus credenciales. Se guardan **solo en tu navegador** — nunca se suben a ningún servidor.

### Pasos:

1. Abrí la URL de tu página (`https://TU-USUARIO.github.io/clockify_manager/`).

2. Hacé clic en el botón **Configuración** en la esquina superior derecha (tiene un ícono de engranaje ⚙).

3. Se abre un panel. Completá los cuatro campos:

   | Campo | Qué poner |
   |---|---|
   | **GitHub Personal Access Token** | El token que copiaste en el Paso 4 (empieza con `ghp_`) |
   | **Repositorio GitHub** | Tu usuario y nombre del repo, así: `TU-USUARIO/clockify_manager` |
   | **Clockify API Key** | Tu API Key de Clockify (la del Paso 2) |
   | **Workspace ID** | Tu Workspace ID (el del Paso 3). Podés dejarlo vacío si no lo tenés. |

4. Hacé clic en **Guardar**.

> ✅ **¡Listo!** La configuración inicial está completa. No necesitás repetir estos pasos en la misma computadora. Si usás otra computadora o borrás los datos del navegador, tendrás que configurarlo de nuevo.

---

## Cómo usar la página web día a día

Una vez configurada, el uso habitual es muy simple:

### 1. Seleccioná los días trabajados

- El calendario muestra el mes actual.
- Hacé clic en cada día que trabajaste para seleccionarlo (se pone azul).
- Los sábados y domingos no se pueden seleccionar.
- Usá las flechas **‹ ›** para cambiar de mes.
- El botón **Mes completo** selecciona todos los días hábiles del mes de un solo clic.
- El botón **Limpiar selección** deselecciona todo.

Los feriados nacionales aparecen listados debajo del calendario como referencia.

### 2. Agregá los proyectos en los que trabajaste

1. Hacé clic en **+ Agregar proyecto**.
2. En la tarjeta que aparece, seleccioná el **proyecto** del menú desplegable.
3. Si el proyecto tiene más de un cliente, elegí el **cliente** correspondiente.
4. Elegí la **etiqueta** (tipo de trabajo): *Gestión de Ingeniería*, *Ejecución de Ingeniería*, etc.
5. Ajustá la **ponderación** (los botones del 1 al 8): indica qué tanto tiempo le dedicaste a ese proyecto respecto a los demás. Un 8 significa que le dedicaste el máximo, un 1 el mínimo. La herramienta calcula el porcentaje automáticamente.

   > 💡 **Ejemplo:** Si trabajaste igual en dos proyectos, ponés 4 en ambos → 50% cada uno. Si a uno le dedicaste el doble, ponés 8 y 4 respectivamente → 67% y 33%.

6. Repetí para cada proyecto adicional.

Si preferís ingresar los porcentajes manualmente, hacé clic en **Porcentual** en el selector de modo. El último proyecto calcula automáticamente su porcentaje para que la suma dé siempre 100%.

### 3. (Opcional) Horas extra después de las 18:00

Si trabajaste horas extra más allá de tu horario habitual:

1. Hacé clic en **+ Agregar horas extra** (en la sección "Horas Extra", con ícono ⚡).
2. Seleccioná el proyecto al que corresponden esas horas.
3. En el campo **Hs extra**, indicá cuántas horas extra trabajaste **por día** (máximo 4 por día, de 18:00 a 22:00).
4. Podés agregar varios bloques de horas extra para diferentes proyectos.

### 4. Generá la distribución

Hacé clic en el botón **Generar distribución**.

La parte inferior de la pantalla muestra una grilla con la distribución de horas por día. Cada proyecto tiene un color diferente. Revisá que todo se vea correcto.

### 5. Cargá las horas en Clockify

1. Hacé clic en **Cargar a Clockify**.

2. La herramienta verifica automáticamente si ya existen entradas en Clockify para esos días:
   - Si hay un **conflicto** (ya hay horas cargadas para ese horario), te pregunta si querés saltear esas entradas o sobreescribirlas.
   - Si estás cargando **horas extra**, verifica que esos días ya tengan las 8 horas regulares cargadas en Clockify. Si no las tienen, te avisa antes de continuar.

3. El proceso tarda 1–2 minutos. Podés seguir el progreso en GitHub yendo a la pestaña **Actions** de tu repositorio.

> ✅ **¿Cómo sé que funcionó?** El workflow termina con un ícono verde ✅. Si hay un error, aparece un ícono rojo ❌ — en ese caso, hacé clic en el workflow para ver el detalle del error.

---

## Cómo actualizar la lista de proyectos

La página web obtiene la lista de proyectos desde Clockify a través de un archivo Excel. Cuando se agregan o modifican proyectos en Clockify, hay que actualizar ese archivo.

### Paso A — Exportar los proyectos desde Clockify

1. En Clockify, hacé clic en **Projects** en el menú lateral izquierdo.

2. En la pantalla de proyectos, buscá el ícono de exportación (generalmente arriba a la derecha, parece una flecha hacia abajo o un ícono de descarga).

3. Hacé clic en **Export as Excel** (o "Exportar como Excel").

4. Se descarga un archivo `.xlsx` a tu computadora.

### Paso B — Subir el archivo a GitHub

1. Andá a tu repositorio en GitHub.

2. Hacé clic en el botón **Add file** → **Upload files**.

3. Arrastrá el archivo descargado al área de carga, **o** hacé clic en *choose your files* para buscarlo en tu computadora.

4. **Importante:** Antes de subir, renombrá el archivo a exactamente **`projects.xlsx`** (en minúsculas, sin espacios). Si el archivo tiene otro nombre, el proceso automático no se activa.

   > 💡 **¿Cómo renombrar?** En Windows: clic derecho sobre el archivo → Cambiar nombre. En Mac: doble clic sobre el nombre del archivo.

5. Una vez cargado, bajá y hacé clic en **Commit changes** → **Commit directly to the `main` branch** → **Commit changes**.

6. GitHub ejecuta automáticamente un proceso que convierte el Excel a un formato que entiende la página web. Tarda 1–2 minutos.

7. La próxima vez que abrás la página web, la lista de proyectos ya va a estar actualizada.

> ⚠️ **El nombre del archivo debe ser exactamente `projects.xlsx`**, con esa ortografía y sin espacios. Si lo subís con otro nombre, tendrás que borrarlo y repetir el proceso.

---

## Preguntas frecuentes

**¿Mis contraseñas y claves están seguras?**

Sí. Las claves que ingresás en la configuración de la página web se guardan solo en tu navegador (en lo que se llama "almacenamiento local") y nunca se suben a ningún servidor. Los secrets que guardás en GitHub están cifrados y ni siquiera GitHub los puede leer.

**¿El proceso de carga puede crear entradas duplicadas?**

No, porque la herramienta verifica automáticamente si ya hay entradas para esos horarios antes de cargar. Si detecta una superposición, te pregunta qué hacer.

**¿Qué pasa si el workflow falla?**

Podés ver el detalle del error en la pestaña **Actions** de tu repositorio. Hacé clic en el workflow que falló (tiene un ícono ❌) → hacé clic en el paso que falló para ver el mensaje de error.

**Mi token de GitHub venció. ¿Qué hago?**

Repetí el Paso 4 para generar un nuevo token, y luego actualizalo en la configuración de la página web (ícono de engranaje ⚙ → campo *GitHub Personal Access Token*).

**¿Puedo usar la herramienta desde cualquier computadora?**

Sí, la página web funciona desde cualquier navegador. Pero la configuración (token, API Key, etc.) se guarda solo en el navegador donde la cargaste. En una computadora nueva, tendrás que ingresar los datos de configuración de nuevo (Paso 7).

**Los proyectos que aparecen en la lista no son los correctos.**

Actualizá el archivo `projects.xlsx` siguiendo los pasos de la sección [Cómo actualizar la lista de proyectos](#cómo-actualizar-la-lista-de-proyectos).

---

## Uso avanzado

Esta sección es para usuarios con conocimientos técnicos que quieran usar funciones adicionales.

### Disparar la carga manualmente desde GitHub

Podés iniciar el proceso de carga directamente desde GitHub sin usar la página web:

1. Andá a la pestaña **Actions** de tu repositorio.
2. En el menú lateral izquierdo, hacé clic en **Log Hours to Clockify**.
3. Hacé clic en **Run workflow**.

Podés elegir entre tres modos:

**Modo `batch` — Múltiples entradas desde archivo**

Creá un archivo llamado `entries.yml` en la raíz de tu repositorio con este formato:

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

Luego corré el workflow con **Mode = `batch`**.

**Modo `single` — Una sola entrada**

| Campo | Ejemplo |
|---|---|
| Mode | `single` |
| Date | `2026-05-09` |
| Start time | `09:00` |
| End time | `18:00` |
| Description | `Desarrollo` |
| Project | `BESS AMBA` |
| Billable | `true` |

**Modo `weekly` — Carga semanal recurrente**

Usa el archivo `weekly_schedule.yml` para definir un horario fijo que se repite semana a semana. Útil para automatizar la carga con un schedule programado.

```yaml
timezone: "America/Argentina/Buenos_Aires"

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

# Semanas con variaciones
weeks:
  "2026-05-11":
    wednesday: []   # día libre esa semana
```

> 💡 Probá siempre con **Dry run = `true`** primero para previsualizar sin crear entradas reales.

### Ejecución local con Python

Si preferís ejecutar el script desde tu propia computadora:

```bash
pip install requests pyyaml tzdata

export CLOCKIFY_API_KEY=tu_api_key
export CLOCKIFY_WORKSPACE_ID=tu_workspace_id

# Previsualizar
python scripts/log_hours.py batch --file entries.yml --dry-run

# Cargar
python scripts/log_hours.py batch --file entries.yml
```
