from fastapi import FastAPI
from main.routes import core_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://steprobotics.ru/'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core_router)