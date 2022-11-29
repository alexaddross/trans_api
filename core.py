from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from main.routes import core_router
from utilities.routes import utility_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://steprobotics.ru/'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core_router)
app.include_router(utility_router)
