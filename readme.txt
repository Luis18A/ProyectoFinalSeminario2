================================================================================
                    TECHFLOW — SISTEMA DE GESTIÓN TÉCNICA
                         Y AUTOMATIZACIÓN DE COMPONENTES
================================================================================
                     DOCUMENTACIÓN DE ARQUITECTURA Y DISEÑO
             Para Presentación Académica / Auditoría de Sistemas
================================================================================

Este documento constituye la especificación técnica formal y de arquitectura de
TechFlow, una plataforma empresarial para la administración del flujo de trabajo 
de reparaciones, gestión de órdenes de servicio y adquisición optimizada de 
componentes y repuestos a través de agentes de web scraping concurrentes y 
sistemas avanzados de evasión anti-bot.

--------------------------------------------------------------------------------
1. RESUMEN EJECUTIVO Y OBJETIVOS DEL SISTEMA
--------------------------------------------------------------------------------
El sistema TechFlow aborda la problemática de la gestión ineficiente y la falta 
de trazabilidad en los talleres de soporte técnico de hardware. Su arquitectura 
permite un control riguroso del ciclo de vida de los dispositivos ingresados, 
garantizando la integridad transaccional del flujo de estados (máquina de 
estados finitos) y optimizando el aprovisionamiento de repuestos. A través de 
un microservicio asíncrono acoplado, el sistema consolida en tiempo real 
precios y disponibilidad de repuestos desde múltiples plataformas de comercio 
electrónico y proveedores mayoristas, evadiendo medidas restrictivas de 
bloqueo mediante fingerprinting y emulación dinámica a nivel de red y hardware.

--------------------------------------------------------------------------------
2. ARQUITECTURA LOGICA Y COMPONENTES DEL SISTEMA
--------------------------------------------------------------------------------
TechFlow implementa una arquitectura híbrida desacoplada que combina un servidor 
monolítico modular basado en el patrón Modelo-Vista-Controlador (MVC) utilizando 
Flask, y un microservicio asíncrono de alto rendimiento implementado con FastAPI.

+------------------------------------------------------------------------------+
|                                ARQUITECTURA                                  |
+------------------------------------------------------------------------------+
|                                                                              |
|  +------------------------------------------------------------------------+  |
|  |                           CAPA DE PRESENTACIÓN                         |  |
|  |    - Layouts Modulares en HTML5/CSS3 (Templates Jinja2)                |  |
|  |    - Interacciones Asíncronas (Búsquedas Globales y Analíticas)        |  |
|  +-----------------------------------+------------------------------------+  |
|                                      | (HTTPS / Formularios Secure JWT)      |
|                                      v                                       |
|  +------------------------------------------------------------------------+  |
|  |                        CAPA DE APLICACIÓN (Flask)                      |  |
|  |  - Enrutamiento Modular (Blueprints)                                   |  |
|  |  - Controladores Segregados (Lógica de Dominio y Flujo)                |  |
|  |  - Filtros y Seguridad de Sesión (Decoradores de Autorización RBAC)   |  |
|  +-----------------------------------+------------------------------------+  |
|                                      |                                       |
|                    +-----------------+-----------------+                     |
|                    | (SQLAlchemy ORM)                  | (HTTP Async Call)   |
|                    v                                   v                     |
|  +----------------------------------+  +----------------------------------+  |
|  |       PERSISTENCIA RELACIONAL    |  |      MICROSERVICIO FASTAPI       |  |
|  |  - PostgreSQL (Motor de BD)      |  |  - Servidor ASGI (Uvicorn)       |  |
|  |  - Modelos ORM Autoestructurados  |  |  - Ejecución Concurrente         |  |
|  |  - Transacciones e Historiales   |  |  - Motores de Scraping Dinámico |  |
|  +----------------------------------+  +----------------------------------+  |
|                                                        |                     |
|                                                        v                     |
|                                        +----------------------------------+  |
|                                        |  AGENTES DE EVASIÓN ANTI-BOT     |  |
|                                        |  - StealthyFetcher (Camoufox)    |  |
|                                        |  - TLS JA3 Fingerprinting        |  |
|                                        |  - Rotación de Browserforge      |  |
|                                        +----------------------------------+  |
+------------------------------------------------------------------------------+

