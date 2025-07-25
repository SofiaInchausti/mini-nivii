from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import response_controller
from app.models.database import engine
from app.models.response_model import Base  # Asegúrate de importar el Base correcto

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ["http://localhost:3000"] si usas React en ese puerto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Crea todas las tablas definidas en los modelos importados
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


# Incluye tus routers
app.include_router(response_controller.router)
