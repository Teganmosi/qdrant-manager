from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .db import Base, engine
from .routes import auth, collections, points, search, users

app = FastAPI(title=settings.APP_NAME)

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(collections.router)
app.include_router(points.router)
app.include_router(search.router)
app.include_router(users.router)

@app.on_event("startup")
def startup():
    # Create DB tables on startup
    try:
        Base.metadata.create_all(bind=engine)
        print("DB tables ensured")
    except Exception as e:
        print("Warning: could not create DB tables at startup:", e)

@app.get("/health")
def health():
    return {"status": "healthy"}