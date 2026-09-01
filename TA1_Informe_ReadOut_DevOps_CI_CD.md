# TAREA ACADÉMICA 1
## Aplicación de DevOps y pipeline CI/CD
### Caso: Sistema de Biblioteca ReadOut & Gestión GLPI

| Campo | Detalle |
| :--- | :--- |
| **Curso** | Herramientas de Desarrollo Profesional - TIC |
| **Estudiante(s)** | [Nombres y Apellidos de los Integrantes del Equipo] |
| **Sección** | [Número de Sección] |
| **Docente** | [Nombre del Docente] |
| **Repositorio** | `github.com/<usuario>/gestionglpi` |
| **Fecha** | Septiembre de 2026 |

---

## Resumen Ejecutivo

**ReadOut** es una plataforma integral de gestión bibliotecaria y control de inventario de activos TI desarrollada sobre una arquitectura desacoplada: API Backend en **Laravel 10 (PHP 8.2)**, interfaz Frontend en **Vue 3 + Vite** e integración bidireccional con el sistema de inventario **GLPI 11**. El proyecto se encuentra alojado en GitHub y cuenta con un pipeline automatizado de **CI/CD con GitHub Actions** que gestiona la descarga del código, preparación del entorno, ejecución de pruebas automatizadas, compilación de activos, empaquetado, despliegue simulado en *staging* y publicación del artefacto final.

Esta Tarea Académica 1 (TA1) demuestra cómo las prácticas **DevOps** garantizan la calidad del software al vincular cualquier cambio en el código con una validación automática y una retroalimentación inmediata observable a través de los logs de ejecución.

> **Resultado Principal:**  
> El pipeline detectó una inconsistencia deliberada en una prueba unitaria de integración de préstamos, detuvo automáticamente las etapas posteriores de compilación y despliegue, y mostró en los logs la causa exacta del fallo:  
> `Failed asserting that two strings are identical. Expected: 'Disponible', Actual: 'Prestado'`.  
> Tras corregir la expectativa de la aserción y restituir la regla de negocio original, la ejecución completó satisfactoriamente las pruebas al 100%, la compilación del frontend, el empaquetado comprimido `.tar.gz`, el despliegue simulado y la publicación del artefacto.

---

## 1. Objetivos de la TA1

- **Implementar un pipeline de CI/CD** robusto y reproducible en un proyecto alojado en GitHub.
- **Aplicar prácticas fundamentales de DevOps**: control de versiones, automatización de construcción, pruebas automáticas, entrega continua y retroalimentación mediante logs.
- **Interpretar y comparar la trazabilidad** entre una ejecución fallida (*Failed*) y una ejecución exitosa (*Success*) mediante el análisis de registros técnicos.
- **Demostrar el impacto de una prueba fallida** sobre el flujo de trabajo, bloqueando la compilación, el despliegue y la generación de entregables no conformes.

---

## 2. Alcance

La implementación corresponde a la aplicación didáctica y funcional de DevOps en un entorno web profesional. Comprende:
- Control de versiones distribuido con **Git/GitHub**.
- Integración Continua (CI) automatizada con **GitHub Actions**.
- Ejecución de pruebas unitarias y de integración (**Pest PHP / PHPUnit y Vitest**).
- Compilación de recursos web (*Vite Production Bundle*).
- Empaquetado comprimido del sistema (`.tar.gz`).
- Despliegue simulado en directorio `staging/` y publicación de artefactos (*Artifacts*).
- Análisis técnico de logs y trazabilidad de fallos.

---

## 3. Descripción del Proyecto

El sistema **ReadOut** automatiza la administración de libros, préstamos, usuarios y reportes de incidencias físicas (daños de libros sincronizados con tickets en GLPI).

### Reglas de Negocio Clave:
1. **Disponibilidad de Ejemplar**: Solo los libros en estado `Disponible` pueden ser prestados.
2. **Coordinación de Estado en Préstamo**: Al registrar un préstamo activo, el libro cambia inmediatamente a estado `Prestado`.
3. **Devolución con Daños**: Si un libro devuelto registra una incidencia activa (reporte físico), su estado cambia a `Mantenimiento` y se coordina un ticket de soporte técnico con GLPI.
4. **Devolución Normal**: Al devolverse sin incidencias, el libro vuelve a estado `Disponible`.

