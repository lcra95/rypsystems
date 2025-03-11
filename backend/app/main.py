from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth_router, user_router

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_application() -> FastAPI:
    app = FastAPI(
        title="RYP Systems API",
        version="1.0.0"
    )

    # Incluir routers
    app.include_router(auth_router.router)
    app.include_router(user_router.router)
    
    return app

create_tables()
app = get_application()
