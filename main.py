from fastapi import FastAPI
from routes.hbos_route import router as hbos_router
from routes.simulate import router as simulate_router


app = FastAPI(title="Percepta - Anomaly Detection API")

@app.get("/")
def health_check():
    return {"status": "ok"}

# Novo endpoint /detect com pipeline real
app.include_router(hbos_router)
app.include_router(simulate_router)
