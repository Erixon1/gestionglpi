# Guía de Ejecución y Pruebas — Bot ReadOut Avisos y Auditoría (UiPath)

Este documento detalla el paso a paso completo para preparar el entorno, cargar datos de prueba de morosos, ejecutar el bot RPA en **UiPath Studio**, evaluar la matriz de pruebas (P1 a P5) y auditar los resultados generados (notificaciones por correo y reporte ejecutivo en Excel).

---

## 1. Arquitectura y Funcionalidad del Bot

El bot implementa dos procesos automatizados sin modificar el código de la aplicación **ReadOut**:
1. **Avisos de Morosidad a Lectores (Mejora 1):** Inicia sesión en ReadOut, extrae el directorio de usuarios (`/users`) y préstamos activos (`/loans?status=Activo|Atrasado`), calcula los días de mora (`fecha_devolución < hoy`), clasifica la criticidad (*Leve*, *Moderado*, *Grave*) y envía un correo HTML personalizado a cada alumno atrasado.
2. **Módulo de Auditoría y Métricas (Módulo 5):** Consolida KPIs institucionales (tasa de morosidad, promedio de atraso, inventario comprometido, ranking de libros y lectores) en un Excel de dos pestañas y despacha un resumen ejecutivo al bibliotecario con el archivo adjunto.

---

## 2. Requisitos Previos

* **Docker Desktop** (para la base de datos MySQL y la plataforma ReadOut).
* **UiPath Studio Community** con la extensión de navegador instalada y activa en **Microsoft Edge**.
* **Python 3** (para el servidor receptor SMTP de pruebas local).
* **Microsoft Excel** instalado.

---

## 3. Paso a Paso para la Ejecución Completa

### Paso 1: Levantar los contenedores de ReadOut
En una consola de PowerShell ejecuta:
```powershell
docker start biblioteca-db biblioteca-laravel biblioteca-frontend
```
> Verifica en tu navegador Edge que `http://localhost:8082` cargue la pantalla de login de ReadOut.

---

### Paso 2: Cargar datos de prueba (Lectores y Préstamos con Mora)
Para evaluar los distintos escenarios (*Leve*, *Moderado*, *Grave*, préstamos vigentes y devueltos), conéctate a la base de datos en Docker:

```powershell
docker exec -it biblioteca-db mysql -uroot -pBibliotecaRoot2026 biblioteca
```

Una vez dentro del prompt `mysql>`, copia y ejecuta el siguiente bloque SQL:

```sql
-- 1. Crear usuarios de prueba con rol Lector
insert into users(name,email,password,role_id,created_at,updated_at) select 'Ana Perez','ana@lectores.test',password,3,now(),now() from users where id=1;
insert into users(name,email,password,role_id,created_at,updated_at) select 'Luis Gomez','luis@lectores.test',password,3,now(),now() from users where id=1;
insert into users(name,email,password,role_id,created_at,updated_at) select 'Marta Rios','marta@lectores.test',password,3,now(),now() from users where id=1;

-- 2. Préstamos vencidos con diferentes criticidades:
-- Ana Perez: 5 días de retraso -> Criticidad MODERADA
insert into loans(book_id,user_id,user_name,loan_date,return_date,status) select 6,id,name,date_sub(curdate(),interval 12 day),date_sub(curdate(),interval 5 day),'Activo' from users where email='ana@lectores.test';

-- Luis Gomez: 10 días de retraso -> Criticidad GRAVE (Riesgo de pérdida)
insert into loans(book_id,user_id,user_name,loan_date,return_date,status) select 7,id,name,date_sub(curdate(),interval 17 day),date_sub(curdate(),interval 10 day),'Activo' from users where email='luis@lectores.test';

-- Marta Rios: 2 días de retraso -> Criticidad LEVE
insert into loans(book_id,user_id,user_name,loan_date,return_date,status) select 8,id,name,date_sub(curdate(),interval 9 day),date_sub(curdate(),interval 2 day),'Atrasado' from users where email='marta@lectores.test';

-- 3. Casos de control (NO deben ser alertados como morosos):
-- Préstamo vigente a futuro
insert into loans(book_id,user_id,user_name,loan_date,return_date,status) select 9,id,name,curdate(),date_add(curdate(),interval 7 day),'Activo' from users where email='luis@lectores.test';
-- Préstamo histórico devuelto
insert into loans(book_id,user_id,user_name,loan_date,return_date,status) select 10,id,name,date_sub(curdate(),interval 30 day),date_sub(curdate(),interval 23 day),'Devuelto' from users where email='ana@lectores.test';
```

Escribe `exit;` para salir de MySQL.

---

### Paso 3: Iniciar el servidor local de correos (SMTP Sink)
Para interceptar todos los correos en tu máquina sin requerir credenciales reales de Gmail ni saturar buzones:

1. Abre una terminal en la carpeta del bot:
   ```powershell
   cd c:\Users\Nox\Documents\TIC\gestionglpi\uipath-readout-avisos
   python Pruebas\smtp_sink.py
   ```
2. **Deja esa terminal abierta.** Verás un mensaje indicando que está escuchando en `127.0.0.1:2525`. El script creará automáticamente las carpetas por fecha (`Pruebas/correos/YYYY-MM-DD/`) con su propio `index.html`.

---

### Paso 4: Validar la configuración del bot
Asegúrate de que el archivo `Config.xlsx` contenga la configuración para entorno local:

