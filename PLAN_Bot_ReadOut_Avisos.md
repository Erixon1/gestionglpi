# Plan: Bot "ReadOut Avisos y Auditoría" — Alerta de Préstamos Vencidos, Notificación a Lectores y Auditoría Ejecutiva (UiPath)

> Proyecto **ReadOut** (Sistema de Biblioteca) · Herramientas de Desarrollo Profesional – TIC  
> Unidad 4. Automatización con RPA y No-Code/Low-Code · Sesión 12: Automatización con Bots Básicos  
> Alcance ampliado: **Excel de Morosos + Notificación Directa al Lector + Resumen al Bibliotecario + Reporte Semanal/Mensual de Auditoría**

---

## 1. Objetivo General

Implementar un proceso RPA en UiPath que automatice de forma integral el control de morosidad y auditoría del sistema de biblioteca ReadOut:
1. **Control de Morosidad y Avisos:** Ingresa diariamente al sistema, extrae los préstamos activos, detecta los préstamos vencidos, **notifica directamente al lector por correo** con su aviso formal, genera la planilla consolidada en Excel y envía un correo resumen al bibliotecario con el archivo adjunto.
2. **Módulo de Auditoría y Métricas:** Consolida indicadores clave de la biblioteca (tasa de morosidad, libros con mayor retraso, inventario comprometido) generando una hoja ejecutiva para la toma de decisiones.

---

## 2. Justificación (Huecos que cubre en el proyecto)

| Hallazgo en ReadOut | Evidencia en el código | Solución RPA (UiPath) |
|---|---|---|
| Préstamos vencidos nunca se alertan en el sistema | `server-laravel/app/Services/LoanService.php:103` (`markOverdueLoans()` existe pero no hay scheduler ni cron configurado en Laravel) | El bot calcula los días de mora en tiempo de ejecución: `return_date < hoy`. |
| Carga manual de cobranza sobre el bibliotecario | El bibliotecario debe contactar manualmente a cada lector atrasado | **Mejora 1:** El bot envía un correo personalizado individual a cada lector moroso avisando del retraso. |
| Ausencia de reportes analíticos y exportación | `LoansView.vue` no cuenta con exportación a Excel/PDF ni dashboard analítico | **Módulo 5 (Auditoría):** El bot genera un Excel con hoja de auditoría y métricas clave (KPIs). |
| Privilegios y acceso sin alterar código | Interfaz web funcional bajo Sanctum (`admin@biblioteca.com` con `loans.view_all` y `users.manage`) | El bot opera como usuario de negocio automatizado sin modificar el código fuente de ReadOut. |

---

## 3. Hallazgos del Código y Reglas de Negocio

| Aspecto | Dato técnico verificado | Implicancia para el bot |
|---|---|---|
| URL y Login | Vue 3 / Vite en puerto `5173`; `#email`, `#password`, `#btn-login` (`LoginView.vue`) | Selectores HTML estables por ID. |
| Ruta de Préstamos | `/loans?status=Activo` (`LoansView.vue:342`) | Navegación directa por query param sin depender de controles custom `BaseCombobox`. |
| Email del Lector | La tabla `/loans` muestra `user_name`. La ruta `/users` (`UsersView.vue`) mapea `Nombre` ↔ `Email` | El bot extrae el directorio de usuarios de `/users` una sola vez para resolver el correo de cada lector moroso. |
| Formato de Fechas | Renderizado `05 nov. 2026` (es-PE, `formatDate`) | Diccionario de mapeo de meses (`ene`..`dic`) para parsear fechas de devolución. |
| Paginación | Botones "Anterior" y "Siguiente" con `disabled` condicional (`LoansView.vue:104-112`) | Bucle de paginación guiado por la propiedad deshabilitada de `Siguiente`. |
| Plazo Estándar | 7 días de préstamo por regla de negocio (`LoansView.vue:300-307`) | Contexto normativo incluido en el correo enviado al estudiante/docente. |

