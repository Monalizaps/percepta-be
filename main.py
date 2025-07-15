from fastapi import FastAPI
from routes.hbos_route import router as hbos_router
from routes.simulate import router as simulate_router
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Percepta - Anomaly Detection API")

origins = [
    "http://localhost:3000",
    "http://localhost:8080",  # URL do seu frontend React em dev
    # adicione outras URLs se precisar
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # permite todos os métodos (GET, POST, OPTIONS...)
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok"}

# Novo endpoint /detect com pipeline real
app.include_router(hbos_router)
app.include_router(simulate_router)
