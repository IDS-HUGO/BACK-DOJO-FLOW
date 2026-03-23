# DojoFlow - Especificación de Base de Datos para Despliegue

## 1. Resumen Ejecutivo

DojoFlow utiliza SQLAlchemy ORM con soporte para múltiples bases de datos. Para despliegue en producción, se recomienda **PostgreSQL** por su escalabilidad, soporte de JSONB, y robustez en entornos empresariales.

## 2. Opciones de Base de Datos

### Opción 1: PostgreSQL (RECOMENDADO)
- **Versión mínima**: 12+
- **Ventajas**:
  - Escalabilidad horizontal
  - JSONB para datos flexibles
  - Full Text Search nativo
  - Excelente para producción SaaS
  - Soporte JSONB para futuras extensiones
- **Conexión en producción**:
  ```
  postgresql://user:password@host:5432/dojoflow
  ```

### Opción 2: MySQL/MariaDB
- **Versión mínima**: 5.7 (MySQL) / 10.3 (MariaDB)
- **Ventajas**:
  - Familiar para muchos equipos
  - Bajo overhead
- **Desventajas**:
  - Limitaciones en JSONB
  - Menos escalable que PostgreSQL
- **Conexión en producción**:
  ```
  mysql+pymysql://user:password@host:3306/dojoflow?charset=utf8mb4
  ```

## 3. Esquema de Base de Datos

### Tablas Principales

#### 1. **users**
Cuentas de propietarios de dojos y admin.
```sql
- id (PK)
- email (UNIQUE, INDEX)
- full_name
- hashed_password
- is_active
- created_at
- updated_at
```

#### 2. **plans**
Planes SaaS disponibles.
```sql
- id (PK)
- name (Blanco, Negro, Maestro)
- monthly_price
- description
- transaction_fee_percent
```

#### 3. **orders**
Pedidos de compra de planes (NUEVA TABLA CRÍTICA).
```sql
- id (PK)
- plan_id (FK -> plans)
- dojo_name
- owner_name
- owner_email (UNIQUE, INDEX) -- Email del dueño que compra
- owner_phone
- city
- timezone
- currency
- amount (precio del plan)
- status (pending, paid, completed, cancelled) -- INDEX
- payment_method (stripe, mercadopago, etc)
- transaction_id (para rastrear pago)
- paid_at (timestamp del pago)
- generated_email (email temporal generado tras pago)
- generated_password (contraseña temporal)
- credentials_sent_at
- created_at
- updated_at
```

#### 4. **academy_profiles**
Perfil del dojo (uno por usuario owner).
```sql
- id (PK)
- user_id (FK -> users, UNIQUE)
- dojo_name
- owner_name
- contact_email
- contact_phone
- city
- timezone
- currency (MXN, USD, etc)
- created_at
- updated_at
```

#### 5. **students**
Estudiantes del dojo.
```sql
- id (PK)
- academy_id (FK -> academy_profiles)
- name
- email
- phone
- belt_level
- status (active, inactive, suspended)
- created_at
- updated_at
```

#### 6. **attendance**
Registro de asistencias por clase.
```sql
- id (PK)
- student_id (FK -> students)
- class_type (BJJ, Karate, MMA, TKD)
- attendance_date
- status (present, absent, excused)
- created_at
```

#### 7. **payments**
Pagos de estudiantes (no de planes).
```sql
- id (PK)
- student_id (FK -> students)
- amount
- status (paid, pending, cancelled)
- method (card, cash, bank_transfer)
- payment_date
- created_at
```

#### 8. **schedules**
Horarios de clases.
```sql
- id (PK)
- academy_id (FK -> academy_profiles)
- class_type
- day_of_week (0=Lunes, 6=Domingo)
- start_time
- end_time
- teacher_id (FK -> teachers)
- max_students
- active
- created_at
- updated_at
```

#### 9. **teachers**
Instructores del dojo.
```sql
- id (PK)
- academy_id (FK -> academy_profiles)
- name
- email
- phone
- specialties (BJJ, Karate, MMA, TKD)
- hourly_rate
- active
- created_at
- updated_at
```

#### 10. **belt_progress**
Seguimiento de cinturones/grados.
```sql
- id (PK)
- student_id (FK -> students)
- belt_level
- exam_date
- grade (A, B, C)
- notes
- created_at
- updated_at
```

#### 11. **coupons**
Códigos de descuento.
```sql
- id (PK)
- code (UNIQUE, INDEX)
- discount_percent
- max_uses
- used_count
- valid_until
- active
- description
- created_at
- updated_at
```

#### 12. **marketplace_items**
Productos para venta (uniformes, protecciones).
```sql
- id (PK)
- name
- category
- price
- stock
- active
- created_at
- updated_at
```

## 4. Índices Críticos para Despliegue

Para optimizar queries en producción, crear estos índices:

```sql
-- PostgreSQL
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_owner_email ON orders(owner_email);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_students_academy ON students(academy_id);
CREATE INDEX idx_attendance_student ON attendance(student_id);
CREATE INDEX idx_payments_student ON payments(student_id);
CREATE INDEX idx_schedules_academy ON schedules(academy_id);
CREATE INDEX idx_teachers_academy ON teachers(academy_id);
CREATE INDEX idx_belt_progress_student ON belt_progress(student_id);
CREATE INDEX idx_coupons_code ON coupons(code);
CREATE INDEX idx_marketplace_active ON marketplace_items(active);
```

## 5. Migración y Despliegue

