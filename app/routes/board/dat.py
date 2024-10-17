from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from ...services.board import BoardService
from ...services.thread import ThreadService
from ...services.response import ResponseService

router = APIRouter()

weekdays = ["月", "火", "水", "木", "金", "土", "日"]


@router.get(
    "/{boardName:str}/dat/{threadId:int}",
    response_class=PlainTextResponse,
)
async def dat(boardName: str, threadId: int):
    """
    Monazilla 1.0の形式のスレッドデータ
    """
    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    thread = await ThreadService.getThread(board.id, threadId)
    if not thread:
        raise HTTPException(status_code=404)
    threadDat = []
    threadDat.append(
        f"{thread.name}<><>{thread.created_at.strftime('%Y/%m/%d')}({weekdays[thread.created_at.weekday()]}) {thread.created_at.strftime('%H/%M/%S')}.{thread.created_at.strftime('%f')[0:1]} ID:{thread.account_id}<> {thread.content} <>{thread.title}"
    )
    responses = await ResponseService.getResponses(board.id, threadId)
    for response in responses:
        threadDat.append(
            f"{response.name}<><>{response.created_at.strftime('%Y/%m/%d')}({weekdays[response.created_at.weekday()]}) {response.created_at.strftime('%H/%M/%S')}.{response.created_at.strftime('%f')[0:1]} ID:{response.account_id}<> {response.content} <>{response.title}"
        )
    return PlainTextResponse(
        "\n".join(threadDat).encode("shift_jis"),
        200,
        headers={"content-type": "text/plain; charset=shift_jis"},
    )
