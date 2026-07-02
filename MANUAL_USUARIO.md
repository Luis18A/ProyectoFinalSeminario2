# Manual de Usuario de TechFlow

Bienvenido al Manual de Usuario de **TechFlow**. Este manual está escrito con un lenguaje sencillo y libre de tecnicismos para ayudarte a comprender cómo funciona el sistema y cómo podés sacarle el máximo provecho en el día a día de tu taller de reparaciones.

---

## 1. ¿Qué es TechFlow?

**TechFlow** es una herramienta digital creada para organizar, controlar y agilizar el trabajo diario en talleres de reparación de tecnología (computadoras, celulares, tablets, etc.). 

Con TechFlow vas a poder:
* Llevar un registro completo de tus **Clientes** y sus **Equipos**.
* Seguir de cerca el estado de cada reparación (desde que entra al taller hasta que el cliente lo retira).
* Buscar y comparar precios de repuestos en internet en tiempo real para armar presupuestos.
* Imprimir comprobantes de servicio profesionales para tus clientes.
* Conocer mejor tu negocio mediante reportes visuales de ganancias, gastos y clientes más habituales.

---

## 2. Primeros Pasos

### Acceso al Sistema
Para abrir el programa, simplemente abrís tu navegador de internet (Chrome, Edge, Firefox, etc.) e ingresás la dirección web del taller (ejemplo local: `http://127.0.0.1:5000` o la dirección que te proporcione tu administrador).

### Cuentas de Acceso (Ejemplos de Roles)
El sistema cuenta con tres tipos de perfiles diferentes según la tarea que realices en el taller:

1. **Administrador** (Acceso total al sistema y finanzas)
   * **Usuario:** `admin` | **Contraseña:** `admin123`
2. **Secretario / Recepcionista** (Registra clientes, recibe equipos y entrega comprobantes)
   * **Usuario:** `secretario` | **Contraseña:** `secretario123`
3. **Técnico** (Revisa los equipos, realiza diagnósticos y repara)
   * **Usuario:** `tecnico` | **Contraseña:** `tecnico123`

---

## 3. Guía de Uso (Paso a Paso)

### Paso A: Registrar un Cliente
Antes de registrar un equipo, necesitamos registrar a su dueño:
1. En el menú superior o lateral, ingresá a la sección **Clientes**.
2. Presioná el botón **Registrar Cliente**.
3. Completá los datos básicos: Nombre, Apellido, DNI o CUIL, Teléfono y Correo Electrónico.
4. Presioná **Guardar**.

### Paso B: Registrar un Equipo y Generar un Ticket
Una vez que el cliente ya existe, registramos el equipo que nos trae para reparar:
1. Ve a la sección **Equipos** o haz clic en "Ver Equipos" dentro del cliente creado.
2. Hacé clic en **Nuevo Equipo**.
3. Seleccioná el tipo de dispositivo (Notebook, Celular, Consola, etc.), escribí la marca, el modelo y el número de serie si lo tiene.
4. En el mismo formulario, iniciá el **Ticket de Servicio**:
   * Describí detalladamente la falla que reporta el cliente (ejemplo: *"No enciende después de una tormenta"*).
   * Indicá qué accesorios deja (ejemplo: *"Cargador original y funda"*).
5. Presioná **Registrar**. El sistema generará automáticamente un número de orden único y podrás imprimir el **Comprobante** para el cliente.

### Paso C: Diagnóstico y Cotización de Repuestos (Trabajo del Técnico)
El técnico verá los equipos listos para ser revisados en su tablero de trabajo:
1. Desde el **Tablero Técnico**, hacé clic en **Ver/Gestionar** sobre la orden del equipo asignado.
2. Cambiá el estado a **En Diagnóstico** para avisar que estás trabajando en él.
3. Indicá el tipo de falla detectado en la lista desplegable.
4. **Buscador de Repuestos Integrado**:
   * Si la reparación requiere una pieza nueva (ejemplo: un disco SSD), escribí lo que buscás en la barra *"Buscador de Repuestos Integrado"* y hacé clic en **Buscar**.
   * El sistema buscará precios y enlaces reales en tiendas online (MercadoLibre, Megatone, Fravega, InfoPartes, etc.).
   * Hacé clic en **+ Cotizar** al lado de la mejor oferta. Se agregará automáticamente al desglose del costo del ticket.
5. Cargá el precio de tu **Mano de Obra** en el campo correspondiente.
6. Guardá los cambios y avanzá el estado a **Presupuestado**.

### Paso D: Reparación, Finalización y Entrega
1. Una vez que el cliente aprueba el presupuesto, podés cambiar el estado del ticket a **En Reparación**.
2. Cuando el equipo esté reparado y verificado, cambialo a **Listo para Entregar**. El cliente recibirá una notificación interna y sabrá que puede retirar su equipo.
3. Al momento del retiro y pago, pasá la orden a **Entregado**. El proceso finaliza y queda registrado el cobro.

---

## 4. Preguntas Frecuentes y Solución de Problemas

### El buscador de repuestos se queda cargando o muestra un error en rojo
* **¿Qué hacer?**: Asegurate de que tu computadora tenga conexión a internet. Dado que el sistema busca precios reales en vivo en portales de internet, requiere acceso constante a la red. Si el problema persiste, intenta buscar con términos más sencillos (ejemplo: usa `"SSD 480"` en lugar de `"Disco rígido de estado sólido Kingston de 480 gigabytes"`).

### No puedo ingresar al sistema, me dice que las credenciales son inválidas
* **¿Qué hacer?**: Verificá que la tecla de mayúsculas no esté activada. Las contraseñas en TechFlow diferencian mayúsculas de minúsculas. Si estás usando una base de datos nueva, recordá usar las cuentas por defecto (`admin` / `admin123`).

### No veo el botón de "Ganancias" o el "Tablero Técnico"
* **¿Qué hacer?**: El menú de opciones cambia de acuerdo a tu rol de usuario.
  * Si iniciaste sesión como **Secretario**, no verás las herramientas de diagnóstico técnico ni los gráficos de ganancias.
  * Si iniciaste sesión como **Técnico**, verás únicamente tus equipos asignados y el buscador de repuestos, pero no las herramientas de facturación ni la gestión de usuarios.
  * Si necesitás ver todo, solicitá a tu taller ingresar con el perfil de **Administrador**.