### A. Preparación del Entorno Producción

#### PostgreSQL (AWS RDS ejemplo)
```bash
# Instalar cliente psql
apt-get install postgresql-client

# Conectar a BD remota
psql -h <host> -U <user> -d dojoflow

# Crear BD desde terminal
createdb -h <host> -U <user> dojoflow
```

#### Variables de entorno (.env producción)
```
DATABASE_URL=postgresql://user:password@prod-db-host:5432/dojoflow
MYSQL_HOST=prod-db-host
MYSQL_PORT=5432
MYSQL_USER=dojoflow_user
MYSQL_PASSWORD=<strong_password>
MYSQL_DB=dojoflow

SECRET_KEY=<random_secret_key_production>
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://app.dojoflow.com,https://dojoflow.com
```

### B. Initialización de Base de Datos

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar script de inicialización
python -m app.init_db

# Esto crea todas las tablas y seed data:
# - Plan Blanco ($0)
# - Plan Negro ($520 MXN)
# - Plan Maestro ($870 MXN)
# - Usuario admin: owner@dojoflow.com / admin123
# - Instructores de ejemplo
# - Horarios de ejemplo
# - Cupones de ejemplo
```

### C. Despliegue en AWS/Cloud

```bash
# Opción 1: AWS RDS + Elastic Beanstalk
eb create dojoflow-prod --instance-type t3.medium --envvars DATABASE_URL=...

# Opción 2: Docker + ECS
docker build -t dojoflow-api:latest .
docker push <ecr-registry>/dojoflow-api:latest

# Opción 3: Heroku
heroku create dojoflow-prod
heroku config:set DATABASE_URL=postgresql://...
git push heroku main
```

## 6. Performance y Consideraciones

### Sharding (Futuro)
Si creces a 10,000+ dojos, considerar sharding por `academy_id`:
- Tabla: `academy_profiles` (shard key)
- Beneficio: Paralelizar queries por dojo

### Replicación
Para producción:
- Master: Write operations (orders, payments, etc)
- Read Replicas: Queries de reportes y dashboards

### Backups
```bash
# PostgreSQL
pg_dump -h host -U user -d dojoflow > backup_$(date +%Y%m%d).sql

# MySQL
mysqldump -h host -u user -p dojoflow > backup_$(date +%Y%m%d).sql
```

## 7. Monitoreo y Alertas

### Queries a Monitorear
```sql
-- Órdenes pendientes de pago
SELECT * FROM orders WHERE status = 'pending' AND created_at < NOW() - INTERVAL '24 hours';

-- Estudiantes con morosidad
SELECT s.* FROM students s
JOIN payments p ON s.id = p.student_id
WHERE p.status = 'pending' AND p.payment_date < NOW() - INTERVAL '30 days';

-- Uso de slots en clases
SELECT s.class_type, COUNT(*) as enrolled, s.max_students
FROM schedules s
JOIN attendance a ON s.id = a.schedule_id
GROUP BY s.id;
```

## 8. Estructura de Archivos de Aplicación

```
Dojo-Flow-API/
├── app/
│   ├── models/           (SQLAlchemy ORM)
│   │   ├── user.py
│   │   ├── order.py
│   │   ├── plan.py
│   │   ├── academy_profile.py
│   │   ├── student.py
│   │   ├── attendance.py
│   │   ├── payment.py
│   │   ├── schedule.py
│   │   ├── teacher.py
│   │   ├── belt_progress.py
│   │   ├── coupon.py
│   │   └── marketplace_item.py
│   ├── schemas/          (Pydantic validators)
│   ├── api/routes/       (Endpoints)
│   ├── db/
│   │   ├── session.py    (Motor de BD)
│   │   └── base.py       (Declarative models)
│   ├── core/
│   │   ├── config.py     (Variables de entorno)
│   │   └── security.py   (Hashing, JWT)
│   └── init_db.py        (Script de seed)
├── requirements.txt
└── README.md
```

## 9. Checklist de Despliegue

- [ ] Base de datos PostgreSQL creada en producción
- [ ] Credenciales almacenadas en secrets manager (AWS Secrets, HashiCorp Vault)
- [ ] Variables de entorno configuradas (DATABASE_URL, SECRET_KEY, CORS_ORIGINS)
- [ ] Script `init_db.py` ejecutado para crear tablas
- [ ] Backup automatizado configurado (diario)
- [ ] HTTPS/SSL certificado instalado
- [ ] Monitoreo de errores activado (Sentry, DataDog)
- [ ] Rate limiting configurado en endpoints públicos (/orders, /checkout)
- [ ] Pruebas de carga completadas (wrk, Apache JMeter)
- [ ] Plan de disaster recovery documentado
- [ ] Logs centralizados (CloudWatch, ELK Stack)

## 10. URLs de Conexión Ejemplo

### Desarrollo Local
```
DATABASE_URL=postgresql://localhost/dojoflow  # Linux/Mac
DATABASE_URL=postgresql://user:password@localhost:5432/dojoflow  # Windows
```

### Staging
```
DATABASE_URL=postgresql://user:password@dojoflow-staging.rds.amazonaws.com:5432/dojoflow_staging
```

### Producción
```
DATABASE_URL=postgresql://user:secure_password@dojoflow-prod-cluster.rds.amazonaws.com:5432/dojoflow_prod
```

---

**Última actualización**: Marzo 22, 2026  
**Responsable**: DevOps / Infrastructure Team  
**Siguiente revisión**: Cuando el número de dojos > 1000