A continuación se detalla la segregación de responsabilidades de los componentes:

+-------------------+----------------------------+-----------------------------+
| Componente        | Implementación / Tecnologías| Responsabilidad Técnica     |
+-------------------+----------------------------+-----------------------------+
| Capa de           | - HTML5 Semántico y CSS3   | - Renderización de layouts  |
| Presentación      | - Jinja2 Templates         |   modulares del sistema.     |
| (Frontend)        | - Vanilla Javascript       | - Consumo de endpoints y    |
|                   |                            |   visualización dinámica de |
|                   |                            |   analíticas en tiempo real.|
+-------------------+----------------------------+-----------------------------+
| Servidor Core     | - Flask Framework          | - Orquestación de rutas,    |
| (Backend)         | - Blueprints Organizados   |   procesamiento de peticiones|
|                   | - Controladores Dedicados  |   e inyección de seguridad  |
|                   |                            |   a través de decoradores.  |
+-------------------+----------------------------+-----------------------------+
| Motor de          | - SQLAlchemy ORM           | - Mapeo de objetos a tablas |
| Persistencia      | - PostgreSQL Database      |   relacionales, aislamiento |
|                   | - SQLite (para desarrollo) |   de queries y transacciones.|
+-------------------+----------------------------+-----------------------------+
| Microservicio     | - FastAPI                  | - Servicio asíncrono de     |
| de API            | - Uvicorn ASGI             |   consulta paralela para la |
|                   | - Asyncio Core             |   extracción de repuestos.  |
+-------------------+----------------------------+-----------------------------+
| Agentes de        | - Scrapling / Playwright   | - Extracción dinámica de    |
| Scraping          | - StealthyFetcher /        |   catálogos evadiendo       |
|                   |   Camoufox / curl_cffi     |   sistemas de firewall y    |
|                   | - Browserforge             |   sistemas de captcha.      |
+-------------------+----------------------------+-----------------------------+

--------------------------------------------------------------------------------
3. ESQUEMA DE BASE DE DATOS Y PERSISTENCIA RELACIONAL
--------------------------------------------------------------------------------
La capa de datos está diseñada bajo la tercera forma normal (3FN) con relaciones 
estrictas de clave foránea, borrados lógicos y control de tipos mediante enums. 
La base de datos PostgreSQL mapea las siguientes entidades críticas:

+------------------------------------------------------------------------------+
|                        DICCIONARIO DE DATOS DETALLADO                        |
+------------------------------------------------------------------------------+

A) Tabla: "usuario"
Mapea las credenciales e información de los operadores de la plataforma.
+-------------------+--------------------+------------------+------------------+
| Atributo          | Tipo/Implementación| Restricciones    | Descripción      |
+-------------------+--------------------+------------------+------------------+
| id                | INTEGER            | PK, Auto-increment| Identificador    |
|                   |                    |                  | único de usuario |
+-------------------+--------------------+------------------+------------------+
| username          | VARCHAR(80)        | Unique, Nullable=F| Nombre de usuario|
|                   |                    |                  | en minúsculas    |
+-------------------+--------------------+------------------+------------------+
| password          | VARCHAR(255)       | Nullable=F       | Hash bcrypt/pbkdf|
|                   |                    |                  | de seguridad     |
+-------------------+--------------------+------------------+------------------+
| nombre            | VARCHAR(80)        | Nullable=F       | Nombre real      |
+-------------------+--------------------+------------------+------------------+
| apellido          | VARCHAR(80)        | Nullable=F       | Apellido real    |
+-------------------+--------------------+------------------+------------------+
| rol_id            | INTEGER            | FK (rol.id)      | Rol de seguridad |
+-------------------+--------------------+------------------+------------------+
| activo            | BOOLEAN            | Default=True     | Estado lógico    |
+-------------------+--------------------+------------------+------------------+
| intentos_fallidos | INTEGER            | Default=0        | Contador para    |
|                   |                    |                  | mitigación brute |
|                   |                    |                  | force            |
+-------------------+--------------------+------------------+------------------+

