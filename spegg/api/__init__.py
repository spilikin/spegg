__version__='0.23.0'
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import api

app = FastAPI(
    title="Spegg", 
    version=__version__, 
    openapi_url="/api/v1/openapi.json", 
    docs_url=None,
    redoc_url='/api/docs'
    )

origins = [
    "https://spilikin.grafana.net",
    "https://spegg.spilikin.dev/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api, prefix="/api/v1")



def serve():
    uvicorn.run("spegg.api:app", reload=True, workers=2)