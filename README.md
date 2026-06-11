# <img src="static/logo_lionheart.png" Style="width: 40px; transform: translateY(10px);" alt="Logo Lionheart"> IES Lionheart — Panel Estadístico Educativo

Aplicación web desarrollada con Python y Flask para consultar y analizar estadísticas educativas de un centro docente a partir de ficheros CSV anonimizados.

Proyecto de fin de Máster · Desarrollo de Aplicaciones en Lenguaje Python  
**Autor:** Marcos Encarnación Martínez · IES Leonardo Da Vinci · Curso 2025–2026

---

## 📋 Descripción

IES Lionheart permite al centro docente analizar de forma visual e interactiva:

- Rendimiento académico por materia y por grupo
- Absentismo por grupo, materia y evolución mensual
- Alumnado en situación de riesgo académico
- Evolución del rendimiento entre evaluaciones

Todos los datos son anonimizados. No se almacenan ni muestran datos personales — el único identificador utilizado es la **MATRÍCULA**, un código interno sin vinculación directa con el alumno.

---

## 🛠️ Tecnologías utilizadas

- **Python 3** — Lenguaje principal
- **Flask** — Framework web
- **Jinja2** — Motor de plantillas utilizadas en Flask
- **pandas** — Carga, limpieza, análisis de CSV y exportación de tablas
- **matplotlib** — Generación de gráficas
- **SQLAlchemy + pymysql** — Conexión con MySQL Workbench
- **openpyxl** — Exportación a Excel
- **HTML / CSS / JavaScript** — Interfaz visual personalizada

---

## 📁 Estructura del proyecto

---

```
proyecto_flask_estadisticas/
│
├── data/  # Ficheros CSV anonimizados
│   ├── datNotas.csv
│   ├── datMatriculas.csv
│   └── datFaltas.csv
│
├── static/
│   ├── css/
│   │   └── estilos.css
│   ├── js/
│   │   ├── graficas.js
│   │   └── utils.js
│   └── logo_lionheart.png
│
├── templates/
│   ├── absentismo.html
│   ├── acerca.html
│   ├── base_login.html
│   ├── base.html
│   ├── grupos.html
│   ├── index.html
│   ├── login.html
│   ├── materias.html
│   └── riesgo.html
│
├── utils/
│   ├── obtener_datos.py # Funciones de carga y cálculo con pandas
│   ├── obtener_tablas.py # Generación de tablas HTML con Styler
│   └── obtener_graficas_plt.py # Generación de gráficas con matplotlib
│
├── app_service/
│    └── data_loader.py  # Orquestación de datos, │exportación y MySQL
│
├── .env.example # Variable de entorno que rellenar con tus credenciales
├── .gitignore
├── app.py  # Rutas Flask y lógica principal
├── check.py  # Algunas comprobaciones
├── LICENSE
├── README.md
└── requirements.txt  # Dependencias del proyecto
```

---

## ⚙️ Instalación y ejecución

### 1. Copia / clona o descomprime el proyecto

```bash
cd proyecto_flask_estadisticas
```

### 2. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 3. Coloca los CSV en la carpeta `data/`

Asegúrate de que los ficheros CSV anonimizados están en la carpeta `data/`:
- `datNotas.csv`
- `datMatriculas.csv`
- `datFaltas.csv`
- Nota: `datUnidades.csv` y `materias_centro.csv`, aunque se incluyan en los archivos dados originales, luego de procesarlos y hacer pruebas, se llegó a la conclusión de que `NO` tienen un uso práctico.

### 4. (Opcional) Configura MySQL Workbench

Si quieres usar la función de guardado en MySQL, crea una base de datos llamada `lionheart`, o una propia cambiando los datos necesarios, en MySQL Workbench y copia el `.env.example` a `.env`, rellenando el enlace con tus credenciales:

```python
DATABASE_URL = "mysql+pymysql://root:TU_CONTRASEÑA@localhost/TU_BASE_DE_DATOS"
```

### 5. Ejecuta la aplicación

```bash
python app.py
```

Abre el navegador en `http://localhost:5000`

---

## 🔐 Credenciales de acceso

| Usuario  | Contraseña   | Rol     |
|----------|--------------|---------|
| admin    | Admin$1234   | Admin   |
| usuario  | User$1234    | Usuario |

El rol **Admin** permite, además, guardar tablas en MySQL Workbench.

---

## 📦 Exportación de datos

Desde cada sección se pueden exportar las tablas filtradas en:
- CSV
- Excel (.xlsx)
- JSON
- SQLite (.db)

Recordatorio: Los administradores pueden, además, guardar directamente en MySQL Workbench con el botón que aparecerá al lado del de `⬇ Descargar tabla`.

---

## 📊 Páginas disponibles

| Ruta | Descripción |
|------|-------------|
| `/` | Dashboard general con resumen del centro |
| `/materias` | Rendimiento por materia con filtros y gráficas |
| `/grupos` | Rendimiento por grupo y peores materias |
| `/absentismo` | Análisis de ausencias y retrasos |
| `/riesgo` | Alumnado en situación de riesgo académico |
| `/acerca` | Información del proyecto y tecnologías |

## 📸 Capturas de las páginas

### Login
![Dashboard](static/capturas/login.png)

### Dashboard general
![Dashboard](static/capturas/dashboard.png)

### Rendimiento por materia
![Materias](static/capturas/materias.png)

### Rendimiento por grupo
![Grupos](static/capturas/grupos.png)

### Absentismo
![Absentismo](static/capturas/absentismo.png)

### Alumnado en riesgo
![Riesgo](static/capturas/riesgo.png)

### Acerca
![Dashboard](static/capturas/acerca.png)