B) Tabla: "rol"
Define la jerarquía de roles para el control de acceso basado en roles (RBAC).
+-------------+--------------------+------------------+------------------------+
| Atributo    | Tipo/Implementación| Restricciones    | Descripción            |
+-------------+--------------------+------------------+------------------------+
| id          | INTEGER            | PK, Auto-increment| Identificador de rol   |
+-------------+--------------------+------------------+------------------------+
| descripcion | VARCHAR(50)        | Unique, Nullable=F| "Administrador",       |
|             |                    |                  | "Técnico", "Secretario"|
+-------------+--------------------+------------------+------------------------+

C) Tabla: "cliente"
Almacena la información de contacto y fiscal de los propietarios de equipos.
+----------------+--------------------+-------------------+--------------------+
| Atributo       | Tipo/Implementación| Restricciones     | Descripción        |
+----------------+--------------------+-------------------+--------------------+
| id             | INTEGER            | PK, Auto-increment | Identificador único|
+----------------+--------------------+-------------------+--------------------+
| dni_cuil       | VARCHAR(20)        | Unique, Nullable=F| Clave tributaria/DNI|
+----------------+--------------------+-------------------+--------------------+
| nombre         | VARCHAR(50)        | Nullable=F        | Nombre del cliente |
+----------------+--------------------+-------------------+--------------------+
| apellido       | VARCHAR(50)        | Nullable=F        | Apellido           |
+----------------+--------------------+-------------------+--------------------+
| telefono       | VARCHAR(20)        | Nullable=F        | Número telefónico  |
+----------------+--------------------+-------------------+--------------------+
| email          | VARCHAR(254)       | Unique, Nullable=T| Correo electrónico|
+----------------+--------------------+-------------------+--------------------+
| domicilio      | VARCHAR(150)       | Nullable=F        | Dirección física   |
+----------------+--------------------+-------------------+--------------------+
| localidad      | VARCHAR(100)       | Nullable=F        | Localidad / Ciudad |
+----------------+--------------------+-------------------+--------------------+
| fecha_registro | DATETIME           | Default=now()     | Marca temporal     |
+----------------+--------------------+-------------------+--------------------+

E) Tabla: "equipo"
Representa los dispositivos tecnológicos ingresados al laboratorio.
+---------------------+--------------------+------------------+----------------+
| Atributo            | Tipo/Implementación| Restricciones    | Descripción    |
+---------------------+--------------------+------------------+----------------+
| id                  | INTEGER            | PK, Auto-increment| Identificador  |
+---------------------+--------------------+------------------+----------------+
| marca               | VARCHAR(50)        | Nullable=F       | Marca del item |
+---------------------+--------------------+------------------+----------------+
| modelo              | VARCHAR(50)        | Nullable=F       | Modelo         |
+---------------------+--------------------+------------------+----------------+
| nro_serie           | VARCHAR(50)        | Unique, Nullable=F| Número de serie|
+---------------------+--------------------+------------------+----------------+
| tipo_dispositivo_id | INTEGER            | FK (tipo_disp.id)| Categoría      |
+---------------------+--------------------+------------------+----------------+
| cliente_id          | INTEGER            | FK (cliente.id)  | Propietario    |
+---------------------+--------------------+------------------+----------------+

