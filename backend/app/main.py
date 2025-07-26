from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import response_controller
from app.models.database import engine, Base
from app.models.response_model import Response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ["http://localhost:3000"] si usas React en ese puerto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create all tables defined in the imported models
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# Include routers
app.include_router(response_controller.router)
