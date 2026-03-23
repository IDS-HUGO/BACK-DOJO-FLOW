from fastapi import APIRouter

from app.api.routes import (
	academy_profile,
	admin_dashboard,
	attendance,
	auth,
	belts,
	coupons,
	dashboard,
	dojo_management,
	marketplace,
	orders,
	payments,
	plans,
	reports,
	schedules,
	students,
	teachers,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(students.router)
api_router.include_router(attendance.router)
api_router.include_router(payments.router)
api_router.include_router(orders.router)
api_router.include_router(belts.router)
api_router.include_router(plans.router)
api_router.include_router(dashboard.router)
api_router.include_router(marketplace.router)
api_router.include_router(academy_profile.router)
api_router.include_router(admin_dashboard.router)
api_router.include_router(dojo_management.router)
api_router.include_router(reports.router)
api_router.include_router(schedules.router)
api_router.include_router(coupons.router)
api_router.include_router(teachers.router)
api_router.include_router(schedules.router)
api_router.include_router(coupons.router)
api_router.include_router(reports.router)
