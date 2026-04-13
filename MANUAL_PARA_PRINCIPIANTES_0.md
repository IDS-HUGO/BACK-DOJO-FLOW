# Manual para principiantes 0 - DojoFlow API

Este archivo explica, de forma simple, como funciona la API de DojoFlow, como levantarla y como se usa el flujo completo con el frontend.

## 1. Que es esta API

DojoFlow API es el backend en FastAPI.

Hace estas tareas:

- Autenticacion con JWT.
- Alta y consulta de alumnos.
- Cobros con PayPal.
- Ordenes de compra de planes.
- Dashboard de admin.
- Reportes.
- Configuracion de academia.
- Manejo de instructores, horarios, cupones y marketplace.

El frontend se conecta a esta API por HTTP.

## 2. Lo primero que debes saber

- La API corre por defecto en `http://localhost:8000`.
- El frontend espera la API en `http://localhost:8000/api/v1`.
- Si la API no esta encendida, el frontend no puede iniciar sesion ni cobrar.

## 3. Configuracion minima para levantarla

### Dependencias

Instala lo necesario con:

```bash
pip install -r requirements.txt
```

### Base de datos

La configuracion por defecto usa:

- Host: `localhost`
- Puerto: `3306`
- Usuario: `root`
- Password: `root`
- Base de datos: `dojoflow`

Si no defines `DATABASE_URL`, la aplicacion puede caer en SQLite local en `./dojoflow.db`.

### Seed inicial

Antes de probar todo, ejecuta:

```bash
python -m app.init_db
```

Eso crea tablas y mete datos de ejemplo.

## 4. Como arrancarla

Ejecuta:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Despues abre la documentacion interactiva de FastAPI en:

- `/docs`
- `/redoc`

## 5. Credenciales de prueba

### Administrador principal del sistema

- Correo: `owner@dojoflow.com`
- Password: `admin123`

Este usuario tiene acceso al panel admin y a varios endpoints protegidos.

### Dojo de ejemplo

- Correo: `dojo_1@dojoflow.local`
- Password: `dojo1234`

Este usuario sirve para probar el flujo normal del dojo.

## 6. Que datos trae el seed

El seed inicial crea:

- El usuario admin principal.
- El usuario demo del dojo.
- Los planes.
- El perfil de academia.
- Los instructores demo.
- Los horarios demo.
- Los cupones demo.
- Productos demo del marketplace.

Importante: no crea un alumno de prueba fijo. Para probar el portal de alumno debes crear uno.

## 7. Flujo de autenticacion

### Login

Endpoint:

- `POST /api/v1/auth/login`

El frontend manda usuario y contraseña.

La API responde con:

- `access_token`
- `account_type`
- `student_id` cuando aplica

### Que hace la API con la sesion

- Genera un JWT.
- El frontend lo guarda en `localStorage` como `dojo_token`.
- Si el usuario existe tambien como alumno, la cuenta se marca como `student`.
- Si no, se marca como `staff`.

### Recuperar contraseña

- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`

### Cambiar contraseña

- `POST /api/v1/auth/change-password`

## 8. Roles reales del sistema

### Admin global

- Solo `owner@dojoflow.com`.
- Puede entrar a `/api/v1/admin/*`.
- Puede ver ordenes, usuarios e ingresos.

### Staff / dojo owner

- Accede al panel operativo.
- Trabaja con alumnos, pagos, horarios, reportes y configuracion.

### Alumno

- Entra al portal de alumno.
- Ve sus pagos.
- Paga mensualidades.
- Cambia su contraseña.

## 9. Flujo completo de negocio

### A. Creacion de una orden de dojo

El cliente publica el formulario en el frontend.

Endpoint:

- `POST /api/v1/orders`

La API:

- Valida que el plan exista.
- Crea la orden en estado `pending`.
- Guarda nombre del dojo, dueño, correo, ciudad, zona horaria y moneda.

### B. Pago de la orden

Para pruebas existe:

- `POST /api/v1/orders/{order_id}/checkout`
- `POST /api/v1/orders/{order_id}/confirm-payment`

En demo, `confirm-payment` simula el pago.

Cuando la orden queda pagada, la API:

- Marca la orden como `paid`.
- Genera credenciales de acceso.
- Crea un usuario nuevo con email tipo `dojo_{id}@dojoflow.local`.

### C. Acceso al panel del dojo

Con el usuario del dojo ya creado, el staff entra al frontend y usa `/app`.

### D. Alta de alumno

Endpoint:

- `POST /api/v1/students`

La API:

- Crea el alumno.
- Genera una contraseña temporal.
- Crea el usuario si no existia.
- Intenta enviar correo con las credenciales.
- Si el correo falla, la respuesta indica si se envio o no.

### E. Login de alumno

Cuando el alumno existe, puede entrar con su correo y contraseña.

### F. Pago de mensualidad

Endpoint principal:

- `POST /api/v1/payments/checkout/paypal/me`

La API crea el checkout de PayPal y luego valida la respuesta con:

- `POST /api/v1/payments/paypal/verify`

### G. Contratacion de plan SaaS

Endpoint:

- `POST /api/v1/plans/{plan_id}/checkout/paypal`

Verificacion:

- `POST /api/v1/plans/checkout/paypal/verify`

## 10. Mapa simple de endpoints

### Auth

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`
- `POST /api/v1/auth/change-password`

### Orders

- `POST /api/v1/orders`
- `POST /api/v1/orders/{order_id}/checkout`
- `POST /api/v1/orders/{order_id}/confirm-payment`
- `GET /api/v1/orders/{order_id}`
- `GET /api/v1/orders/status/{email}`
- `GET /api/v1/orders`

### Students

- `GET /api/v1/students`
- `POST /api/v1/students`
- `GET /api/v1/students/me`

### Payments

- `GET /api/v1/payments`
- `POST /api/v1/payments`
- `POST /api/v1/payments/checkout/paypal`
- `POST /api/v1/payments/checkout/paypal/me`
- `POST /api/v1/payments/paypal/verify`

### Plans

- `GET /api/v1/plans`
- `POST /api/v1/plans/{plan_id}/checkout/paypal`
- `POST /api/v1/plans/checkout/paypal/verify`

### Dashboard y reportes

- `GET /api/v1/dashboard/kpis`
- `GET /api/v1/reports/summary`
- `GET /api/v1/reports/attendance-trend`
- `GET /api/v1/reports/revenue-breakdown`
- `GET /api/v1/reports/top-students`

### Academia y operacion

- `GET /api/v1/academy-profile`
- `PATCH /api/v1/academy-profile`
- `GET /api/v1/teachers`
- `POST /api/v1/teachers`
- `GET /api/v1/schedules`
- `POST /api/v1/schedules`
- `GET /api/v1/coupons`
- `POST /api/v1/coupons`
- `GET /api/v1/marketplace`
- `POST /api/v1/marketplace`
- `GET /api/v1/belts`
- `POST /api/v1/belts`
- `GET /api/v1/attendance`
- `POST /api/v1/attendance`

### Admin global

- `GET /api/v1/admin/dashboard`
- `GET /api/v1/admin/orders`
- `GET /api/v1/admin/orders/{id}`
- `PATCH /api/v1/admin/orders/{id}/status`
- `GET /api/v1/admin/users`
- `GET /api/v1/admin/users/{id}`
- `PATCH /api/v1/admin/users/{id}/toggle-active`
- `GET /api/v1/admin/plans`
- `GET /api/v1/admin/revenue-report`

## 11. Variables importantes de entorno

### Generales

- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `FRONTEND_BASE_URL`
- `CORS_ORIGINS`

### Base de datos

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DB`
- `DATABASE_URL`

### PayPal

- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_BASE_URL`
- `PAYPAL_SUCCESS_URL`
- `PAYPAL_CANCEL_URL`
- `PAYPAL_PLAN_SUCCESS_URL`
- `PAYPAL_PLAN_CANCEL_URL`

### Correo

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_FROM_EMAIL`

## 12. PayPal en modo prueba

Por defecto la API apunta a:

- `https://api-m.sandbox.paypal.com`

Si no hay credenciales de PayPal configuradas, los endpoints de checkout devolveran error de configuracion.

## 13. Correo de credenciales

La API puede enviar correos para:

- Credenciales de nuevos alumnos.
- Recuperacion de contrasena.

Si SMTP no esta configurado, el envio falla, pero el flujo general puede seguirse en desarrollo.

## 14. Cosas que debes entender para no perderte

- El frontend no autentica por si solo; solo usa el token que da la API.
- El admin global no es un rol generico; es un correo fijo.
- Los alumnos no aparecen solos: primero debes crearlos.
- Los pagos de PayPal y las ordenes de plan usan verificacion posterior.
- El seed se puede volver a correr sin romper datos existentes porque evita duplicados basicos.

## 15. Orden recomendado para probar todo sin fallar

1. Configura el `.env`.
2. Instala dependencias.
3. Ejecuta `python -m app.init_db`.
4. Arranca la API con Uvicorn.
5. Arranca el frontend.
6. Entra como `owner@dojoflow.com` / `admin123`.
7. Revisa `/admin`.
8. Entra a `/app`.
9. Crea un alumno.
10. Entra al portal de alumno y prueba un pago.

## 16. Problemas tipicos

### No conecta el frontend

Revisa que la API este arriba y que `VITE_API_BASE_URL` apunte al puerto correcto.

### Login falla

Revisa el correo, la contrasena y que la base de datos tenga el seed cargado.

### PayPal falla

Revisa credenciales de sandbox y variables de retorno.

### El alumno no puede entrar

Revisa que el alumno exista en la tabla de alumnos y que tenga un usuario asociado.

### No llegan correos

Revisa SMTP, especialmente Gmail con app password y 2FA.