---

## 4. Estructura del Proyecto UiPath

```
ReadOutAvisosAuditoria/
├── Main.xaml                      ← Flujo principal / orquestador
├── Config.xlsx                    ← Parámetros (URLs, credenciales, switches, SMTP)
├── Data/
│   ├── Plantilla_Aviso_Lector.html ← Plantilla HTML con placeholders ({Nombre}, {Libro}, {Dias})
│   └── Plantilla_Auditoria.xlsx   ← Plantilla con formato de reporte y KPIs
└── Output/
    ├── avisos_vencidos_YYYY-MM-DD.xlsx
    └── auditoria_prestamos_YYYY-MM-DD.xlsx (o pestaña adicional consolidada)
```

### Configuración (`Config.xlsx`)

| Parámetro | Ejemplo | Descripción |
|---|---|---|
| `base_url` | `http://localhost:5173` | URL de ReadOut |
| `login_email` | `admin@biblioteca.com` | Usuario con permisos `loans.view_all` y `users.manage` |
| `login_password` | `admin123` | Contraseña |
| `smtp_host` | `smtp.gmail.com` | Servidor de correo saliente |
| `smtp_port` | `587` | Puerto STARTTLS |
| `smtp_user` | `biblioteca.readout@gmail.com` | Buzón remitente |
| `smtp_password` | *(App Password de 16 caracteres)* | Credencial segura de aplicación |
| `mail_bibliotecario`| `bibliotecario@biblioteca.com` | Correo donde llega el consolidado diario |
| `enable_student_emails` | `TRUE` | Bandera: `TRUE` envía a lectores; `FALSE` solo al bibliotecario (modo testing) |
| `enable_audit_kpis` | `TRUE` | Bandera: `TRUE` genera hoja de métricas y auditoría |

---

## 5. Arquitectura del Flujo Paso a Paso (`Main.xaml`)

### Fase 1: Inicialización y Lectura de Configuración
1. `Try/Catch` global con gestión de logs y `Take Screenshot` en caso de error.
2. `Read Range` sobre `Config.xlsx` para cargar diccionario `in_Config`.

### Fase 2: Extracción de Datos (Web Scraping UI)
3. **Open Browser (Chrome/Edge)** → Navegar a `{base_url}/login`.
4. `Type Into` usuario/clave y `Click` en Iniciar Sesión.
5. **Carga de Directorio de Usuarios (para correos):**
   * Navegar a `{base_url}/users`.
   * `Extract Structured Data` sobre la tabla de usuarios: columnas `[Nombre, Email]`. Guardar en `dtUsuarios`.
6. **Extracción de Préstamos Activos:**
   * Navegar a `{base_url}/loans?status=Activo`.
   * Esperar desaparición del spinner (`.spinner-overlay`).
   * Bucle `While` mientras exista botón `Siguiente` activo:
     - `Extract Structured Data` de la tabla de préstamos: `[ID, Libro, Usuario, Fecha Préstamo, Fecha Devolución, Estado]`.
     - Si botón `Siguiente` habilitado → `Click` y esperar recarga; sino → salir del bucle.
   * `Close Window` / Cerrar navegador.

### Fase 3: Procesamiento de Negocio y Reglas de Auditoría
7. `For Each Row` sobre préstamos extraídos:
   * Parsear `Fecha Devolución`.
   * Si `Fecha Devolución < Hoy`:
     - Calcular `Días de Atraso = (Hoy - Fecha Devolución).Days`.
     - Cruzar `Usuario` con `dtUsuarios` para obtener su `Email`.
     - Categorizar nivel de criticidad de mora:
       - *Leve:* 1 a 3 días.
       - *Moderado:* 4 a 7 días.
       - *Grave (Riesgo de pérdida):* > 7 días.
     - Agregar a `dtVencidos`.

