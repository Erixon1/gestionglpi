# Sistema de Biblioteca - Proyecto Integrado

Este repositorio contiene el sistema completo de gestión de biblioteca, incluyendo el frontend, el backend administrativo y la integración con el inventario GLPI.

## Estructura del Proyecto

- **`/client`**: Aplicación Frontend desarrollada en Vue.js.
- **`/server-laravel`**: API Backend desarrollada en Laravel 10.
- **`/server-glpi`**: Entorno Dockerizado con GLPI y su respectiva base de datos MariaDB.
- **`/db_backups`**: Exportaciones SQL con los datos actuales (libros, usuarios, activos).

## Requisitos Previos

1. **Docker y Docker Compose** (para GLPI).
2. **PHP >= 8.1** y **Composer** (para Laravel).
3. **Node.js >= 18** y **NPM/PNPM** (para el Cliente).
4. **Servidor MySQL/MariaDB** local (ej. XAMPP o Laragon) para la base de datos de Laravel.

## Pasos para la Restauración

### 1. Clonar y configurar variables de entorno
Crea los archivos `.env` en `/client` y `/server-laravel` basándote en los archivos de configuración actuales.

### 2. Levantar GLPI (Docker)
```bash
cd server-glpi
docker-compose up -d
```

### 3. Restaurar Bases de Datos
Para no perder los libros y usuarios existentes, importa los dumps incluidos:

**Para Laravel (Base de datos: `biblioteca`):**
Importa `db_backups/laravel_biblioteca.sql` en tu MySQL local.

**Para GLPI (Servicio Docker):**
```bash
# Una vez que el contenedor glpi-db esté arriba:
docker exec -i glpi-db mysql -u glpi_user -pglpi_pass glpi_db < db_backups/glpi_db.sql
```

### 4. Instalar dependencias
```bash
# Server Laravel
cd server-laravel
composer install
php artisan key:generate

# Client
cd client
npm install
```

## Credenciales por defecto
- **Admin Laravel**: admin@biblioteca.com / admin123
- **GLPI**: glpi / glpi (usuario por defecto del sistema)

## Imagenes del proyecto

<img width="1917" height="946" alt="image" src="https://github.com/user-attachments/assets/25161a2a-c5ab-4a54-acb3-78f431f7aea7" />

<img width="1901" height="987" alt="image" src="https://github.com/user-attachments/assets/9c465b46-3980-400d-84ce-42fa29bc6213" />

<img width="1919" height="991" alt="image" src="https://github.com/user-attachments/assets/bffd3771-57a7-491c-8543-bb5ff2b94548" />

<img width="1918" height="949" alt="image" src="https://github.com/user-attachments/assets/b9914826-e617-47e3-b3da-bc388e7ef143" />

<img width="1915" height="989" alt="image" src="https://github.com/user-attachments/assets/76d2d41b-bc18-4c4c-beab-898fdebcd84c" />

<img width="1915" height="944" alt="image" src="https://github.com/user-attachments/assets/0cb3ad47-97c9-43cb-90fc-d225260305f2" />

<img width="1918" height="985" alt="image" src="https://github.com/user-attachments/assets/734f3d49-310e-46f8-a357-d78b977491d4" />

<img width="1916" height="948" alt="image" src="https://github.com/user-attachments/assets/98d90ac2-cfc2-4536-97ca-255543899659" />




