from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

with open("./pages/index.html") as f:
    binary = f.read()

@router.get("/", response_class=HTMLResponse)
def index():
    return binary
