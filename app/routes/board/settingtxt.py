from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from ...services.board import BoardService

router = APIRouter()


@router.get(
    "/{boardName:str}/SETTING.TXT",
    response_class=PlainTextResponse,
)
async def settingTXT(boardName: str):
    """
    Monazilla 1.0の形式の板設定。
    """
    board = await BoardService.getBoard(boardName)
    if not board:
        raise HTTPException(status_code=404)
    setting = f"""
BBS_TITLE={board.name}
BBS_TITLE_PICTURE=
BBS_TITLE_COLOR=#000000
BBS_TITLE_LINK=
BBS_BG_PICTURE=
BBS_BG_COLOR=#FFFFFF
BBS_MENU_COLOR=#CCFFCC
BBS_MAKETHREAD_COLOR=#CCFFCC
BBS_THREAD_COLOR=#EFEFEF
BBS_TEXT_COLOR=#000000
BBS_SUBJECT_COLOR=#FF0000
BBS_NAME_COLOR=green
BBS_LINK_COLOR=#0000FF
BBS_ALINK_COLOR=#FF0000
BBS_VLINK_COLOR=#660099
BBS_MENU_NUMBER=8
BBS_THREAD_NUMBER=5
BBS_CONTENTS_NUMBER=3
BBS_LINE_NUMBER=6
BBS_NONAME_NAME={board.anonymous_name}
BBS_NANASHI_CHECK=
BBS_SUBJECT_COUNT={board.subject_count}
BBS_NAME_COUNT={board.name_count}
BBS_MAIL_COUNT=128
BBS_MESSAGE_COUNT={board.message_count}
BBS_NAME_COOKIE=checked
BBS_MAIL_COOKIE=checked
BBS_FORCE_ID=checked
"""
    return PlainTextResponse(
        setting.encode("shift_jis"),
        200,
        headers={"content-type": "text/plain; charset=shift_jis"},
    )
