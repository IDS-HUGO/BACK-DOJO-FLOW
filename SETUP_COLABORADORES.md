# 🚀 DojoFlow API - Guía de Setup para Colaboradores

## Estado Actual
✅ **Backend completamente funcional** con flujo de órdenes/checkout implementado
- 6 endpoints de orden (create, checkout, confirm-payment, list, get, get-by-email)
- Generación automática de credenciales tras pago
- Base de datos MySQL con tabla `orders`
- Documentación Swagger en `/docs`

---

## 🔧 Requisitos

- **Python 3.10+**
- **MySQL 8.0+** (local o cloud)
- **Git**
- **pip** (gestor de paquetes Python)

---

## 📦 Instalación Rápida

### 1. Clonar Repositorio
```bash
git clone https://github.com/IDS-HUGO/BACK-DOJO-FLOW.git
cd BACK-DOJO-FLOW
git checkout hugo  # Rama principal de colaboración
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar `.env`
Crea archivo `.env` en raíz:
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DB=dojoflow

SECRET_KEY=change_this_secret_in_production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:5173,http://localhost:5174

APP_NAME=DojoFlow API
```

### 5. Inicializar BD
```bash
python -m app.init_db
```

### 6. Correr API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📍 Endpoints Implementados

### Health Check
```bash
GET /health
Response: {"status": "ok", "service": "DojoFlow API"}
```

### Autenticación
```bash
POST /api/v1/auth/login
- Email: owner@dojoflow.com
- Password: admin123 (creado en init_db.py)
Response: {"access_token": "jwt_token...", "token_type": "bearer"}
```

### Órdenes (NEW)
```bash
# Crear orden de compra
POST /api/v1/orders
Body: {
  "plan_id": 1,
  "dojo_name": "Mi Academia",
  "owner_name": "Juan Pérez",
  "owner_email": "juan@example.com",
  "owner_phone": "+52 5512345678",
  "city": "CDMX",
  "timezone": "America/Mexico_City",
  "currency": "MXN"
}

# Obtener mock checkout (Stripe en producción)
POST /api/v1/orders/{order_id}/checkout

# Confirmar pago y generar credenciales
POST /api/v1/orders/{order_id}/confirm-payment

# Listar órdenes (admin only)
GET /api/v1/orders
Headers: Authorization: Bearer {token}

# Obtener orden por ID
GET /api/v1/orders/{order_id}

# Rastrear orden por email
GET /api/v1/orders/status/{email}
```

### Planes
```bash
GET /api/v1/plans
Response: [
  {"id": 1, "name": "Plan Blanco", "monthly_price": 0},
  {"id": 2, "name": "Plan Negro", "monthly_price": 520},
  {"id": 3, "name": "Plan Maestro", "monthly_price": 870}
]
```

---

## 🔍 Testing Endpoints

### Opción 1: Swagger UI (Recomendado)
```
http://localhost:8000/docs
```
Interfaz interactiva para probar todos los endpoints.

### Opción 2: PowerShell/CMD
```powershell
# Health check
$response = Invoke-RestMethod -Uri "http://localhost:8000/health"
$response

# Crear orden
$body = @{
    plan_id = 2
    dojo_name = "Karate Do"
    owner_name = "Ana López"
    owner_email = "ana@example.com"
    owner_phone = "+52 5587654321"
    city = "Monterrey"
    timezone = "America/Mexico_City"
    currency = "MXN"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/orders" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

$response | ConvertTo-Json
```

### Opción 3: MySQL Query
```sql
-- Ver órdenes creadas
SELECT * FROM orders;

-- Ver usuarios con credenciales generadas
SELECT email, is_active FROM users WHERE email LIKE 'dojo_%';

-- Ver planes disponibles
SELECT * FROM plans;
```

---

## 📊 Modelos de Datos

### Tabla `orders` (NEW)
```
id (PK)
plan_id (FK -> plans)
dojo_name
owner_name
owner_email (UNIQUE)
owner_phone
city
timezone
currency
amount
status (pending/paid/completed/cancelled)
payment_method
transaction_id
paid_at
generated_email
generated_password
credentials_sent_at
created_at
updated_at
```

### Tabla `plans`
```
id (PK)
name (Blanco, Negro, Maestro)
monthly_price
description
transaction_fee_percent
```

### Tabla `users`
```
id (PK)
email (UNIQUE)
full_name
hashed_password
is_active
created_at
updated_at
```

---

## 🔄 Flujo de Checkout

```
1. Frontend: POST /orders
   ↓
2. Backend: Crear orden (status=PENDING)
   ↓
3. Frontend: POST /orders/{id}/checkout (obtiene session_id)
   ↓
4. Frontend: Redirige a checkout (Stripe)
   ↓
5. Usuario: Completa pago en Stripe
   ↓
6. Backend: Webhook Stripe (en producción) o manual confirm-payment
   ↓
7. Backend: POST /orders/{id}/confirm-payment
   - Cambiar status → PAID
   - Generar email temporal (dojo_{id}@dojoflow.local)
   - Generar password aleatoria
   - Crear User con credenciales
   ↓
8. Frontend: Mostrar credenciales al usuario
```