| Parámetro | Valor | Descripción |
|---|---|---|
| `base_url` | `http://localhost:8082` | URL del frontend en Docker |
| `login_email` | `admin@biblioteca.com` | Usuario con permisos `loans.view_all` y `users.manage` |
| `login_password` | `admin123` | Contraseña |
| `smtp_host` | `127.0.0.1` | Servidor local |
| `smtp_port` | `2525` | Puerto de escucha |
| `smtp_ssl` | `FALSE` | Conexión directa sin SSL para pruebas |
| `mail_bibliotecario`| `bibliotecario@biblioteca.com` | Buzón receptor del consolidado |
| `enable_student_emails` | `TRUE` | Activa el envío de avisos a alumnos |
| `enable_audit_kpis` | `TRUE` | Genera pestaña y cálculos de KPIs |
| `send_if_empty` | `TRUE` | Envía confirmación diaria aunque no haya morosos |

> ⚠️ **IMPORTANTE:** Cierra Microsoft Excel y todas las ventanas de Microsoft Edge antes de ejecutar. Si dejas archivos abiertos, UiPath se bloqueará.

---

### Paso 5: Ejecución en UiPath Studio
1. Abre **UiPath Studio**.
2. Haz clic en **Abrir (Open)** y selecciona el archivo `project.json` dentro de `uipath-readout-avisos`.
3. Abre el archivo `Main.xaml`.
4. Presiona **F5** (o botón *Run File / Ejecutar archivo*).
5. **No uses el teclado ni el ratón** durante los 1–2 minutos de ejecución. El bot controlará Edge, ingresará al sistema, extraerá las tablas, generará el Excel y despachará los correos.

---

## 4. Matriz de Casos de Prueba (P1 al P5)

### 🔹 Prueba P1 y P2: Detección de Mora y Notificación Individual
* **Condición:** `enable_student_emails = TRUE`.
* **Resultado:** 
  * En `Pruebas/correos/YYYY-MM-DD/index.html` se generan los correos para `luis@lectores.test` (10 días, **Grave**), `ana@lectores.test` (5 días, **Moderado**) y `marta@lectores.test` (2 días, **Leve**).
  * En el Excel, la columna *Estado Notificación* marca `Sí (HH:mm:ss)`. Los préstamos vigentes y devueltos no aparecen.

### 🔹 Prueba P3: Modo Simulación (`enable_student_emails = FALSE`)
* **Condición:** Cambiar `enable_student_emails` a `FALSE` en `Config.xlsx` y ejecutar (F5).
* **Resultado:** No se genera ningún correo para alumnos. El Excel marca `No enviado (modo prueba)` y solo se despacha el correo resumen al bibliotecario.

### 🔹 Prueba P4: Auditoría Ejecutiva y KPIs
* **Condición:** `enable_audit_kpis = TRUE`.
* **Resultado:** La hoja `Auditoria y KPIs` en Excel calcula la tasa de morosidad, promedio de retraso, cantidad por nivel de gravedad y los rankings Top 3 de libros y usuarios.

### 🔹 Prueba P5: Robustez ante Fallo SMTP
* **Condición:** Detener `smtp_sink.py` (o puerto incorrecto en `Config.xlsx`) y ejecutar (F5).
* **Resultado:** El bot no se cuelga: conserva el Excel generado en `Output/` y captura el error en `Logs/error_YYYYMMDD_HHmmss.txt` y `Logs/error_YYYYMMDD_HHmmss.png`.

---

## 5. Dónde Visualizar los Resultados

### 📊 Reporte Ejecutivo en Excel
Se guarda en la carpeta `Output/` con la fecha de ejecución:
* Ruta: `uipath-readout-avisos/Output/avisos_vencidos_YYYY-MM-DD.xlsx`
* **Pestaña "Detalle Morosos":** Tabla ordenada descendentemente por días de atraso (`ID | Libro | Usuario | Email | F. Devolución | Días Atraso | Criticidad | Estado Notificación`).
* **Pestaña "Auditoria y KPIs":** Panel con la tasa de morosidad institucional, desglose de mora (*Grave/Moderado/Leve*), total de títulos comprometidos y ranking *Top 3 libros y lectores*.

### 📬 Bandeja Web de Correos Interceptados
Los correos se organizan automáticamente por carpetas diarias para no mezclar ejecuciones:
* Ruta: `uipath-readout-avisos/Pruebas/correos/YYYY-MM-DD/`
* **Visor central del día (`index.html`):** Haz doble clic en el archivo `index.html` de esa carpeta para ver una tabla interactiva con todos los correos generados, etiquetados por tipo (*Lector* o *Bibliotecario*) con botones para abrirlos en el navegador.
* **Archivos `.eml`:** Disponibles en la misma carpeta para abrirlos con **Microsoft Outlook** o la app **Correo** de Windows y verificar la descarga del Excel adjunto.

---

## 6. Limpieza de Datos de Prueba (Opcional)
Para restablecer la base de datos a su estado original después de las pruebas:
```powershell
docker exec -it biblioteca-db mysql -uroot -pBibliotecaRoot2026 biblioteca -e "delete from loans where user_name in ('Ana Perez','Luis Gomez','Marta Rios'); delete from users where email in ('ana@lectores.test','luis@lectores.test','marta@lectores.test');"
```
