# 🎯 DojoFlow - Guía Completa de Roles y Acceso

## 📋 Resumen

DojoFlow tiene **dos tipos de usuarios con acceso diferenciado**:

| Usuario | Email | Rol | Acceso |
|---------|--------|-----|--------|
| **Admin (Ustedes)** | `owner@dojoflow.com` | Sistema Owner | Dashboard admin, todas las órdenes, todos los usuarios |
| **Dojo Owner (Clientes)** | `dojo_N@dojoflow.local` | Plan Owner | Solo su academia, sus estudiantes, sus horarios |

---

## 🔐 Autenticación

### 1. Login Admin
```bash
POST /api/v1/auth/login
{
  "email": "owner@dojoflow.com",
  "password": "admin123"  # Default admin password (change in production!)
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 2. Login Dojo Owner (Post-Purchase)
```bash
POST /api/v1/auth/login
{
  "email": "dojo_1@dojoflow.local",
  "password": "Aj$9mK2xL@pZ1"  # Generated after payment
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## 👨‍💼 ADMIN ENDPOINTS (owner@dojoflow.com)

### Dashboard Statistics
```bash
GET /api/v1/admin/dashboard
Authorization: Bearer {admin_token}

Response:
{
  "orders": {
    "total": 15,
    "pending": 3,
    "paid": 10,
    "completed": 2
  },
  "users": {
    "total": 50,
    "active": 48
  },
  "revenue": {
    "total": 8700,
    "currency": "MXN"
  }
}
```

### View All Orders
```bash
GET /api/v1/admin/orders
GET /api/v1/admin/orders?status=pending  # Filter by status
Authorization: Bearer {admin_token}

Response:
[
  {
    "id": 1,
    "plan_id": 2,
    "dojo_name": "Karate Do México",
    "owner_name": "Juan Pérez",
    "owner_email": "juan@academia.com",
    "city": "CDMX",
    "amount": 520,
    "status": "paid",
    "generated_email": "dojo_1@dojoflow.local",
    "created_at": "2026-03-22T10:30:00"
  },
  ...
]
```

### View Order Details
```bash
GET /api/v1/admin/orders/{order_id}
Authorization: Bearer {admin_token}

Response:
{
  "id": 1,
  "plan_id": 2,
  "dojo_name": "Karate Do México",
  "owner_name": "Juan Pérez",
  "owner_email": "juan@academia.com",
  "owner_phone": "+52 5512345678",
  "city": "CDMX",
  "timezone": "America/Mexico_City",
  "currency": "MXN",
  "amount": 520,
  "status": "paid",
  "payment_method": "stripe",
  "transaction_id": "txn_mock_1_1711187400",
  "paid_at": "2026-03-22T11:00:00",
  "generated_email": "dojo_1@dojoflow.local",
  "generated_password": "Aj$9mK2xL@pZ1",
  "credentials_sent_at": "2026-03-22T11:00:00",
  "created_at": "2026-03-22T10:30:00",
  "updated_at": "2026-03-22T11:00:00"
}
```

### Update Order Status
```bash
PATCH /api/v1/admin/orders/{order_id}/status
Authorization: Bearer {admin_token}

Body:
{
  "new_status": "completed"  # pending, paid, completed, cancelled
}

Response:
{
  "id": 1,
  "status": "completed",
  "message": "Order status updated"
}
```

### List All Users
```bash
GET /api/v1/admin/users
Authorization: Bearer {admin_token}

Response:
[
  {
    "id": 1,
    "email": "owner@dojoflow.com",
    "full_name": "Admin User",
    "is_active": true,
    "created_at": "2026-03-22T10:00:00"
  },
  {
    "id": 2,
    "email": "dojo_1@dojoflow.local",
    "full_name": "Juan Pérez",
    "is_active": true,
    "created_at": "2026-03-22T11:00:00"
  },
  ...
]
```

### View User Details
```bash
GET /api/v1/admin/users/{user_id}
Authorization: Bearer {admin_token}

Response:
{
  "id": 2,
  "email": "dojo_1@dojoflow.local",
  "full_name": "Juan Pérez",
  "is_active": true,
  "created_at": "2026-03-22T11:00:00",
  "associated_order": {
    "id": 1,
    "dojo_name": "Karate Do México",
    "owner_email": "juan@academia.com",
    "status": "paid",
    "amount": 520
  }
}
```

### Activate/Deactivate User
```bash
PATCH /api/v1/admin/users/{user_id}/toggle-active
Authorization: Bearer {admin_token}

Response:
{
  "id": 2,
  "email": "dojo_1@dojoflow.local",
  "is_active": false,
  "message": "User deactivated"
}
```

### View All Plans
```bash
GET /api/v1/admin/plans
Authorization: Bearer {admin_token}

Response:
[
  {
    "id": 1,
    "name": "Plan Blanco",
    "monthly_price": 0,
    "description": "Plan básico gratuito"
  },
  {
    "id": 2,
    "name": "Plan Negro",
    "monthly_price": 520,
    "description": "Plan profesional"
  },
  {
    "id": 3,
    "name": "Plan Maestro",
    "monthly_price": 870,
    "description": "Plan premium"
  }
]
```

### Revenue Report by Plan
```bash
GET /api/v1/admin/revenue-report
Authorization: Bearer {admin_token}

Response:
{
  "Plan Blanco": {
    "count": 5,
    "monthly_price": 0,
    "total_revenue": 0,
    "orders": [10, 11, 12, 13, 14]
  },
  "Plan Negro": {
    "count": 8,
    "monthly_price": 520,
    "total_revenue": 4160,
    "orders": [1, 2, 3, 4, 5, 6, 7, 8]
  },
  "Plan Maestro": {
    "count": 2,
    "monthly_price": 870,
    "total_revenue": 1740,
    "orders": [9, 15]
  }
}
```

---

## 🏫 DOJO OWNER ENDPOINTS (dojo_N@dojoflow.local)

### Get My Dojo Info
```bash
GET /api/v1/dojo/me
Authorization: Bearer {dojo_owner_token}

Response:
{
  "academy": {
    "id": 1,
    "dojo_name": "Karate Do México",
    "owner_name": "Juan Pérez",
    "contact_email": "dojo_1@dojoflow.local",
    "contact_phone": "+52 5512345678",
    "city": "CDMX",
    "timezone": "America/Mexico_City"
  },
  "subscription": {
    "order_id": 1,
    "plan_id": 2,
    "status": "paid",
    "amount": 520,
    "joined_date": "2026-03-22T11:00:00"
  },
  "user": {
    "email": "dojo_1@dojoflow.local",
    "name": "Juan Pérez",
    "active": true
  }
}
```

### Get My Students
```bash
GET /api/v1/dojo/students
Authorization: Bearer {dojo_owner_token}

Response:
[
  {
    "id": 1,
    "name": "Carlos López",
    "email": "carlos@example.com",
    "phone": "+52 5512345671",
    "belt_level": "White",
    "status": "active",
    "created_at": "2026-03-22T12:00:00"
  },
  {
    "id": 2,
    "name": "María García",
    "email": "maria@example.com",
    "phone": "+52 5512345672",
    "belt_level": "Blue",
    "status": "active",
    "created_at": "2026-03-21T14:30:00"
  }
]
```

### Get My Teachers
```bash
GET /api/v1/dojo/teachers
Authorization: Bearer {dojo_owner_token}

Response:
[
  {
    "id": 1,
    "name": "Sensei Takeshi",
    "email": "takeshi@academia.com",
    "phone": "+52 5587654321",
    "specialties": "Karate",
    "hourly_rate": 250,
    "active": true
  }
]
```

### Get My Class Schedules
```bash
GET /api/v1/dojo/schedules
Authorization: Bearer {dojo_owner_token}

Response:
[
  {
    "id": 1,
    "class_type": "Karate",
    "day_of_week": 1,  # 0=Monday, 6=Sunday
    "start_time": "18:00:00",
    "end_time": "19:30:00",
    "teacher_id": 1,
    "max_students": 20,
    "active": true
  },
  {
    "id": 2,
    "class_type": "Karate",
    "day_of_week": 3,
    "start_time": "18:00:00",
    "end_time": "19:30:00",
    "teacher_id": 1,
    "max_students": 20,
    "active": true
  }
]
```

### Get My Stats
```bash
GET /api/v1/dojo/stats
Authorization: Bearer {dojo_owner_token}

Response:
{
  "academy": "Karate Do México",
  "students": {
    "total": 45,
    "active": 43
  },
  "teachers": {
    "total": 3
  },
  "classes": {
    "total": 6
  }
}
```

### Update My Profile
```bash
PATCH /api/v1/dojo/profile
Authorization: Bearer {dojo_owner_token}

Body:
{
  "contact_phone": "+52 5599999999",
  "city": "Guadalajara",
  "timezone": "America/Mexico_City"
}

Response:
{
  "message": "Profile updated successfully",
  "academy": {
    "dojo_name": "Karate Do México",
    "contact_phone": "+52 5599999999",
    "city": "Guadalajara",
    "timezone": "America/Mexico_City"
  }
}
```

---

## 🛒 PUBLIC ENDPOINTS (No Authentication Required)

### Get Available Plans
```bash
GET /api/v1/plans

Response:
[
  {
    "id": 1,
    "name": "Plan Blanco",
    "monthly_price": 0,
    "description": "Plan básico"
  },
  {
    "id": 2,
    "name": "Plan Negro",
    "monthly_price": 520,
    "description": "Plan profesional"
  },
  {
    "id": 3,
    "name": "Plan Maestro",
    "monthly_price": 870,
    "description": "Plan premium"
  }
]
```

### Create Order (Purchase)
```bash
POST /api/v1/orders

Body:
{
  "plan_id": 2,
  "dojo_name": "Mi Academia de Karate",
  "owner_name": "Juan Pérez",
  "owner_email": "juan@example.com",
  "owner_phone": "+52 5512345678",
  "city": "CDMX",
  "timezone": "America/Mexico_City",
  "currency": "MXN"
}

Response:
{
  "id": 1,
  "plan_id": 2,
  "dojo_name": "Mi Academia de Karate",
  "owner_name": "Juan Pérez",
  "owner_email": "juan@example.com",
  "amount": 520,
  "status": "pending",
  "created_at": "2026-03-22T10:30:00"
}
```

### Simulate Checkout
```bash
POST /api/v1/orders/{order_id}/checkout

Response:
{
  "order_id": 1,
  "checkout_url": "https://stripe-mock.example.com/checkout/1?session_id=cs_mock_1",
  "message": "To complete payment in production, use Stripe checkout. For testing, call /orders/{order_id}/confirm-payment"
}
```

### Confirm Payment (Demo/Testing)
```bash
POST /api/v1/orders/{order_id}/confirm-payment

Response:
{
  "id": 1,
  "plan_id": 2,
  "dojo_name": "Mi Academia de Karate",
  "owner_name": "Juan Pérez",
  "owner_email": "juan@example.com",
  "amount": 520,
  "status": "paid",
  "generated_email": "dojo_1@dojoflow.local",
  "generated_password": "Aj$9mK2xL@pZ1",
  "paid_at": "2026-03-22T11:00:00",
  "message": "✅ Orden pagada. Credenciales generadas."
}
```

### Track Order by ID
```bash
GET /api/v1/orders/{order_id}

Response:
{
  "id": 1,
  "dojo_name": "Mi Academia",
  "owner_email": "juan@example.com",
  "amount": 520,
  "status": "paid"
}
```

### Track Order by Email
```bash
GET /api/v1/orders/status/{email}

Response:
{
  "id": 1,
  "dojo_name": "Mi Academia",
  "owner_email": "juan@example.com",
  "status": "paid"
}
```

---

## 🔄 Flujo de Uso Completo

### Parte 1: Cliente Compra (Public)
```
1. Cliente en landing ve 3 planes
2. Click "Comienza ahora"
3. POST /api/v1/orders ← Crea orden (PENDING)
4. POST /api/v1/orders/{id}/checkout ← Obtiene URL Stripe
5. Cliente paga en Stripe (o demo: POST /api/v1/orders/{id}/confirm-payment)
6. Orden estado: PAID
7. Email generado: dojo_1@dojoflow.local
8. Password generado automáticamente
9. Usuario creado en BD
```

### Parte 2: Admin Gestiona (Admin Only)
```
1. Admin login: POST /api/v1/auth/login (owner@dojoflow.com)
2. GET /api/v1/admin/dashboard ← Ver estadísticas
3. GET /api/v1/admin/orders ← Listar todas órdenes
4. GET /api/v1/admin/revenue-report ← Ver ingresos
5. PATCH /api/v1/admin/orders/{id}/status ← Cambiar estado orden
6. GET /api/v1/admin/users ← Ver todos usuarios
```

### Parte 3: Dojo Owner Gestiona Su Academia (Dojo Only)
```
1. Dojo owner login: POST /api/v1/auth/login (dojo_1@dojoflow.local)
2. GET /api/v1/dojo/me ← Ver su perfil
3. GET /api/v1/dojo/students ← Ver sus estudiantes
4. GET /api/v1/dojo/teachers ← Ver sus instructores
5. GET /api/v1/dojo/schedules ← Ver horarios de clases
6. GET /api/v1/dojo/stats ← Ver estadísticas de su academia
7. PATCH /api/v1/dojo/profile ← Actualizar datos de su academia
```

---

## 🛡️ Árboles de Control de Acceso

### Admin Access Control
- `GET /api/v1/admin/*` - ✅ Solo admin
- `PATCH /api/v1/admin/*` - ✅ Solo admin
- Verifica: `current_user.email == "owner@dojoflow.com"`
- Si falla: HTTP 403 Forbidden

### Dojo Owner Access Control
- `GET /api/v1/dojo/*` - ✅ Solo usuarios con orden PAID
- Verifica: Usuario tiene Order con status=PAID o COMPLETED
- Si falla: HTTP 403 Forbidden
- Cada dojo solo ve sus propios datos (filtrado por academy_id)

### Public Access Control
- `/api/v1/orders` (POST) - ✅ Sin autenticación
- `/api/v1/plans` (GET) - ✅ Sin autenticación
- Cualquier otra ruta protegida requiere Bearer token válido

---

## 🧪 Testing Completo

### Test 1: Admin Dashboard
```bash
# 1. Login como admin
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@dojoflow.com","password":"admin123"}' \
  | jq -r '.access_token')

# 2. Ver dashboard
curl http://localhost:8000/api/v1/admin/dashboard \
  -H "Authorization: Bearer $TOKEN"

# 3. Ver órdenes
curl http://localhost:8000/api/v1/admin/orders \
  -H "Authorization: Bearer $TOKEN"

# 4. Ver ingresos
curl http://localhost:8000/api/v1/admin/revenue-report \
  -H "Authorization: Bearer $TOKEN"
```

### Test 2: Dojo Owner Management
```bash
# 1. Login como dojo owner
DOJO_TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"dojo_1@dojoflow.local","password":"Aj$9mK2xL@pZ1"}' \
  | jq -r '.access_token')

# 2. Ver mi información
curl http://localhost:8000/api/v1/dojo/me \
  -H "Authorization: Bearer $DOJO_TOKEN"

# 3. Ver mis estudiantes
curl http://localhost:8000/api/v1/dojo/students \
  -H "Authorization: Bearer $DOJO_TOKEN"

# 4. Ver estadísticas
curl http://localhost:8000/api/v1/dojo/stats \
  -H "Authorization: Bearer $DOJO_TOKEN"
```

---

**Documentación Generada:** Marzo 22, 2026  
**Versión API:** 1.0
