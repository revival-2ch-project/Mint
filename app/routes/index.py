from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..services.meta import MetaDataService

router = APIRouter()
templates = Jinja2Templates(directory="pages")


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"metadata": MetaDataService.metadata},
    )
