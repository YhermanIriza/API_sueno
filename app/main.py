from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Backend API",
    description="API backend modular y profesional",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {"message": "API funcionando correctamente 🚀"}
