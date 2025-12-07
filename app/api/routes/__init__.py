from fastapi import FastAPI
from app.api.routes import (
    health,
    users,
    auth,
    companies,
    company_invitations,
    company_requests,
    company_members,
    quizzes,
    exports,
    analytics,
    notifications
)


def include_routers(app: FastAPI) -> None:
    """Include all API routers"""
    app.include_router(health.router, tags=["health"])
    app.include_router(users.router, tags=["users"])
    app.include_router(auth.router, tags=["auth"])
    app.include_router(companies.router)
    app.include_router(company_invitations.router)
    app.include_router(company_requests.router)
    app.include_router(company_members.router)
    app.include_router(quizzes.router)
    app.include_router(exports.router)
    app.include_router(analytics.router)
    app.include_router(notifications.router)
