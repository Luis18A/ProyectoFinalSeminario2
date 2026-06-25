# Guía de Librerías y Dependencias del Proyecto

Este archivo detalla y explica todas las librerías de Python especificadas en el archivo `requirements.txt` que son utilizadas en este proyecto.

---

## 📦 Lista de Dependencias (`requirements.txt`)

Para instalar todas las librerías a la vez al cambiar de entorno, ejecuta el siguiente comando en tu terminal (asegúrate de tener tu entorno virtual activo):

```bash
pip install -r requirements.txt
```

---

## 🔍 Descripción y Uso de Cada Librería

### 1. **Flask (v3.0.0)**
* **Definición:** Un framework web de Python ligero, modular y fácil de usar (microframework).
* **Uso en el proyecto:** Es el núcleo del servidor web. Se encarga de recibir las peticiones HTTP del navegador, manejar las rutas principales (rutas de vistas y lógica de negocio), administrar las sesiones de los usuarios y renderizar las plantillas HTML (Jinja2).

### 2. **Flask-SQLAlchemy**
* **Definición:** Una extensión para Flask que facilita la integración con **SQLAlchemy**, el ORM (Object-Relational Mapper) líder en Python.
* **Uso en el proyecto:** Permite interactuar con la base de datos PostgreSQL utilizando clases de Python (Modelos) en lugar de escribir consultas SQL a mano. Por ejemplo, define tablas como `Usuario`, `Cliente` u `OrdenServicio` como objetos y permite hacer búsquedas con métodos como `.query.filter_by(...)`.

### 3. **psycopg2-binary**
* **Definición:** El adaptador oficial y más popular de base de datos PostgreSQL para el lenguaje de programación Python.
* **Uso en el proyecto:** Es el "traductor" de bajo nivel. Permite que SQLAlchemy y Flask se conecten y envíen comandos directamente al motor de base de datos de PostgreSQL en tu máquina local o servidor.

### 4. **Flask-WTF**
* **Definición:** Una extensión de Flask que integra **WTForms**, ofreciendo herramientas para el manejo seguro de formularios web y mecanismos de protección contra ataques.
* **Uso en el proyecto:** Proporciona la funcionalidad de **CSRFProtect** (seguridad contra Falsificación de Petición en Sitios Cruzados) que valida automáticamente los formularios que envían datos (`POST`, `PUT`, etc.) asegurando que provengan del frontend legítimo de tu aplicación.

### 5. **FastAPI**
* **Definición:** Un framework web moderno, sumamente rápido (de alto rendimiento) y asíncrono para construir APIs con Python basado en anotaciones de tipo estándar.
* **Uso en el proyecto:** Se utiliza en la arquitectura del backend para levantar endpoints API rápidos, modulares o asíncronos que corren paralelamente a la aplicación Flask o para tareas específicas de extracción de datos.

### 6. **Uvicorn**
* **Definición:** Un servidor web ASGI (Asynchronous Server Gateway Interface) ultrarrápido para Python.
* **Uso en el proyecto:** Es el servidor encargado de ejecutar y servir la aplicación de **FastAPI**, dado que FastAPI al ser asíncrona no puede correr sobre servidores WSGI tradicionales.

### 7. **Scrapling**
* **Definición:** Una librería moderna y optimizada para web scraping (extracción de datos web) diseñada para ser extremadamente veloz y eludir sistemas de protección contra bots.
* **Uso en el proyecto:** Utilizada en la carpeta de scrapeadores (`scrappers/`) para extraer información automatizada de sitios externos.

### 8. **Playwright**
* **Definición:** Una librería desarrollada por Microsoft para la automatización e instrumentación de navegadores web (Chromium, Firefox y WebKit) mediante una API única.
* **Uso en el proyecto:** Se utiliza para realizar web scraping dinámico de páginas que cargan su contenido con JavaScript, simulando las acciones de un usuario real (dar clics, hacer scroll, rellenar formularios).

### 9. **Patchright**
* **Definición:** Una bifurcación/modificación de Playwright diseñada específicamente para evadir protecciones anti-bot de manera más efectiva, emulando comportamientos más humanos en el navegador.
* **Uso en el proyecto:** Complemento de Playwright en tareas de extracción de datos donde los sitios web tienen bloqueos estrictos.

### 10. **Curl_cffi**
* **Definición:** Una librería que permite realizar peticiones HTTP emulando de manera exacta los detalles de red y firmas (como JA3/TLS fingerprints) de navegadores reales (Chrome, Safari, Firefox).
* **Uso en el proyecto:** Permite hacer peticiones automatizadas de web scraping sin levantar un navegador pesado, pero evitando que el servidor de destino bloquee la petición por identificarla como un script de Python.

### 11. **Browserforge**
* **Definición:** Una biblioteca especializada en la generación y gestión de perfiles de navegador realistas (User-Agent, tamaño de pantalla, cabeceras HTTP específicas, etc.).
* **Uso en el proyecto:** Modifica los encabezados de los navegadores automatizados en el módulo de scraping para alternar identidades de navegador (evitando bloqueos por exceso de peticiones con el mismo identificador).