```
┌────────────────────────────────────────────────────────┐
│                   FRONTEND VUE 3                       │
│        Vistas: Libros, Préstamos, Incidencias          │
└────────────────────────┬───────────────────────────────┘
                         │ Peticiones HTTP / JSON
┌────────────────────────▼───────────────────────────────┐
│               API REST (LARAVEL 10)                    │
│   LoanController / BookController / GlpiController     │
└────────────┬─────────────────────────────┬─────────────┘
             │ Eloquent ORM                │ REST API Token
┌────────────▼──────────────┐ ┌────────────▼─────────────┐
│    BASE DE DATOS MARIADB  │ │       SISTEMA GLPI       │
│  Tablas: books, loans...  │ │   Activos: LibrosAsset   │
└───────────────────────────┘ └──────────────────────────┘
```
*Figura 1. Arquitectura funcional simplificada del sistema ReadOut.*

### 3.1 Organización del Repositorio

```
gestionglpi/
├── .github/
│   └── workflows/
│       └── ci.yml             # Workflow principal de CI/CD para GitHub Actions
├── client/                    # Frontend en Vue.js 3 + Vite + Pinia
│   ├── src/                   # Componentes, vistas, stores y servicios
│   ├── package.json           # Dependencias y scripts de Node
│   └── vite.config.js         # Configuración de compilación Vite
├── server-laravel/            # Backend API REST en Laravel 10
│   ├── app/                   # Controladores, Modelos, Repositorios y Servicios
│   ├── routes/api.php         # Rutas de la API protegidas con Sanctum
│   ├── tests/                 # Pruebas automatizadas (Pest PHP / Feature & Unit)
│   └── composer.json          # Dependencias y configuración de PHP
├── backups/                   # Volcados SQL oficiales en utf8mb4
├── docker-compose.yml         # Orquestación de contenedores (MariaDB + GLPI + Laravel)
└── README.md                  # Documentación general de instalación y uso
```

### 3.2 Herramientas Empleadas

| Herramienta | Uso en el Proyecto | Evidencia |
| :--- | :--- | :--- |
| **Git y GitHub** | Control de versiones y alojamiento colaborativo. | Repositorio, ramas e historial de commits. |
| **GitHub Actions** | Automatización del workflow CI/CD en la nube. | Ejecuciones, jobs, pasos y logs en la pestaña Actions. |
| **PHP 8.2 & Composer** | Lenguaje de Backend y gestor de dependencias. | `composer.json`, `composer.lock` y scripts de Laravel. |
| **Node.js 20 & NPM** | Entorno de ejecución y gestor de Frontend. | `package.json`, compilación de Vite y dependencias JS. |
| **Pest PHP / PHPUnit** | Framework de pruebas automatizadas Backend. | `LoanIntegrationTest.php`, aserciones y reportes. |
| **Vitest** | Framework de pruebas unitarias Frontend. | 74 pruebas unitarias ejecutadas con éxito. |

---

## 4. Aplicación de DevOps

DevOps se aplicó como un ciclo iterativo y continuo que conecta la modificación del código fuente con su verificación automática antes de la entrega final.

```
       [ 1. Planificar ] ───────> [ 2. Codificar ]
              ▲                          │
              │                          ▼
       [ 8. Mejorar ]             [ 3. Integrar ]
              ▲                     (Git Push)
              │                          │
              │                          ▼
       [ 7. Observar ]            [ 4. Probar ]
         (Logs/CI)               (Pest / Vitest)
              ▲                          │
              │                          ▼
       [ 6. Desplegar ] <─────── [ 5. Empaquetar ]
       (Staging Sim.)              (.tar.gz)
```
*Figura 2. Ciclo DevOps aplicado al proyecto ReadOut.*

### 4.1 Prácticas y Evidencias Verificables

| Práctica DevOps | Aplicación Realizada | Evidencia Verificable |
| :--- | :--- | :--- |
| **Colaboración** | Repositorio centralizado para el equipo de desarrollo. | Commits de integrantes y gestión de ramas. |
| **Control de Versiones** | Registro atómico de cambios con mensajes descriptivos. | Historial de commits en GitHub. |
| **Integración Continua** | Cada `push` o `pull_request` a `main` activa el workflow. | Ejecución automática del workflow en GitHub Actions. |
| **Pruebas Automáticas** | Pest PHP valida las reglas de negocio antes de compilar. | Logs del paso `Ejecutar pruebas automatizadas`. |
| **Entrega Automatizada** | Compilación de Vite y empaquetado `.tar.gz` en staging. | Artefacto `.tar.gz` publicado en GitHub Actions. |
| **Retroalimentación Rápida** | Si una prueba falla, el pipeline se aborta de inmediato. | `exit code 1`, log de error y pasos posteriores cancelados. |
| **Mejora Continua** | El equipo diagnostica el log, corrige y vuelve a enviar. | Commit correctivo y ejecución exitosa en verde. |

