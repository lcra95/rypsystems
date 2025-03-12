from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import user_router, auth_router, company_router, number_router, webhook_router, sse_router

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_application() -> FastAPI:
    app = FastAPI(
        title="RYP Systems API",
        version="1.0.0"
    )

    # 🔥 Configurar CORS para permitir solicitudes del frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5500"],  # Cambia esto por el dominio de tu frontend
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Incluir routers
    app.include_router(auth_router.router)
    app.include_router(user_router.router)
    app.include_router(company_router.router)
    app.include_router(number_router.router)
    app.include_router(webhook_router.router)
    app.include_router(sse_router.router)

    return app

create_tables()
app = get_application()
