__version__='0.11.0'
import uvicorn
from fastapi import FastAPI
from .api import api

app = FastAPI(
    title="Spegg", 
    version=__version__, 
    openapi_url="/api/v1/openapi.json", 
    docs_url=None,
    redoc_url='/api/docs'
    )
app.include_router(api, prefix="/api/v1")

def serve():
    uvicorn.run("spegg.api:app", reload=True, workers=2)