@echo off
title Sistema ReadOut / Gestion GLPI - Iniciador
echo ======================================================================
echo          Iniciando Stack Completo: GLPI + Laravel + Vue 3
echo ======================================================================
echo.

echo [*] 1. Levantando Contenedores Docker (MariaDB + GLPI + Laravel + Mailpit)...
docker compose up -d

echo.
echo [*] 2. Verificando estado de los contenedores...
docker compose ps

echo.
echo [*] 3. Iniciando Servidor Frontend Vue 3 (Vite)...
start "ReadOut Frontend (Vite)" cmd /k "cd client && npm run dev"

echo.
echo ======================================================================
echo    [OK] Despliegue completado exitosamente!
echo    - Frontend Web:        http://localhost:5173
echo    - Backend API Laravel: http://localhost:8000/api
echo    - Consola GLPI:        http://localhost:8080 (Usuario: glpi / glpi)
echo    - Servidor Mailpit:    http://localhost:8025
echo.
echo    Credenciales por defecto (Sistema Biblioteca):
echo    - Admin:         admin@biblioteca.com / admin123
echo    - Bibliotecario: bibliotecario@biblioteca.com / admin123
echo ======================================================================
pause
