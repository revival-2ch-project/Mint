from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .captchaType import CaptchaType


class ChangeableMetaData(BaseModel):
    id: int
    name: Optional[str] = None
    captcha_type: Optional[CaptchaType] = None
    captcha_sitekey: Optional[str] = None
    captcha_secret: Optional[str] = None


class MetaData(BaseModel):
    id: int
    created_at: datetime
    name: str
    captcha_type: CaptchaType
    captcha_sitekey: Optional[str] = None
    captcha_secret: Optional[str] = None
