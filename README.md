# DojoFlow API (FastAPI + MySQL)

API backend para operación SaaS de academias de artes marciales, separada del frontend y lista para entorno local/profesional.

## Ubicación del proyecto

- API: `D:/UNIVERSIDAD/ANALISIS FINANCIERO/Dojo-Flow-API`
- Frontend (separado): `D:/UNIVERSIDAD/ANALISIS FINANCIERO/Dojo-Flow`

## Stack

- FastAPI
- SQLAlchemy
- MySQL (PyMySQL)
- JWT (python-jose)

## Requisitos

- Python 3.11+
- MySQL 8+

## Configuración

1. Copia `.env.example` a `.env`.
2. Crea la base de datos MySQL definida en `MYSQL_DB`.
3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Inicializa tablas y seed:

```bash
python -m app.init_db
```

5. Ejecuta API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Comandos rapidos (API)

```bash
# Ubicarse en el proyecto
cd D:/UNIVERSIDAD/ANALISIS FINANCIERO/Dojo-Flow-API

# Instalar dependencias
pip install -r requirements.txt

# Crear/actualizar tablas y seed de datos
python -m app.init_db

# Levantar API en local
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Verificacion rapida de sintaxis de modulos
python -m compileall app
```

## Comandos rapidos (frontend + API)

Terminal 1 (API):

```bash
cd D:/UNIVERSIDAD/ANALISIS FINANCIERO/Dojo-Flow-API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (frontend):

```bash
cd D:/UNIVERSIDAD/ANALISIS FINANCIERO/Dojo-Flow
npm install
npm run dev
```

Chequeos funcionales recomendados:

1. Crear alumno y validar envio de credenciales.
2. Iniciar sesion staff y revisar modulos (students, attendance, schedules, marketplace, reports).
3. Iniciar sesion alumno y pagar desde portal /student.
4. Contratar plan desde /app/plans y confirmar estado en retorno de PayPal.

## Usuario inicial

- Usuario: `owner@dojoflow.com`
- Contraseña: `admin123`

## Endpoints principales

### Autenticación
- `POST /api/v1/auth/login` - Inicio de sesión

### Estudiantes y Asistencia
- `GET/POST /api/v1/students` - Gestión de alumnos
- `GET/POST /api/v1/attendance` - Registro de asistencia
- `GET/POST /api/v1/belts` - Seguimiento de exámenes y grados

### Finanzas
- `GET/POST /api/v1/payments` - Registro de pagos
- `POST /api/v1/payments/checkout/paypal` - Crear checkout online de alumnos
- `POST /api/v1/payments/paypal/verify` - Verificar/capturar pago de alumnos
- `GET /api/v1/plans` - Planes SaaS disponibles
- `POST /api/v1/plans/{plan_id}/checkout/paypal` - Checkout de suscripcion DojoFlow
- `POST /api/v1/plans/checkout/paypal/verify` - Verificar/capturar pago de suscripcion

## PayPal Sandbox (rapido, sin verificar empresa para pruebas)

Configura estas variables en `.env`:

- `PAYPAL_CLIENT_ID`
- `PAYPAL_CLIENT_SECRET`
- `PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com`
- `PAYPAL_SUCCESS_URL`
- `PAYPAL_CANCEL_URL`
- `PAYPAL_PLAN_SUCCESS_URL`
- `PAYPAL_PLAN_CANCEL_URL`

Con esto, la pantalla de pagos redirige al checkout de PayPal y al regresar valida/captura el pago en la API.

Pasos rapidos para obtener credenciales Sandbox:

1. Entra a https://developer.paypal.com y crea cuenta (personal sirve para entorno sandbox).
2. Ve a `Apps & Credentials`.
3. En `Sandbox`, crea una app nueva.
4. Copia `Client ID` y `Secret`.
5. Pegalos en `.env` como `PAYPAL_CLIENT_ID` y `PAYPAL_CLIENT_SECRET`.

## PayPal Live (cuando ya se despliegue)

- Cambia `PAYPAL_BASE_URL` a `https://api-m.paypal.com`.
- Usa las credenciales Live de la misma app en `Apps & Credentials`.
- Sustituye las URLs `localhost` por el dominio real de tu despliegue.

## Portal de alumnos + credenciales por Gmail

- Al crear un alumno en `POST /api/v1/students`, la API crea también su usuario de acceso.
- Se genera contraseña temporal y se envía por Gmail al correo del alumno.
- Si SMTP falla, la respuesta incluye `fallback_temporary_password` para compartirla manualmente.

Variables SMTP requeridas en `.env`:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD` (app password de Gmail)
- `SMTP_FROM_EMAIL` (opcional)

Notas para Gmail de Google:

- Usa `SMTP_HOST=smtp.gmail.com` y `SMTP_PORT=587`.
- Configura 2FA en la cuenta y genera un **App Password** para `SMTP_PASSWORD`.
- No uses contraseña normal de Gmail en producción.
- El sistema hace reintento automático de envío para mitigar fallos transitorios.

Recuperación y cambio de contraseña (automatizado):

- `POST /api/v1/auth/forgot-password` envía enlace por correo.
- `POST /api/v1/auth/reset-password` actualiza contraseña usando token temporal.
- `POST /api/v1/auth/change-password` permite cambio autenticado desde el portal.

Variables relacionadas:

- `FRONTEND_BASE_URL` (para construir el enlace de recuperación)
- `RESET_PASSWORD_EXPIRE_MINUTES`

### Operaciones
- `GET/POST /api/v1/teachers` - Gestión de instructores
- `GET/POST /api/v1/schedules` - Horarios de clases
- `GET/POST /api/v1/coupons` - Cupones y descuentos
- `GET/POST /api/v1/marketplace` - Catálogo de productos

### Análisis y Configuración
- `GET /api/v1/dashboard/kpis` - KPIs de la academia
- `GET /api/v1/dashboard/mrr-trend` - Tendencia de ingresos recurrentes
- `GET /api/v1/reports/summary` - Resumen de reportes
- `GET /api/v1/reports/attendance-trend` - Tendencia de asistencia
- `GET /api/v1/reports/revenue-breakdown` - Desglose de ingresos
- `GET /api/v1/reports/top-students` - Top estudiantes por asistencia
- `GET/PUT /api/v1/academy-profile` - Configuración de academia