F) Tabla: "orden_servicio"
La entidad transaccional central de TechFlow. Administra los costos, estados, 
presupuestos y repuestos cotizados para el dispositivo.
+--------------------+--------------------+------------------+-----------------+
| Atributo           | Tipo/Implementación| Restricciones    | Descripción     |
+--------------------+--------------------+------------------+-----------------+
| id                 | INTEGER            | PK, Auto-increment| Nro de orden    |
+--------------------+--------------------+------------------+-----------------+
| usuario_id         | INTEGER            | FK (usuario.id)  | Operador a cargo|
+--------------------+--------------------+------------------+-----------------+
| equipo_id          | INTEGER            | FK (equipo.id)   | Equipo reparado |
+--------------------+--------------------+------------------+-----------------+
| falla_reportada    | VARCHAR(500)       | Nullable=F       | Síntomas        |
+--------------------+--------------------+------------------+-----------------+
| accesorios         | VARCHAR(500)       | Nullable=F       | Componentes ext |
+--------------------+--------------------+------------------+-----------------+
| estado             | ENUM (EstadoOrden) | Nullable=F       | Pendiente, Listo|
|                    |                    |                  | Diagnóstico, etc|
+--------------------+--------------------+------------------+-----------------+
| estado_diagnostico | VARCHAR(255)       | Nullable=T       | Notas de técnico|
+--------------------+--------------------+------------------+-----------------+
| fecha_recepcion    | DATETIME           | Default=now()    | Fecha ingreso   |
+--------------------+--------------------+------------------+-----------------+
| fecha_entrega      | DATETIME           | Nullable=T       | Cierre de orden |
+--------------------+--------------------+------------------+-----------------+
| costo              | NUMERIC(10,2)      | Nullable=T       | Precio cobrado  |
+--------------------+--------------------+------------------+-----------------+
| observaciones      | VARCHAR(500)       | Nullable=T       | Comentarios final|
+--------------------+--------------------+------------------+-----------------+
| repuestos          | JSON (MutableList) | Nullable=T,      | Lista dinámica  |
|                    |                    | Default=[]       | de repuestos    |
+--------------------+--------------------+------------------+-----------------+

G) Tabla: "historial_estado"
Soporta la trazabilidad auditable de todas las mutaciones de estado de la orden.
+---------------------+--------------------+------------------+----------------+
| Atributo            | Tipo/Implementación| Restricciones    | Descripción    |
+---------------------+--------------------+------------------+----------------+
| id                  | INTEGER            | PK, Auto-increment| ID de log      |
+---------------------+--------------------+------------------+----------------+
| orden_id            | INTEGER            | FK (orden_ser.id)| Orden auditada |
+---------------------+--------------------+------------------+----------------+
| estado_anterior     | VARCHAR(50)        | Nullable=F       | Estado de origen|
+---------------------+--------------------+------------------+----------------+
| estado_nuevo        | VARCHAR(50)        | Nullable=F       | Estado de dest. |
+---------------------+--------------------+------------------+----------------+
| fecha_cambio        | DATETIME           | Default=now()    | Timestamp      |
+---------------------+--------------------+------------------+----------------+
| usuario_id          | INTEGER            | FK (usuario.id)  | Autor del cambio|
+---------------------+--------------------+------------------+----------------+
| observacion_tecnica | VARCHAR(255)       | Nullable=T       | Justificación  |
+---------------------+--------------------+------------------+----------------+

--------------------------------------------------------------------------------
4. MAQUINA DE ESTADOS Y LOGICA DE FLUJO DE TRABAJO (WORKFLOW)
--------------------------------------------------------------------------------
El núcleo transaccional del sistema se rige por una Máquina de Estados Finitos 
(FSM) estricta implementada en `EstadoOrden.py`. Esta máquina evita transiciones 
ilegítimas de negocio (por ejemplo, pasar un equipo de "Pendiente" a "Entregado" 
sin diagnóstico ni presupuesto previo), resguardando la coherencia operativa 
del taller y la integridad de los datos financieros.

A continuación se detalla la matriz de transiciones de estados permitidas:

+-------------------+----------------------------+-----------------------------+
| Estado Inicial    | Estados Destino Permitidos | Impacto y Regla de Negocio  |
+-------------------+----------------------------+-----------------------------+
| PENDIENTE         | - DIAGNOSTICO              | - Estado inicial por defecto|
|                   |                            |   al recibir un equipo.     |
+-------------------+----------------------------+-----------------------------+
| DIAGNOSTICO       | - PRESUPUESTADO            | - El técnico evalúa la      |
|                   |                            |   falla y asigna repuestos. |
+-------------------+----------------------------+-----------------------------+
| PRESUPUESTADO     | - REPARACION               | - El cliente aprueba e      |
|                   | - DIAGNOSTICO (Reevaluación)|  inicia la fase técnica.   |
|                   |                            | - Si se rechaza o hay cambio|
|                   |                            |   vuelve a diagnóstico.     |
+-------------------+----------------------------+-----------------------------+
| REPARACION        | - LISTO                    | - Se aplica la mano de obra|
|                   | - PRESUPUESTADO (Adicional)|  y repuestos comprados.     |
|                   |                            | - Si surgen extras, vuelve  |
|                   |                            |   a fase presupuestaria.    |
+-------------------+----------------------------+-----------------------------+
| LISTO             | - ENTREGADO                | - Equipo reparado y testeado|
|                   |                            |   en espera de retiro.      |
+-------------------+----------------------------+-----------------------------+
| ENTREGADO         | - (Ninguno - Estado Final) | - Registro de cobro final,  |
|                   |                            |   bloqueo de edición.       |
+-------------------+----------------------------+-----------------------------+