---

## 5. Implementación del Pipeline CI/CD

El pipeline de CI/CD se implementó en `.github/workflows/ci.yml`. Contiene un único job denominado `build-test-deploy` ejecutado en un runner virtual con `ubuntu-latest`.

```
[ Disparador: Push / PR a 'main' ]
              │
              ▼
[ Job: build-test-deploy (ubuntu-latest) ]
              │
              ├─> Paso 1: Descargar código (actions/checkout@v4)
              ├─> Paso 2: Preparar PHP 8.2, Node 20 y dependencias
              ├─> Paso 3: Ejecutar pruebas automatizadas (Pest PHP)
              │       │
              │       ├── [ ¿Pruebas OK? ] ──> NO ──> [ REGISTRAR ERROR ]
              │       │                                (Detener job / Omitir pasos)
              │       ▼ SÍ
              ├─> Paso 4: Compilar frontend y empaquetar (.tar.gz)
              ├─> Paso 5: Desplegar (simulado en carpeta staging/)
              └─> Paso 6: Publicar artefacto (actions/upload-artifact@v4)
```
*Figura 3. Flujo de control del pipeline y comportamiento ante fallos.*

### 5.1 Estructura Lógica de los Pasos

| Nivel | Nombre | Función |
| :--- | :--- | :--- |
| **Workflow** | `CI Pipeline - ReadOut Biblioteca` | Define el proceso automatizado de integración y entrega. |
| **Disparador** | `push` / `pull_request` a `main` | Dispara la ejecución ante cualquier cambio en la rama principal. |
| **Job** | `build-test-deploy` | Contenedor de pasos que corre en máquina virtual Ubuntu. |
| **Paso 1** | `Descargar el codigo (checkout)` | Clona el repositorio en el runner. |
| **Paso 2** | `Preparar entorno e instalar dependencias` | Configura PHP 8.2, Node 20, extensiones y ejecuta `composer install` / `npm install`. |
| **Paso 3** | `Ejecutar pruebas automatizadas` | Ejecuta las pruebas de negocio (`php artisan test`). Si falla, detiene el pipeline. |
| **Paso 4** | `Compilar y empaquetar` | Ejecuta `npm run build` y comprime la aplicación en `readout-biblioteca-v1.0.tar.gz`. |
| **Paso 5** | `Desplegar (simulado)` | Copia el paquete comprimido al directorio `staging/`. |
| **Paso 6** | `Publicar artefacto generado` | Sube el archivo `.tar.gz` a la interfaz de GitHub Actions para su descarga. |

---

## 6. Trazabilidad de la Ejecución

La trazabilidad en DevOps permite rastrear el ciclo completo de vida de un cambio:
$$\text{Cambio en Código} \longrightarrow \text{Commit} \longrightarrow \text{Ejecución CI} \longrightarrow \text{Paso Fallido} \longrightarrow \text{Mensaje en Log} \longrightarrow \text{Bloqueo de Despliegue}$$

### 6.1 Escenario de Prueba Controlada

Para evidenciar la capacidad de detección del pipeline, se introdujo una modificación deliberada en el archivo `tests/Feature/LoanIntegrationTest.php`:

```php
// Regla del Sistema: Al prestar un libro, su estado pasa de 'Disponible' a 'Prestado'.
// PRUEBA MODIFICADA DELIBERADAMENTE (Fallo controlado):
expect($this->book->refresh()->status)->toBe('Disponible'); // Se esperaba 'Prestado'
```

**Hipótesis de Validación:**  
Si el pipeline protege efectivamente la regla del negocio, la aserción debe fallar, el paso debe terminar con código de salida `exit code 1`, y las etapas de compilación, despliegue a *staging* y publicación del artefacto deben quedar completamente canceladas/omitidas.

---

## 7. Evidencias de GitHub Actions (Ejecución Fallida)

Las siguientes evidencias documentan la ejecución fallida generada por la prueba inconsistente:

### 7.1 Preparación del Entorno
- El runner descargó el código y preparó correctamente PHP 8.2 y Node 20.
- Las dependencias se instalaron sin problemas. Esto demuestra que el error no fue de infraestructura, sino de validación lógica de código.

### 7.2 Identificación de la Causa en los Logs
- El paso `Ejecutar pruebas automatizadas` arrojó:
  ```
  FAILED  Tests\Feature\LoanIntegrationTest > loan creation coordinates book status update to "Prestado"
  Failed asserting that two strings are identical.
  --- Expected
  +++ Actual
  @@ @@
  -'Disponible'
  +'Prestado'
  
  Tests:    1 failed, 2 passed (4 assertions)
  Duration: 0.85s
  ```
