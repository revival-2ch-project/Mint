from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from ...services.board import BoardService
from ...services.thread import ThreadService

router = APIRouter()


@router.get(
    "/{boardName:str}/subject.txt",
    response_class=PlainTextResponse,
)
async def subjectTXT(boardName: str):
    """
    Monazilla 1.0の形式のスレッド一覧
    """
    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    threads = await ThreadService.getThreads(board.id)
    subject = []
    for thread in threads:
        subject.append(f"{thread.id}.dat<>{thread.title} ({thread.count})")
    return PlainTextResponse(
        "\n".join(subject).encode("shift_jis"),
        200,
        headers={"content-type": "text/plain; charset=shift_jis"},
    )