El método `preparar_cambio_estado` de la clase `OrdenServicio` valida de forma 
dinámica estas reglas a través del enum `EstadoOrden.es_transicion_valida()`. 
Si la transición solicitada no es legal, se lanza una excepción de negocio 
`ValueError` que el controlador intercepta para hacer rollback de la transacción 
y notificar al usuario, impidiendo la corrupción lógica del historial.

--------------------------------------------------------------------------------
5. MOTOR DE EXTRACCION DE DATOS ASINCRONO Y TECNICAS ANTI-BOT
--------------------------------------------------------------------------------
La búsqueda de repuestos y precios consolidada se realiza de manera totalmente 
concurrente a través de un módulo especializado de Web Scraping conectado a 
FastAPI (`apis/fastapi.py`).

Dada la naturaleza síncrona de los scrapes individuales debido al motor de 
navegador subyence, FastAPI implementa `asyncio.to_thread` para derivar cada 
tarea a hilos optimizados de forma asíncrona, y ejecuta un `asyncio.gather` para 
resolver de forma paralela las peticiones a todas las tiendas.

+------------------------------------------------------------------------------+
|                         MATRIZ DE AGENTES SCRAPERS                           |
+------------------------------------------------------------------------------+

+--------------+-----------------------+-------------------+-------------------+
| Proveedor    | Clase / Archivo       | Tecnología Base   | Estrategia de     |
|              |                       |                   | Evasión Anti-Bot  |
+--------------+-----------------------+-------------------+-------------------+
| MercadoLibre | MercadoLibreScraper   | - Scrapling CSS   | - StealthyFetcher |
|              |                       | - StealthyFetcher |   (Camoufox)      |
|              |                       |                   | - Fingerprinting  |
|              |                       |                   |   de Hardware     |
+--------------+-----------------------+-------------------+-------------------+
| Fravega      | FravegaScraper        | - DynamicFetcher  | - DynamicFetcher  |
|              |                       |                   |   c/ User-Agent   |
|              |                       |                   | - Red inactiva    |
|              |                       |                   |   (4000ms wait)   |
+--------------+-----------------------+-------------------+-------------------+
| Megatone     | MegatoneScraper       | - DynamicFetcher  | - Cabeceras de    |
|              |                       |                   |   browserforge    |
+--------------+-----------------------+-------------------+-------------------+
| InfoPartes   | InfoPartesScraper     | - StealthyFetcher | - TLS JA3 Bypass  |
|              |                       |                   | - Simulación de   |
|              |                       |                   |   red real        |
+--------------+-----------------------+-------------------+-------------------+
| FullStore    | FullstoreScraper      | - StealthyFetcher | - Fingerprinting  |
|              |                       |                   |   avanzado        |
+--------------+-----------------------+-------------------+-------------------+

Detalle Técnico de Evasión Antibot:
- StealthyFetcher (Bypass Avanzado): Emplea una integración especializada con 
  `Camoufox` y `patchright` para modificar firmas de variables Javascript del 
  navegador automatizado (navigator.webdriver, WebGL fingerprints, resoluciones,
  plataforma, codecs multimedia). Esto desactiva las heurísticas de firewalls 
  como Cloudflare, Akamai o PerimeterX.
- curl_cffi: En los scrapers estáticos rápidos, emula de manera binaria la firma 
  del protocolo criptográfico TLS (firma JA3) de un navegador Google Chrome v119,
  evitando que el backend deniegue la petición HTTP por discrepancias en la 
  negociación de cifrado (típica de librerías como urllib o requests).
