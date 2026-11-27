# Cristobal-Colon-Galactico
# Nombre del Proyecto

    "Cristobal Colón Galáctico" es una API REST para gestionar misiones espaciales destinadas a la exploración y descubrimiento de nuevos exoplanetas

## Características principales
* CRUD de usuarios
    Permite crear, consultar, actualizar y borrar registros de usuarios
* Asignar una misión
    Se crea una misión con unas fechas determinadas y se asignan tanto la nave como la tripulaciín de manera aleatoria teneinedo en cuenta el tamaño de la nave y las fechas de la misión
* Finalizar una misión
    Permite cerrar una misión indicando si ha tenido éxito o ha fracasado y registrando los exoplanetas descubiertos en caso de éxito
* Consultar los tripulantes de una misión
    Dada una misión conocida, se obtiene los tripulantes que han participado y sus habilidades

* Consultar los planetas descubiertos por un capitán
    Permite consultar todos los exoplanetas descubiertos en las misiones en las que ha participado un capitán concreto

## Tecnologías utilizadas
* Lenguaje / Framework principal (ej. Python, React, Node.js)
* Base de datos / Herramientas adicionales

## Requisitos previos
Asegúrate de tener instalado lo siguiente antes de empezar:
* [Nombre de herramienta o lenguaje] (versión X.X o superior)

## Instalación y ejecución

Sigue estos pasos para poner en funcionamiento la API en tu entorno local:

### 1. Requisitos previos
* Python 3.10 o superior
* Git

### 2. Clonar el repositorio
```bash
git clone https://github.com/igarciacob/Cristobal-Colon-Galactico.git
cd tu-repositorio
```

### 3. Crear y activar el entorno virtual
* **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```
* **En Windows:**
  ```bash
  python -m venv .venv
  .venv\Scripts\activate
  ```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno *(si aplica)*
Si tu proyecto utiliza un archivo `.env`, créalo en la raíz con las variables necesarias:
```env
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
```

### 6. Crear la base de datos y aplicar migraciones
Este comando generará automáticamente el archivo `db.sqlite3` con las tablas necesarias:
```bash
python manage.py migrate
```

### 7. Poblar datos de prueba *(opcional)*
Para generar datos iniciales (capitanes, tripulantes, naves, misiones y exoplanetas):
```bash
python manage.py factoria
```

### 8. *(Opcional)* Crear un superusuario
Para acceder al panel de administración de Django (`/admin`):
```bash
python manage.py createsuperuser
```

### 9. Ejecutar el servidor
```bash
python manage.py runserver
```

La API estará disponible en `http://127.0.0`.

## Documentación de la API

La URL base para todas las peticiones en entorno local es: `http://127.0.0` (o con el prefijo `/api/` según la configuración de `urls.py`).

### Validaciones y respuestas de error
Las validaciones de datos comprueban los campos de entrada y acumulan los fallos encontrados para devolverlos en una lista `"errores"` con código `400` cuando hay varios errores de validación a la vez, facilitando corregirlos de una pasada.

### Endpoints disponibles

#### Usuarios

| Método | Endpoint | Descripción | Parámetros de ruta |
| :--- | :--- | :--- | :--- |
| `POST` | `/crearusuario/` | Crea un nuevo usuario | — |
| `GET` | `/consultarusuario/{id}/` | Obtiene los datos de un usuario específico | `id` (entero) |
| `PUT` / `PATCH` | `/usuarios/{id}/modificar/` | Actualiza la información de un usuario existente | `id` (entero) |
| `DELETE` | `/usuarios/{id}/eliminar/` | Elimina un usuario del sistema | `id` (entero) |

#### Misiones, Tripulación y Exoplanetas

| Método | Endpoint | Descripción | Parámetros de ruta |
| :--- | :--- | :--- | :--- |
| `POST` | `/asignarmision/` | Asigna una misión a un usuario o tripulación | — |
| `GET` | `/consultartripulacion/{id}/` | Consulta los detalles de una tripulación específica | `id` (entero) |
| `POST` | `/finalizarmision/{id}/` | Finaliza una misión indicando éxito o fracaso y registra exoplanetas si hubo éxito | `id` (entero) |
| `GET` | `/consultarplanetascapitan/{id}/` | Consulta los exoplanetas descubiertos en las misiones de un capitán | `id` (entero) |

---

### Ejemplos de peticiones y respuestas

#### 1. Crear un usuario (`POST /crearusuario/`)

**Cuerpo de la petición (JSON):**
```json
{
	"nombre": "Vasco",
    "apellidos": "Nuñez de Balboa",
    "tipo":"capitan",
    "habilidad":[
    "Mantenimiento","Resolucion conflictos"
  ]
}
```

**Respuesta exitosa (`201`):**
```json
{
    "exito": "Usuario creado correctamente",
    "id": 81
}
```

#### 2. Consultar un usuario (`GET /consultarusuario/1/`)

**Respuesta exitosa (`200`):**
```json
{
    "nombre": "Joaquina",
    "apellidos": "Pastor",
    "tipo": "tripulante"
}
```

#### 3. Asignar una misión (`POST /asignarmision/`)

**Cuerpo de la petición (JSON):**
```json
{
	"nombre" : "Exploración espacial",
    "fecha_inicio" : "2026-11-26",
    "fecha_fin" : "2026-12-15",
    "exito" : false
}
```

**Respuesta exitosa (`201 Created`):**
```json
{
    "exito": "Misión creada correctamente",
    "id": 7
}
```

#### 4. Finalizar una misión (`POST /finalizarmision/1/`)

**Cuerpo de la petición (JSON):**
```json
{
    "exito": true,
    "fecha_fin": "2026-11-27",
    "exoplanetas": ["Kepler-452b", "Gliese 667 Cc"]
}
```

**Respuesta exitosa (`200`):**
```json
{
    "exito": "Misión finalizada correctamente",
    "id": 1,
    "resultado": true,
    "fecha_fin": "2026-11-27",
    "exoplanetas": [
        {
            "id": 1,
            "nombre": "Kepler-452b"
        },
        {
            "id": 2,
            "nombre": "Gliese 667 Cc"
        }
    ]
}
```

#### 5. Consultar los planetas descubiertos por un capitán (`GET /consultarplanetascapitan/1/`)

**Respuesta exitosa (`200`):**
```json
{
    "capitan_id": 1,
    "nombre": "Vasco",
    "apellidos": "Nuñez de Balboa",
    "exoplanetas": [
        {
            "id": 1,
            "nombre": "Kepler-452b",
            "mision_id": 1,
            "mision_nombre": "Exploración espacial"
        }
    ]
}
```

## Pruebas

El proyecto incluye pruebas automatizadas para verificar el correcto funcionamiento de los endpoints y la lógica de negocio.

### Casos cubiertos
* **Gestión de usuarios:** Creación de usuarios

* **Misiones y tripulación:** 

### Cómo ejecutar las pruebas

Asegúrate de tener el entorno virtual activado y ejecuta el siguiente comando desde la raíz del proyecto:

```bash
python manage.py test
```