---

## 📝 Estructura de Carpetas

```
app/
├── models/
│   ├── __init__.py
│   ├── base.py          # Base mixins (TimestampMixin)
│   ├── user.py          # Usuario/Dojo owner
│   ├── plan.py          # Planes SaaS
│   ├── order.py         # ← NEW: Órdenes de compra
│   ├── student.py       # Estudiantes
│   ├── schedule.py      # Horarios de clase
│   ├── teacher.py       # Instructores
│   ├── attendance.py    # Asistencias
│   ├── payment.py       # Pagos estudiantes
│   ├── belt_progress.py # Cinturones/grados
│   ├── coupon.py        # Cupones descuento
│   ├── marketplace_item.py # Productos
│   └── academy_profile.py  # Perfil dojo
│
├── schemas/             # Pydantic validators
│   ├── __init__.py
│   ├── user.py
│   ├── plan.py
│   ├── order.py         # ← NEW: Schemas orden
│   └── ...
│
├── api/
│   ├── __init__.py
│   ├── router.py        # Router principal
│   └── routes/
│       ├── __init__.py
│       ├── auth.py      # Login/Register
│       ├── orders.py    # ← NEW: Order CRUD
│       ├── plans.py
│       ├── students.py
│       ├── teachers.py
│       ├── schedules.py
│       ├── attendance.py
│       ├── payments.py
│       ├── belts.py
│       ├── dashboard.py
│       ├── marketplace.py
│       ├── academy_profile.py
│       ├── reports.py
│       └── coupons.py
│
├── db/
│   ├── __init__.py
│   ├── session.py       # Configuración SQLAlchemy
│   └── base.py          # Imports de modelos
│
├── core/
│   ├── __init__.py
│   ├── config.py        # Variables de entorno
│   └── security.py      # JWT, Hashing
│
├── main.py              # Aplicación FastAPI
└── init_db.py           # Script inicialización BD
```

---

## 🚦 Status Códigos HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Operación exitosa |
| 201 | CREATED - Recurso creado |
| 400 | BAD REQUEST - Datos inválidos |
| 401 | UNAUTHORIZED - No autenticado |
| 403 | FORBIDDEN - Sin permisos |
| 404 | NOT FOUND - Recurso no existe |
| 500 | SERVER ERROR - Error interno |

---

## 🔐 Seguridad

### Variables de Entorno Sensibles
NUNCA commits credenciales. Usa `.env`:
```
SECRET_KEY=random_very_long_string_here
MYSQL_PASSWORD=secure_password
```

### JWT Tokens
- Expiran en 1440 minutos (24 horas)
- Se envían en header: `Authorization: Bearer {token}`
- Generados en `/api/v1/auth/login`

### CORS
Por defecto acepta requests desde:
- `http://localhost:5173`
- `http://localhost:5174`
- Configurable en `.env` CORS_ORIGINS

---

## 📝 Developing

### Crear Nuevo Endpoint

1. **Crear Schema** en `app/schemas/nuevo.py`:
```python
from pydantic import BaseModel

class NuevoCreate(BaseModel):
    campo1: str
    campo2: int
```

2. **Crear Route** en `app/api/routes/nuevo.py`:
```python
from fastapi import APIRouter, Depends
from app.schemas.nuevo import NuevoCreate

router = APIRouter(prefix="/nuevo", tags=["nuevo"])

@router.post("/")
def create_nuevo(data: NuevoCreate, db: Session = Depends(get_db)):
    # Lógica aquí
    return {"id": 1, "campo1": data.campo1}
```

3. **Registrar Route** en `app/api/router.py`:
```python
from app.api.routes import nuevo

api_router.include_router(nuevo.router)
```

4. **Reinicia uvicorn** - Los cambios se replican automáticamente con `--reload`

---

## 🐛 Debugging

### Logs Detallados
```bash
# Activar SQL queries logging
# En app/core/config.py descomentar:
# SQLALCHEMY_ECHO = True

uvicorn app.main:app --reload --log-level debug
```

### Verificar BD

```bash
mysql -h localhost -u root -p dojoflow

# Ver tablas
SHOW TABLES;

# Ver estructura orders
DESCRIBE orders;

# Ver órdenes creadas
SELECT id, plan_id, owner_email, status FROM orders;

# Ver usuarios generados
SELECT id, email FROM users WHERE email LIKE 'dojo_%';
```

---

## 📦 Dependencias Principales

```
fastapi==0.115.12          # Framework web
uvicorn[standard]==0.34.0  # Servidor ASGI
SQLAlchemy==2.0.39         # ORM
pymysql==1.1.1             # Driver MySQL
pydantic==2.11.1           # Validación datos
python-jose[cryptography]  # JWT
bcrypt==4.0.1              # Hashing
passlib[bcrypt]==1.7.4     # Password hashing
```

---

## 🚀 Deploy

Consulta **DATABASE_DEPLOYMENT.md** para:
- Deploying con PostgreSQL
- AWS RDS setup
- Heroku/Vercel
- Docker containers
- Backups y disaster recovery

---

**Última actualización:** Marzo 22, 2026  
**Rama de colaboración:** `hugo`
