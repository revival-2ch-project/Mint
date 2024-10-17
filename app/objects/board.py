from pydantic import BaseModel


class Board(BaseModel):
    id: str
    name: str
    anonymous_name: str = "名無しさん"
    deleted_name: str = "あぼーん"
    subject_count: int = 64
    name_count: int = 50
    message_count: int = 2000
    head: str = (
        '<div style="text-align: center; margin: 1.2em 0">\n    <span style="color: red">クリックで救える命が…ないです(｀･ω･´)ｼｬｷｰﾝ</font>\n</div>\n\n<b>掲示板使用上の注意</b>\n<ul style="font-weight:bold;">\n    <li>･転んでも泣かない</li>\n    <li>･出されたものは残さず食べる</li>\n    <li>･Python使いを尊重する</li>\n</ul>'
    )