- Browserforge: Genera cabeceras HTTP aleatorias pero coherentes y ordenadas, 
  evitando patrones sintácticos artificiales detectables por analizadores WAF.

--------------------------------------------------------------------------------
6. ANALISIS DE SEGURIDAD Y MITIGACIÓN DE VULNERABILIDADES (OWASP TOP 10)
--------------------------------------------------------------------------------
TechFlow implementa rigurosas defensas a nivel de infraestructura, framework y 
código fuente contra los vectores de ataque más comunes identificados por OWASP.

6.1 Autenticación
El sistema implementa autenticación basada en sesiones Flask con las siguientes 
características de seguridad integradas a nivel de servidor:

+----------------------+-----------------------------------------------------------------+-------------------------------+
| Mecanismo            | Implementación                                                  | Archivo                       |
+----------------------+-----------------------------------------------------------------+-------------------------------+
| Hash de contraseñas  | werkzeug.security.generate_password_hash() -- PBKDF2-SHA256     | backend/models/Usuario.py     |
+----------------------+-----------------------------------------------------------------+-------------------------------+
| Bloqueo por intentos | Cuenta bloqueada automáticamente tras 5 intentos fallidos       | backend/controller/           |
|                      | consecutivos de inicio de sesión.                               | auth_controller.py            |
+----------------------+-----------------------------------------------------------------+-------------------------------+
| Session fixation     | session.clear() antes de crear nueva sesión en cada login.      | backend/routes/vistas_route.py|
+----------------------+-----------------------------------------------------------------+-------------------------------+
| Cookie segura        | SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax'     | app.py                        |
+----------------------+-----------------------------------------------------------------+-------------------------------+
| SECRET_KEY           | Variable de entorno obligatoria y validada en producción.       | app.py / .env                 |
+----------------------+-----------------------------------------------------------------+-------------------------------+
| CSRF                 | Flask-WTF CSRFProtect activo globalmente.                       | app.py                        |
+----------------------+-----------------------------------------------------------------+-------------------------------+

6.2 Autorización — Control de Acceso por Roles
Todas las rutas protegidas utilizan los decoradores @login_required y 
@role_required definidos en backend/utils/decorators.py. La verificación de rol 
se realiza contra la sesión Flask (cuya integridad depende de la SECRET_KEY).

+-----------------+--------------------------------------------------------------------------------------------+
| Rol             | Permisos principales                                                                       |
+-----------------+--------------------------------------------------------------------------------------------+
| Administrador   | Acceso total. Gestión de usuarios, clientes, equipos, órdenes, analytics, backup y         |
|                 | restauración de base de datos.                                                             |
+-----------------+--------------------------------------------------------------------------------------------+
| Secretario      | Crear/editar clientes, equipos y órdenes. Aprobar/rechazar presupuestos. Gestionar         |
|                 | entregas. Sin acceso a usuarios ni analytics.                                              |
+-----------------+--------------------------------------------------------------------------------------------+
| Técnico         | Ver y actualizar órdenes asignadas. Cambiar estados técnicos (diagnóstico, reparación,    |
|                 | listo). Sin acceso a aprobación de presupuesto ni entrega.                                 |
+-----------------+--------------------------------------------------------------------------------------------+

Nota de seguridad:
El administrador puede simular otros roles desde el panel para verificar la experiencia de cada perfil. 
La verificación del rol real se realiza siempre contra la base de datos, no contra la sesión, para prevenir 
escalada de privilegios.

6.3 Protección contra Vulnerabilidades Comunes
Se especifican a continuación las mitigaciones implementadas frente al estándar OWASP Top 10:

