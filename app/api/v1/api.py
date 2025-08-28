from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, catalog, questions, quizzes, attempts, ai, payments, community

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(catalog.router, prefix="/catalog", tags=["Catalog"])
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["Quizzes"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["Attempts"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Services"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(community.router, prefix="/community", tags=["Community"])