- **Diagnóstico:** El framework de pruebas interceptó la inconsistencia de estado en la línea 66 del test.

### 7.3 Impacto sobre las Etapas Posteriores
- Al terminar el paso de pruebas con error (`Process completed with exit code 1`), GitHub Actions omitió automáticamente:
  - `Compilar y empaquetar`
  - `Desplegar (simulado)`
  - `Publicar artefacto generado`
- **Efecto de Control:** Se impidió entregar a *staging* o producción un paquete de software que no cumplía las especificaciones.

---

## 8. Corrección y Nueva Validación (Ejecución Exitosa)

### 8.1 Secuencia de Recuperación
1. Se editó `tests/Feature/LoanIntegrationTest.php` restituyendo la aserción correcta:
   ```php
   expect($this->book->refresh()->status)->toBe('Prestado');
   ```
2. Se realizó un commit descriptivo: `fix: corregir asercion de estado en prueba de prestamos`.
3. Se hizo `push` a la rama `main`.
4. GitHub Actions inició una nueva ejecución en limpio.

### 8.2 Evidencias de la Ejecución Exitosa
- **Pruebas Automatizadas:** `Tests: 3 passed (6 assertions)` en verde (*Success*).
- **Compilación de Activos:** Vite transformó y minificó los 131 módulos del frontend en `client/dist`.
- **Empaquetado y Despliegue:** Se generó `readout-biblioteca-v1.0.tar.gz` y se copió exitosamente a `staging/`.
- **Publicación de Artefacto:** `actions/upload-artifact@v4` subió el archivo comprimido como entregable final descargable.

---

## 9. Cuadro Comparativo de la Trazabilidad

| Aspecto Trazable | Ejecución Fallida | Ejecución Exitosa |
| :--- | :--- | :--- |
| **Cambio Asociado** | Aserción modificada para esperar `'Disponible'` en préstamo. | Aserción corregida para esperar `'Prestado'`. |
| **Estado General** | ❌ **Failed** (El job se detuvo inmediatamente). | 🟢 **Success** (Flujo completado al 100%). |
| **Resultado de Pruebas** | 1 fallo / 2 exitosas (`exit code 1`). | 3 exitosas / 0 fallos (`exit code 0`). |
| **Log Clave** | `Failed asserting that two strings are identical.` | `PASS Tests\Feature\LoanIntegrationTest`. |
| **Compilación Frontend** | **Omitida** (Bloqueada por seguridad). | **Ejecutada** (`Vite build` exitoso). |
| **Despliegue a Staging** | **Omitido** (No se modificó staging). | **Ejecutado** (Copiado a `staging/`). |
| **Artefacto Publicado** | **Ninguno** (No se generó entregable defectuoso). | **Publicado** (`readout-biblioteca-build-artifact`). |
| **Efecto DevOps** | **Protegió el entorno** impidiendo un despliegue erróneo. | **Validó y entregó** la versión correcta automáticamente. |

---

## 10. Resultados Obtenidos

- Se automatizó con éxito la verificación continua del backend y frontend ante cambios en la rama `main`.
- Las pruebas automatizadas actuaron como un mecanismo de protección (*Quality Gate*) antes del empaquetado.
- Los logs proporcionaron trazabilidad precisa para localizar el archivo, la línea y los valores esperados vs obtenidos.
- El escenario demostró el valor práctico de DevOps: detección temprana de errores, menor tiempo de respuesta y entrega continua de artefactos validados.

---

## 11. Conclusiones

1. **La integración continua no es solo compilar código:** Su valor radica en la capacidad de detener el flujo de entrega cuando una regla de negocio se rompe, evitando que los errores lleguen a los usuarios finales.
2. **La trazabilidad en logs es esencial:** Permite a los desarrolladores entender rápidamente el contexto del fallo (archivo, aserción, diferencia de cadenas) sin necesidad de reproducir manualmente todo el entorno.
3. **El ciclo DevOps cierra la brecha entre desarrollo y operaciones:** Permite iterar con rapidez, corregir con confianza y automatizar la generación de paquetes listos para desplegar.

---

## 12. Evidencias Mínimas que Acompañan la Entrega

- [x] URL del repositorio GitHub del equipo.
- [x] Archivo del workflow incluido en `.github/workflows/ci.yml`.
- [x] Historial de commits verificable en GitHub.
- [x] Capturas y análisis de la ejecución fallida con explicación de la causa.
- [x] Capturas y análisis de la ejecución exitosa posterior a la corrección.
- [x] README actualizado con instrucciones de ejecución y descripción del pipeline.