+---------------------------+--------------------------------------------------------------------------------------+
| Vulnerabilidad            | Mitigación implementada                                                              |
+---------------------------+--------------------------------------------------------------------------------------+
| SQL Injection             | SQLAlchemy ORM con parámetros vinculados. Ninguna query construye SQL con f-strings  |
|                           | de datos externos.                                                                   |
+---------------------------+--------------------------------------------------------------------------------------+
| XSS                       | Jinja2 escapa automáticamente todas las variables en templates. Sin uso de |safe en  |
| (Cross-Site Scripting)    | datos provistos por el usuario.                                                      |
+---------------------------+--------------------------------------------------------------------------------------+
| CSRF                      | Flask-WTF CSRFProtect activo globalmente. Token CSRF requerido en todos los          |
| (Cross-Site Request Forg) | formularios POST.                                                                    |
+---------------------------+--------------------------------------------------------------------------------------+
| Enumeración de usuarios   | Login retorna siempre el mismo mensaje genérico ('Usuario o contraseña incorrectos') |
|                           | independientemente de si el usuario existe o no.                                     |
+---------------------------+--------------------------------------------------------------------------------------+
| Timing attack             | La verificación de contraseña ocurre antes de verificar el estado de la cuenta,      |
|                           | equalizando el tiempo de respuesta en solicitudes inválidas.                         |
+---------------------------+--------------------------------------------------------------------------------------+
| Fuerza bruta              | Bloqueo automático tras 5 intentos fallidos. Cuenta desactivada hasta intervención |
|                           | del administrador.                                                                   |
+---------------------------+--------------------------------------------------------------------------------------+
| Datos sensibles en código | Credenciales de BD y SECRET_KEY cargadas desde variables de entorno (os.environ.get).|
+---------------------------+--------------------------------------------------------------------------------------+


--------------------------------------------------------------------------------
7. ESTRUCTURA DIRECTA DE ARCHIVOS DEL PROYECTO
--------------------------------------------------------------------------------
La distribución modular del código fuente se presenta a continuación:

/proyectos seminario
│
├── apis/
│   └── fastapi.py            # Microservicio asíncrono para paralelizar scrapers
│
├── backend/
│   ├── controller/           # Controladores de la lógica de negocio (MVC)
│   │   ├── admin_controller.py
│   │   ├── analytics_controller.py
│   │   ├── auth_controller.py
│   │   ├── cliente_controller.py
│   │   ├── equipo_controller.py
│   │   ├── notificacion_controller.py
│   │   ├── orden_flujo_controller.py
│   │   ├── orden_presupuesto_controller.py
│   │   ├── orden_servicio_controller.py
│   │   ├── search_controller.py
│   │   ├── tipo_dispositivo_controller.py
│   │   └── usuario_controller.py
│   │
│   ├── models/               # Clases y Enums del modelo de datos de SQLAlchemy
│   │   ├── Cliente.py
│   │   ├── Equipo.py
│   │   ├── EstadoOrden.py
│   │   ├── HistorialEstado.py
│   │   ├── Notificacion.py
│   │   ├── OrdenServicio.py
│   │   ├── Rol.py
│   │   ├── TipoDispositivo.py
│   │   └── Usuario.py
│   │
│   ├── routes/               # Modularización de endpoints de vistas y APIs Flask
│   │   ├── admin_route.py
│   │   ├── cliente_route.py
│   │   ├── equipo_route.py
│   │   ├── notificacion_route.py
│   │   ├── orden_servicio_route.py
│   │   ├── tipo_dispositivo_route.py
│   │   ├── usuario_route.py
│   │   └── vistas_route.py
│   │
│   └── utils/
│       └── decorators.py     # Filtros interceptores de autenticación y RBAC
│
├── frontend/                 # Plantillas HTML y archivos estáticos (CSS/JS)
│   ├── static/
│   └── templates/
│
├── scrappers/                # Motores individuales de extracción anti-bot
│   ├── fravega.py
│   ├── fullstore.py
│   ├── infopartes.py
│   ├── megatone.py
│   └── mercadoLibre.py
│
├── app.py                    # Punto de entrada y configuraciones de seguridad
├── database.py               # Inicialización del objeto SQLAlchemy central
├── datos_prueba.py           # Script de siembra de registros realistas (Seed)
├── requirements.txt          # Dependencias y librerías requeridas
└── LIBRERIAS.md              # Documentación interna de dependencias del sistema

================================================================================
FIN DEL DOCUMENTO TÉCNICO DE REFERENCIA
================================================================================