### Fase 4 (Mejora 1): Notificación Individual a Lectores Morosos
8. Si `enable_student_emails = TRUE` y existen registros en `dtVencidos`:
   * Bucle `For Each Row` sobre `dtVencidos`:
     - Si el usuario tiene email válido:
       - Cargar `Plantilla_Aviso_Lector.html` y reemplazar `{Nombre}`, `{Libro}`, `{FechaDevolucion}`, `{DiasAtraso}`.
       - Actividad `Send SMTP Mail` enviando correo formal al lector con asunto:  
         `[Aviso Importante] Préstamo vencido en Biblioteca: {Libro}`.
       - Registrar en columna de auditoría: `Notificado: Sí (HH:mm:ss)`.

### Fase 5 (Módulo 5): Generación de Reporte y Métricas de Auditoría
9. Cálculo de Indicadores Clave (KPIs) en memoria:
   * `Total Préstamos Activos` vs. `Total Préstamos Vencidos`.
   * `Tasa de Morosidad (%) = (Vencidos / Activos) * 100`.
   * `Promedio de días de atraso`.
   * `Top 3 libros con mayor tiempo en mora`.
   * `Top usuarios con retrasos recurrentes / críticos`.
10. `Write Range` en `Output/avisos_vencidos_YYYY-MM-DD.xlsx`:
    * **Hoja 1 ("Detalle Morosos"):** Listado ordenado descendentemente por días de atraso (`ID | Libro | Usuario | Email | F. Devolución | Días Atraso | Criticidad | Estado Notificación`).
    * **Hoja 2 ("Auditoría y KPIs"):** Tabla ejecutiva resumen con los indicadores del punto 9, fecha/hora de auditoría y total de lectores notificados.

### Fase 6: Despacho del Resumen Ejecutivo al Bibliotecario
11. Generar cuerpo HTML con el resumen ejecutivo:
    * Métricas del día (Total vencidos, mayor atraso, porcentaje de morosidad).
    * Alerta de casos críticos (> 7 días).
    * Notificación de cuántos avisos automáticos fueron enviados a los alumnos.
12. Adjuntar el archivo Excel completo y enviar vía `Send SMTP Mail` a `mail_bibliotecario`.

---

## 6. Plan de Pruebas y Validación

| Caso de Prueba | Entrada / Condición | Resultado Esperado |
|---|---|---|
| **P1. Filtro y cálculo de días** | Préstamo con fecha de hace 5 días | Calculado exactamente como 5 días de atraso; clasificado como "Moderado". |
| **P2. Notificación individual (Mejora 1)** | Registro vencido con email de prueba | Correo HTML entregado al buzón del lector con los datos correctos del libro. |
| **P3. Bandera de prueba (`enable_student_emails = FALSE`)** | Registros morosos detectados | No se envían correos a alumnos; solo se despacha el consolidado al bibliotecario. |
| **P4. Hoja de Auditoría (Módulo 5)** | 10 préstamos activos, 3 vencidos | Tasa de morosidad reflejada al 30%; KPIs y promedios calculados correctamente en Hoja 2. |
| **P5. Control de fallos (Robusteza)** | SMTP con contraseña inválida | Bot atrapa la excepción, guarda el Excel en disco y genera captura de pantalla en `Logs/`. |

---

## 7. Entregables del Bot Actualizado

1. **Workflow UiPath:** Archivos `.xaml` con arquitectura modular (`Main.xaml`, `NotificarLectores.xaml`, `CalcularAuditoria.xaml`).
2. **Archivos de Configuración y Plantillas:** `Config.xlsx`, `Plantilla_Aviso_Lector.html`.
3. **Reporte Consolidado:** `avisos_vencidos_<fecha>.xlsx` con hojas de Detalle y Auditoría/KPIs.
4. **Evidencias:** Capturas del correo recibido por el lector, del correo recibido por el bibliotecario y del log de ejecución en UiPath Assistant.
