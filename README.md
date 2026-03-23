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
- `GET /api/v1/plans` - Planes SaaS disponibles

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
