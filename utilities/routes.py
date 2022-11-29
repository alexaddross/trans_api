from fastapi import Request
from fastapi import APIRouter
from fastapi.responses import JSONResponse

utility_router = APIRouter()

@utility_router.get('/is_alive')
async def is_alive():
    return JSONResponse({'ok': 'alive'})
